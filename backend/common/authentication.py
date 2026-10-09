"""
Custom JWT Authentication supporting both Bearer header and HTTP-only cookie,
with tokenVersion revocation check matching monolith authMiddleware.js.
"""

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from common.constants import ERROR_CODES

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('token')

        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1].strip()

        if not token:
            return None  # Unauthenticated request; allow permission classes to handle

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed({
                'success': False,
                'message': 'Authentication token has expired. Please log in again.',
                'data': None,
                'errors': [],
            })
        except jwt.InvalidTokenError:
            raise AuthenticationFailed({
                'success': False,
                'message': 'Invalid or malformed authentication token.',
                'data': None,
                'errors': [],
            })

        user_id = payload.get('userId')
        if not user_id:
            raise AuthenticationFailed({
                'success': False,
                'message': ERROR_CODES.UNAUTHORIZED['message'],
                'data': None,
                'errors': [],
            })

        from users.models import User
        try:
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            raise AuthenticationFailed({
                'success': False,
                'message': ERROR_CODES.UNAUTHORIZED['message'],
                'data': None,
                'errors': [],
            })

        # Token revocation check (Caveat #4)
        token_version = payload.get('version', 0)
        if token_version < user.token_version:
            raise AuthenticationFailed({
                'success': False,
                'message': ERROR_CODES.TOKEN_REVOKED['message'],
                'data': None,
                'errors': [],
            })

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'
