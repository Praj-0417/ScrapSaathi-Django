"""
Role-based authorization permissions.
Matches monolith requireRoleMiddleware and protect middleware.
"""

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from common.constants import ROLES, USER_TYPES

class IsAuthenticatedCustom(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            raise NotAuthenticated('Unauthorized')
        return True

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            raise NotAuthenticated('Unauthorized')
        if request.user.role != ROLES.ADMIN:
            raise PermissionDenied('Forbidden: Admin access required')
        return True

class IsCollectorRole(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            raise NotAuthenticated('Unauthorized')
        if request.user.user_type != USER_TYPES.WASTE_COLLECTOR:
            raise PermissionDenied('Forbidden: Waste collector access required')
        return True
