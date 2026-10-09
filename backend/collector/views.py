"""
Waste Collector Views: Proximity pool dispatch, Atomic Acceptance, Atomic Release,
Atomic Completion with weighment/settlement, and Live Telemetry publishing.
"""

import math
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView

from common.permissions import IsCollectorRole
from common.utils import api_success, api_failure
from common.constants import MESSAGES, ERROR_CODES, PICKUP_STATUS
from pickups.models import PickupRequest

class AvailablePickupsView(APIView):
    permission_classes = [IsCollectorRole]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)
        longitude = request.query_params.get('longitude')
        latitude = request.query_params.get('latitude')
        radius = float(request.query_params.get('radius', 25))

        queryset = PickupRequest.objects.filter(status=PICKUP_STATUS.PENDING).select_related('user').order_by('-created_at')

        # Geographic proximity dispatch (Caveat #9)
        if longitude is not None and latitude is not None:
            try:
                c_lon = float(longitude)
                c_lat = float(latitude)
                candidates = []
                for p in queryset:
                    if p.latitude is not None and p.longitude is not None:
                        # Haversine distance
                        d_lat = math.radians(p.latitude - c_lat)
                        d_lon = math.radians(p.longitude - c_lon)
                        a = (
                            math.sin(d_lat / 2) ** 2
                            + math.cos(math.radians(c_lat)) * math.cos(math.radians(p.latitude)) * math.sin(d_lon / 2) ** 2
                        )
                        dist_km = 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                        if dist_km <= radius:
                            candidates.append(p)
                    else:
                        candidates.append(p)
                queryset = candidates
            except (ValueError, TypeError):
                pass

        total = len(queryset) if isinstance(queryset, list) else queryset.count()
        start = (page - 1) * limit
        end = start + limit
        p_list = queryset[start:end]

        docs = [p.to_dict() for p in p_list]
        pages = math.ceil(total / limit) if limit > 0 else 1

        return api_success(
            data={'pickups': docs},
            meta={'total': total, 'page': page, 'limit': limit, 'pages': pages},
            message=MESSAGES.PICKUPS_FETCHED,
        )

class CollectorPickupsView(APIView):
    permission_classes = [IsCollectorRole]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)

        queryset = PickupRequest.objects.filter(waste_collector=request.user).select_related('user').order_by('-created_at')
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        pickups = queryset[start:end]

        docs = [p.to_dict() for p in pickups]
        pages = math.ceil(total / limit) if limit > 0 else 1

        return api_success(
            data={'pickups': docs},
            meta={'total': total, 'page': page, 'limit': limit, 'pages': pages},
            message=MESSAGES.PICKUPS_FETCHED,
        )

class AcceptPickupView(APIView):
    permission_classes = [IsCollectorRole]

    def post(self, request, id):
        collector = request.user

        # Atomic conditional update (Caveats #8 + #9: prevents double claiming races)
        with transaction.atomic():
            pickup = PickupRequest.objects.select_for_update().filter(
                id=id, status=PICKUP_STATUS.PENDING
            ).first()

            if not pickup:
                return api_failure(
                    message=ERROR_CODES.PICKUP_ALREADY_ACCEPTED['message'],
                    status_code=409,
                )

            pickup.status = PICKUP_STATUS.ACCEPTED
            pickup.waste_collector = collector
            history = pickup.status_history or []
            history.append({
                'status': PICKUP_STATUS.ACCEPTED,
                'actorId': str(collector.id),
                'timestamp': timezone.now().isoformat(),
            })
            pickup.status_history = history
            pickup.save()

        return api_success(data={'pickup': pickup.to_dict()}, message=MESSAGES.PICKUP_ACCEPTED)

class ReleasePickupView(APIView):
    permission_classes = [IsCollectorRole]

    def post(self, request, id):
        collector = request.user

        # Atomic release conditional update
        with transaction.atomic():
            pickup = PickupRequest.objects.select_for_update().filter(
                id=id, status=PICKUP_STATUS.ACCEPTED, waste_collector=collector
            ).first()

            if not pickup:
                return api_failure(
                    message=ERROR_CODES.PICKUP_INVALID_TRANSITION['message'],
                    status_code=409,
                )

            pickup.status = PICKUP_STATUS.PENDING
            pickup.waste_collector = None
            history = pickup.status_history or []
            history.append({
                'status': PICKUP_STATUS.PENDING,
                'actorId': str(collector.id),
                'note': 'Released by collector',
                'timestamp': timezone.now().isoformat(),
            })
            pickup.status_history = history
            pickup.save()

        return api_success(data={'pickup': pickup.to_dict()}, message=MESSAGES.PICKUP_CANCELLED)

class CompletePickupView(APIView):
    permission_classes = [IsCollectorRole]

    def post(self, request, id):
        collector = request.user
        data = request.data or {}

        with transaction.atomic():
            pickup = PickupRequest.objects.select_for_update().filter(
                id=id, status=PICKUP_STATUS.ACCEPTED, waste_collector=collector
            ).first()

            if not pickup:
                return api_failure(
                    message=ERROR_CODES.PICKUP_INVALID_TRANSITION['message'],
                    status_code=409,
                )

            # Weighment and settlement (Caveats #7 + #11)
            final_weight = data.get('finalWeight') if data.get('finalWeight') is not None else data.get('actualWeight')
            settled_amount = data.get('settledAmount') if data.get('settledAmount') is not None else data.get('paidAmount')
            adjustment_reason = data.get('adjustmentReason', '')
            evidence_urls = data.get('evidenceUrls', [])
            collector_notes = data.get('collectorNotes', '')

            if collector_notes:
                pickup.collector_notes = collector_notes

            if final_weight is not None or settled_amount is not None or adjustment_reason or evidence_urls:
                pickup.settlement = {
                    'finalWeight': float(final_weight) if final_weight is not None else None,
                    'settledAmount': float(settled_amount) if settled_amount is not None else None,
                    'adjustmentReason': adjustment_reason,
                    'evidenceUrls': evidence_urls if isinstance(evidence_urls, list) else [],
                    'settledAt': timezone.now().isoformat(),
                    'settledBy': str(collector.id),
                }

            pickup.status = PICKUP_STATUS.COMPLETED
            history = pickup.status_history or []
            history.append({
                'status': PICKUP_STATUS.COMPLETED,
                'actorId': str(collector.id),
                'note': collector_notes or 'Completed by collector',
                'timestamp': timezone.now().isoformat(),
            })
            pickup.status_history = history
            pickup.save()

        return api_success(data={'pickup': pickup.to_dict()}, message=MESSAGES.PICKUP_COMPLETED)

class PushCollectorLocationView(APIView):
    permission_classes = [IsCollectorRole]

    def post(self, request, id):
        collector = request.user
        data = request.data

        pickup = PickupRequest.objects.filter(
            id=id, status=PICKUP_STATUS.ACCEPTED, waste_collector=collector
        ).first()

        if not pickup:
            return api_failure(message=ERROR_CODES.TRACKING_NOT_ALLOWED['message'], status_code=403)

        lon = data.get('longitude')
        lat = data.get('latitude')
        heading = data.get('heading', 0)
        speed = data.get('speed', 0)

        if lon is None or lat is None:
            return api_failure(message='Valid longitude and latitude are required', status_code=400)

        tracking = {
            'coordinates': [float(lon), float(lat)],
            'heading': float(heading) if heading else 0,
            'speed': float(speed) if speed else 0,
            'updatedAt': timezone.now().isoformat(),
        }
        pickup.live_tracking = tracking
        pickup.save(update_fields=['live_tracking'])

        return api_success(data={'tracking': tracking}, message='Location updated successfully')
