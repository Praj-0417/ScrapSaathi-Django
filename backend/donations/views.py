"""
Donations Views: Record Donation with provisional certificate, list personal donations, and admin auditing.
"""

import time
import random
import math
from rest_framework.views import APIView
from common.permissions import IsAuthenticatedCustom, IsAdminRole
from common.utils import api_success, api_failure
from common.constants import MESSAGES
from donations.models import Donation

class DonationCreateView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def post(self, request):
        user = request.user
        data = request.data

        amount = float(data.get('amount', 0))
        if amount < 10:
            return api_failure(message='Donation amount must be at least ₹10', status_code=400)

        provisional_ack_id = data.get('certificateId') or f'ACK-ECO-{hex(int(time.time()))[2:].upper()}-{random.randint(1000, 9999)}'
        tx_id = data.get('transactionId', '').strip()

        donation = Donation.objects.create(
            user=user,
            amount=amount,
            cause=data.get('cause', 'general'),
            donor_name=data.get('donorName', user.name),
            pan_number=data.get('panNumber', '').upper(),
            transaction_id=tx_id,
            payment_method=data.get('paymentMethod', 'upi_qr'),
            payment_status='completed' if tx_id else 'pending',
            verification_status='unverified',
            receipt_type='provisional_acknowledgement',
            certificate_id=provisional_ack_id,
            message=data.get('message', ''),
        )

        return api_success(
            data={'donation': donation.to_dict()},
            message=MESSAGES.DONATION_CREATED,
            status_code=201,
        )

class MyDonationsView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)

        queryset = Donation.objects.filter(user=request.user).order_by('-created_at')
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        donations = queryset[start:end]

        docs = [d.to_dict() for d in donations]
        pages = math.ceil(total / limit) if limit > 0 else 1

        return api_success(
            data={'donations': docs},
            meta={'total': total, 'page': page, 'limit': limit, 'pages': pages},
            message=MESSAGES.DONATIONS_FETCHED,
        )

class AdminDonationListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)

        queryset = Donation.objects.all().select_related('user').order_by('-created_at')
        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        donations = queryset[start:end]

        docs = [d.to_dict() for d in donations]
        pages = math.ceil(total / limit) if limit > 0 else 1

        return api_success(
            data={'donations': docs},
            meta={'total': total, 'page': page, 'limit': limit, 'pages': pages},
            message=MESSAGES.DONATIONS_FETCHED,
        )
