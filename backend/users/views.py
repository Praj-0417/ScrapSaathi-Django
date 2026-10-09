"""
User Profile and Admin User Views.
"""

import math
from rest_framework.views import APIView
from common.permissions import IsAuthenticatedCustom, IsAdminRole
from common.utils import api_success, api_failure
from common.constants import MESSAGES
from users.models import User, IndividualProfile, WasteCollectorProfile, RecycleCompanyProfile, BigOrganizationProfile

class UserMeView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def get(self, request):
        return api_success(
            data={'user': request.user.to_dict()},
            message=MESSAGES.USER_FETCHED,
        )

    def patch(self, request):
        user = request.user
        data = request.data

        if 'name' in data and data['name']:
            user.name = data['name'].strip()
        if 'phone' in data:
            user.phone = data['phone'].strip()
        if 'avatar' in data:
            user.avatar = data['avatar'].strip()

        user.save()
        return api_success(
            data={'user': user.to_dict()},
            message=MESSAGES.PROFILE_UPDATED,
        )

class UserProfileView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def patch(self, request):
        user = request.user
        data = request.data
        user_type = user.user_type

        profile = None
        if user_type == 'individual':
            profile, _ = IndividualProfile.objects.get_or_create(user=user)
            if 'address' in data:
                profile.address = data['address']
            if 'profilePhoto' in data:
                profile.profile_photo = data['profilePhoto']
            profile.save()

        elif user_type == 'waste-collector':
            profile, _ = WasteCollectorProfile.objects.get_or_create(user=user)
            if 'address' in data:
                profile.address = data['address']
            if 'profilePhoto' in data:
                profile.profile_photo = data['profilePhoto']
            if 'companyName' in data:
                profile.company_name = data['companyName']
            if 'businessLicenseNo' in data:
                profile.business_license_no = data['businessLicenseNo']
            profile.save()

        elif user_type == 'recycle-company':
            profile, _ = RecycleCompanyProfile.objects.get_or_create(user=user)
            if 'address' in data:
                profile.address = data['address']
            if 'companyName' in data:
                profile.company_name = data['companyName']
            if 'businessLicenseNo' in data:
                profile.business_license_no = data['businessLicenseNo']
            if 'wasteType' in data:
                profile.waste_type = data['wasteType']
            if 'recyclingCapabilities' in data:
                profile.recycling_capabilities = data['recyclingCapabilities']
            profile.save()

        elif user_type == 'big-organization':
            profile, _ = BigOrganizationProfile.objects.get_or_create(user=user)
            if 'address' in data:
                profile.address = data['address']
            if 'companyName' in data:
                profile.company_name = data['companyName']
            if 'businessLicenseNo' in data:
                profile.business_license_no = data['businessLicenseNo']
            profile.save()

        if not profile:
            return api_failure(message='Profile not found', status_code=404)

        return api_success(
            data={'profile': profile.to_dict()},
            message=MESSAGES.PROFILE_UPDATED,
        )

class AdminUserListView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 10)), 100)
        search = request.query_params.get('search', '').strip()

        queryset = User.objects.all().order_by('-created_at')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(Q(name__icontains=search) | Q(email__icontains=search))

        total = queryset.count()
        start = (page - 1) * limit
        end = start + limit
        users = queryset[start:end]

        docs = [u.to_dict() for u in users]
        pages = math.ceil(total / limit) if limit > 0 else 1

        return api_success(
            data={'users': docs},
            meta={'total': total, 'page': page, 'limit': limit, 'pages': pages},
            message=MESSAGES.USERS_FETCHED,
        )
