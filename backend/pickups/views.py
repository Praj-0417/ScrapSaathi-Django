"""
Pickup Request Controllers: Booking, Listing, Cancellation, Live Tracking, Admin Audit.
Preserves exact behaviors from pickupController.js and pickupService.js.
"""

import json
import math
from datetime import datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from common.permissions import IsAuthenticatedCustom, IsAdminRole
from common.utils import api_success, api_failure, check_serviceability
from common.constants import MESSAGES, ERROR_CODES, PICKUP_STATUS
from pickups.models import PickupRequest
from rates.models import ScrapItem

class PickupListCreateView(APIView):
    permission_classes = [IsAuthenticatedCustom]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user = request.user
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)

        queryset = PickupRequest.objects.filter(user=user).select_related('user', 'waste_collector').order_by('-created_at')
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

    def post(self, request):
        user = request.user
        data = request.data

        address = data.get('address', '').strip()
        preferred_time_slot = data.get('preferredTimeSlot', '').strip()
        customer_notes = data.get('customerNotes', '').strip()
        scheduled_date_raw = data.get('scheduledDate')
        city = data.get('city', 'delhi-ncr').lower().strip()

        if not address or not preferred_time_slot:
            return api_failure(message='Address and preferredTimeSlot are required', status_code=400)

        # Latitude & Longitude
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        lat_float = None
        lon_float = None

        if latitude is not None and longitude is not None:
            try:
                lat_float = float(latitude)
                lon_float = float(longitude)
                service_check = check_serviceability(lat_float, lon_float)
                if not service_check.get('serviceable'):
                    return api_failure(
                        message=ERROR_CODES.LOCATION_NOT_SERVICEABLE['message'],
                        status_code=400,
                    )
                if service_check.get('hubId'):
                    city = service_check['hubId']
            except (ValueError, TypeError):
                pass

        # Normalize wasteDetails
        raw_waste_details = data.get('wasteDetails')
        waste_details = []
        if isinstance(raw_waste_details, str):
            try:
                waste_details = json.loads(raw_waste_details)
            except Exception:
                waste_details = []
        elif isinstance(raw_waste_details, list):
            waste_details = raw_waste_details

        if not waste_details:
            waste_type = data.get('wasteType')
            quantity = data.get('quantity')
            unit = data.get('unit', 'kg')
            subcategory = data.get('subcategory')
            if waste_type and quantity:
                try:
                    waste_details = [{
                        'wasteType': waste_type,
                        'subcategory': subcategory,
                        'quantity': float(quantity),
                        'unit': unit,
                    }]
                except (ValueError, TypeError):
                    waste_details = []

        if not waste_details or not waste_details[0].get('wasteType') or not waste_details[0].get('quantity'):
            return api_failure(message=ERROR_CODES.BAD_REQUEST['message'], status_code=400)

        # Server-authoritative quote calculation (Caveat #6)
        all_items = ScrapItem.objects.filter(active=True)
        rate_map = {}
        for item in all_items:
            key = item.name.lower().strip()
            prices = item.prices or {}
            rate_map[key] = (
                prices.get(city)
                or prices.get('delhi-ncr')
                or (list(prices.values())[0] if prices else 0)
            )

        quote_items = []
        total_estimate = 0.0

        for detail in waste_details:
            w_type = detail.get('wasteType', '').lower().strip()
            unit_rate = rate_map.get(w_type, 0.0)
            qty = float(detail.get('quantity', 0.0))
            line_total = round(unit_rate * qty, 2)
            total_estimate += line_total
            quote_items.append({
                'wasteType': detail.get('wasteType'),
                'subcategory': detail.get('subcategory'),
                'quantity': qty,
                'unit': detail.get('unit', 'kg'),
                'unitRate': unit_rate,
                'lineTotal': line_total,
            })

        quote_snapshot = {
            'items': quote_items,
            'city': city,
            'currency': 'INR',
            'totalEstimate': round(total_estimate, 2),
            'rateSnapshotDate': timezone.now().isoformat(),
        }

        # Handle optional photo upload
        image_url = None
        if 'photo' in request.FILES:
            photo = request.FILES['photo']
            from django.core.files.storage import default_storage
            saved_name = default_storage.save(f'pickups/{photo.name}', photo)
            image_url = f'/media/{saved_name}'

        # Parse scheduled date
        scheduled_date = None
        if scheduled_date_raw:
            try:
                scheduled_date = datetime.fromisoformat(str(scheduled_date_raw).replace('Z', '+00:00'))
            except Exception:
                pass

        pickup = PickupRequest.objects.create(
            user=user,
            waste_details=waste_details,
            quote=quote_snapshot,
            address=address,
            preferred_time_slot=preferred_time_slot,
            customer_notes=customer_notes,
            scheduled_date=scheduled_date,
            image_url=image_url,
            latitude=lat_float,
            longitude=lon_float,
            status=PICKUP_STATUS.PENDING,
            status_history=[{
                'status': PICKUP_STATUS.PENDING,
                'actorId': str(user.id),
                'timestamp': timezone.now().isoformat(),
            }],
        )

        return api_success(
            data={'pickup': pickup.to_dict()},
            message=MESSAGES.PICKUP_CREATED,
            status_code=201,
        )

class MyPickupsListView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        user = request.user
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)

        queryset = PickupRequest.objects.filter(user=user).select_related('user', 'waste_collector').order_by('-created_at')
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

class PickupDetailView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request, id):
        pickup = PickupRequest.objects.filter(id=id).select_related('user', 'waste_collector').first()
        if not pickup:
            return api_failure(message=ERROR_CODES.PICKUP_NOT_FOUND['message'], status_code=404)

        user_id = str(request.user.id)
        is_owner = str(pickup.user_id) == user_id
        is_collector = pickup.waste_collector and str(pickup.waste_collector_id) == user_id
        is_admin = request.user.role == 'admin'

        if not (is_owner or is_collector or is_admin):
            return api_failure(message=ERROR_CODES.FORBIDDEN['message'], status_code=403)

        return api_success(data={'pickup': pickup.to_dict()}, message=MESSAGES.PICKUPS_FETCHED)

class PickupCancelView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def patch(self, request, id):
        pickup = PickupRequest.objects.filter(id=id, user=request.user).first()
        if not pickup:
            return api_failure(message=ERROR_CODES.PICKUP_INVALID_CANCEL['message'], status_code=400)

        if pickup.status not in [PICKUP_STATUS.PENDING, PICKUP_STATUS.ACCEPTED]:
            return api_failure(message=ERROR_CODES.PICKUP_INVALID_CANCEL['message'], status_code=400)

        pickup.status = PICKUP_STATUS.CANCELLED
        history = pickup.status_history or []
        history.append({
            'status': PICKUP_STATUS.CANCELLED,
            'actorId': str(request.user.id),
            'timestamp': timezone.now().isoformat(),
        })
        pickup.status_history = history
        pickup.save()

        return api_success(data={'pickup': pickup.to_dict()}, message=MESSAGES.PICKUP_CANCELLED)

class PickupTrackingView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request, id):
        pickup = PickupRequest.objects.filter(id=id).select_related('user', 'waste_collector').first()
        if not pickup:
            return api_failure(message=ERROR_CODES.NOT_FOUND['message'], status_code=404)

        user_id = str(request.user.id)
        is_owner = str(pickup.user_id) == user_id
        is_collector = pickup.waste_collector and str(pickup.waste_collector_id) == user_id
        is_admin = request.user.role == 'admin'

        if not (is_owner or is_collector or is_admin):
            return api_failure(message=ERROR_CODES.TRACKING_NOT_ALLOWED['message'], status_code=403)

        live = pickup.live_tracking or None
        is_stale = False
        if live and live.get('updatedAt'):
            try:
                up_dt = datetime.fromisoformat(live['updatedAt'].replace('Z', '+00:00'))
                diff_sec = (timezone.now() - up_dt).total_seconds()
                is_stale = diff_sec > 300  # > 5 minutes
            except Exception:
                pass

        collector_dict = None
        if pickup.waste_collector:
            collector_dict = {
                '_id': str(pickup.waste_collector.id),
                'id': str(pickup.waste_collector.id),
                'name': pickup.waste_collector.name,
                'email': pickup.waste_collector.email,
                'phone': pickup.waste_collector.phone,
            }

        destination = None
        if pickup.latitude is not None and pickup.longitude is not None:
            destination = {'type': 'Point', 'coordinates': [pickup.longitude, pickup.latitude]}

        tracking_data = {
            'pickupId': str(pickup.id),
            'status': pickup.status,
            'collector': collector_dict,
            'destination': destination,
            'address': pickup.address,
            'liveTracking': live,
            'isStale': is_stale,
        }

        return api_success(data=tracking_data, message='Tracking details retrieved')

class AdminPickupListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)
        status = request.query_params.get('status')

        queryset = PickupRequest.objects.all().select_related('user', 'waste_collector').order_by('-created_at')
        if status:
            queryset = queryset.filter(status=status)

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
