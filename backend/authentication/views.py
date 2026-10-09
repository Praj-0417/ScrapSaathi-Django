"""
Authentication Controllers: Register, Login, Google OAuth, OTP verification, Password Reset.
Ensures 100% parity with monolith authController.js & authService.js.
"""

import random
import time
import jwt
import bcrypt
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from common.permissions import IsAuthenticatedCustom
from common.utils import api_success, api_failure
from common.constants import MESSAGES, ERROR_CODES, USER_TYPES, ROLES
from users.models import (
    User,
    IndividualProfile,
    WasteCollectorProfile,
    RecycleCompanyProfile,
    BigOrganizationProfile,
)
from authentication.models import OTP

def generate_jwt_token(user):
    """Generates standard access token with user metadata and tokenVersion (Caveat #4)."""
    payload = {
        'userId': str(user.id),
        'email': user.email,
        'userType': user.user_type,
        'role': user.role,
        'name': user.name,
        'version': user.token_version,
        'exp': int(time.time()) + settings.JWT_EXPIRES_IN,
        'iat': int(time.time()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

def sign_verification_token(email):
    """Signs short-lived verification token proving OTP validation for registration (Caveat #2)."""
    payload = {
        'email': email.lower().strip(),
        'purpose': 'registration',
        'exp': int(time.time()) + 900,  # 15 minutes
        'iat': int(time.time()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')

def set_auth_cookie(response, token):
    """Attaches httpOnly authentication cookie to HTTP response."""
    response.set_cookie(
        'token',
        token,
        max_age=settings.JWT_EXPIRES_IN,
        httponly=True,
        samesite='Lax',
        secure=not settings.DEBUG,
    )
    return response

def verify_user_password(raw_password, stored_password):
    """Validates password supporting both Django hashers and migrated bcrypt hashes."""
    if not stored_password:
        return False
    # Try Django check_password
    try:
        if check_password(raw_password, stored_password):
            return True
    except Exception:
        pass
    # Try bcrypt fallback
    try:
        if bcrypt.checkpw(raw_password.encode('utf-8'), stored_password.encode('utf-8')):
            return True
    except Exception:
        pass
    return False

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        name = data.get('name', '').strip()
        email = data.get('email', '').lower().strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        terms_accepted = data.get('termsAccepted', True)
        user_type = data.get('userType', USER_TYPES.INDIVIDUAL)
        verification_token = data.get('verificationToken')

        if not terms_accepted:
            return api_failure(message=ERROR_CODES.TERMS_NOT_ACCEPTED['message'], status_code=400)

        # OTP challenge verification (Caveat #2)
        if not verification_token:
            return api_failure(message=ERROR_CODES.OTP_NOT_VERIFIED['message'], status_code=400)

        try:
            decoded = jwt.decode(verification_token, settings.JWT_SECRET, algorithms=['HS256'])
            if decoded.get('purpose') != 'registration' or decoded.get('email') != email:
                return api_failure(message=ERROR_CODES.OTP_NOT_VERIFIED['message'], status_code=400)
        except Exception:
            return api_failure(message=ERROR_CODES.OTP_NOT_VERIFIED['message'], status_code=400)

        if User.objects.filter(email=email).exists():
            return api_failure(message=ERROR_CODES.USER_ALREADY_EXISTS['message'], status_code=400)

        # Profile model name resolution
        profile_model_map = {
            USER_TYPES.INDIVIDUAL: 'IndividualProfile',
            USER_TYPES.WASTE_COLLECTOR: 'WasteCollectorProfile',
            USER_TYPES.RECYCLE_COMPANY: 'RecycleCompanyProfile',
            USER_TYPES.BIG_ORGANIZATION: 'BigOrganizationProfile',
        }
        profile_model = profile_model_map.get(user_type, 'IndividualProfile')

        # Create user
        user = User(
            name=name,
            email=email,
            phone=phone,
            user_type=user_type,
            role=ROLES.USER,
            terms_accepted=terms_accepted,
            otp_verified=True,
            auth_provider='local',
            profile_model=profile_model,
        )
        user.set_password(password)
        user.save()

        # Create typed profile
        address = data.get('address', '')
        company_name = data.get('companyName', '')
        business_license_no = data.get('businessLicenseNo', '')
        waste_type = data.get('wasteType', '')
        recycling_capabilities = data.get('recyclingCapabilities', '')

        if user_type == USER_TYPES.INDIVIDUAL:
            IndividualProfile.objects.create(user=user, address=address)
        elif user_type == USER_TYPES.WASTE_COLLECTOR:
            WasteCollectorProfile.objects.create(
                user=user, address=address, company_name=company_name, business_license_no=business_license_no
            )
        elif user_type == USER_TYPES.RECYCLE_COMPANY:
            RecycleCompanyProfile.objects.create(
                user=user,
                address=address,
                company_name=company_name,
                business_license_no=business_license_no,
                waste_type=waste_type,
                recycling_capabilities=recycling_capabilities,
            )
        elif user_type == USER_TYPES.BIG_ORGANIZATION:
            BigOrganizationProfile.objects.create(
                user=user, address=address, company_name=company_name, business_license_no=business_license_no
            )

        token = generate_jwt_token(user)
        resp = api_success(
            data={'token': token, 'user': user.to_dict()},
            message=MESSAGES.USER_REGISTERED,
            status_code=201,
        )
        return set_auth_cookie(resp, token)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return api_failure(message=ERROR_CODES.INVALID_CREDENTIALS['message'], status_code=401)

        if not verify_user_password(password, user.password):
            return api_failure(message=ERROR_CODES.INVALID_CREDENTIALS['message'], status_code=401)

        token = generate_jwt_token(user)
        resp = api_success(
            data={'token': token, 'user': user.to_dict()},
            message=MESSAGES.LOGIN_SUCCESS,
        )
        return set_auth_cookie(resp, token)

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        credential = data.get('credential')
        email = data.get('email')
        name = data.get('name')
        picture = data.get('picture')
        google_id = data.get('googleId')

        if credential:
            # Decode payload
            try:
                parts = credential.split('.')
                if len(parts) >= 2:
                    import base64
                    import json
                    padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
                    parsed = json.loads(base64.urlsafe_b64decode(padded).decode('utf-8'))
                    email = email or parsed.get('email')
                    name = name or parsed.get('name')
                    picture = picture or parsed.get('picture')
                    google_id = google_id or parsed.get('sub')
            except Exception:
                pass

        if not email:
            return api_failure(message='Email is required for Google login', status_code=400)

        email = email.lower().strip()
        user = User.objects.filter(email=email).first()

        if user:
            if google_id and not user.google_id:
                user.google_id = google_id
            if picture and not user.avatar:
                user.avatar = picture
            user.save()
        else:
            user = User(
                name=name or email.split('@')[0],
                email=email,
                phone='',
                google_id=google_id or f'google_{int(time.time())}',
                auth_provider='google',
                avatar=picture or '',
                user_type=USER_TYPES.INDIVIDUAL,
                role=ROLES.USER,
                terms_accepted=True,
                otp_verified=True,
            )
            user.set_unusable_password()
            user.save()
            IndividualProfile.objects.create(user=user, address='', profile_photo=picture or '')

        token = generate_jwt_token(user)
        resp = api_success(
            data={'token': token, 'user': user.to_dict()},
            message='Google login successful',
        )
        return set_auth_cookie(resp, token)

class LogoutView(APIView):
    permission_classes = [IsAuthenticatedCustom]

    def post(self, request):
        user = request.user
        if user and user.is_authenticated:
            user.token_version += 1
            user.save(update_fields=['token_version'])

        resp = api_success(message='Logged out successfully')
        resp.delete_cookie('token')
        return resp

class SendRegistrationOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        if not email:
            return api_failure(message='Email is required', status_code=400)

        if User.objects.filter(email=email).exists():
            return api_failure(message=ERROR_CODES.USER_ALREADY_EXISTS['message'], status_code=400)

        code = str(random.randint(100000, 999999))
        hashed = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        expires_at = timezone.now() + timedelta(seconds=settings.OTP_EXPIRATION_SECONDS)

        OTP.objects.create(email=email, otp=hashed, expires_at=expires_at)
        return api_success(message=MESSAGES.OTP_SENT)

class SendResetOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        if not email:
            return api_failure(message='Email is required', status_code=400)

        if not User.objects.filter(email=email).exists():
            return api_failure(message=ERROR_CODES.USER_NOT_FOUND['message'], status_code=404)

        code = str(random.randint(100000, 999999))
        hashed = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        expires_at = timezone.now() + timedelta(seconds=settings.OTP_EXPIRATION_SECONDS)

        OTP.objects.create(email=email, otp=hashed, expires_at=expires_at)
        return api_success(message=MESSAGES.OTP_SENT)

class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        code = str(request.data.get('otp', '')).strip()
        purpose = request.query_params.get('purpose')

        record = OTP.objects.filter(email=email, used_at__isnull=True).order_by('-created_at').first()
        if not record:
            return api_failure(message=ERROR_CODES.INVALID_OTP['message'], status_code=400)

        if record.expires_at < timezone.now():
            record.used_at = timezone.now()
            record.save(update_fields=['used_at'])
            return api_failure(message=ERROR_CODES.INVALID_OTP['message'], status_code=400)

        try:
            is_match = bcrypt.checkpw(code.encode('utf-8'), record.otp.encode('utf-8'))
        except Exception:
            is_match = (code == record.otp)

        if not is_match:
            return api_failure(message=ERROR_CODES.INVALID_OTP['message'], status_code=400)

        record.used_at = timezone.now()
        record.save(update_fields=['used_at'])

        data = {}
        if purpose == 'registration':
            data['verificationToken'] = sign_verification_token(email)

        return api_success(data=data, message=MESSAGES.OTP_VERIFIED)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        code = str(request.data.get('otp', '')).strip()
        password = request.data.get('password', '')

        record = OTP.objects.filter(email=email).order_by('-created_at').first()
        if not record:
            return api_failure(message=ERROR_CODES.INVALID_OTP['message'], status_code=400)

        try:
            is_match = bcrypt.checkpw(code.encode('utf-8'), record.otp.encode('utf-8'))
        except Exception:
            is_match = (code == record.otp)

        if not is_match:
            return api_failure(message=ERROR_CODES.INVALID_OTP['message'], status_code=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return api_failure(message=ERROR_CODES.USER_NOT_FOUND['message'], status_code=404)

        user.set_password(password)
        user.token_version += 1
        user.save()

        return api_success(message=MESSAGES.PASSWORD_RESET_SUCCESS)

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')

        try:
            admin = User.objects.get(email=email, role=ROLES.ADMIN)
        except User.DoesNotExist:
            return api_failure(message=ERROR_CODES.INVALID_CREDENTIALS['message'], status_code=401)

        if not verify_user_password(password, admin.password):
            return api_failure(message=ERROR_CODES.INVALID_CREDENTIALS['message'], status_code=401)

        token = generate_jwt_token(admin)
        return api_success(
            data={
                'token': token,
                'user': {'id': str(admin.id), 'name': admin.name, 'email': admin.email, 'role': admin.role},
            },
            message=MESSAGES.ADMIN_LOGIN_SUCCESS,
        )
