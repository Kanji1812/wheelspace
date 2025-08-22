from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_type == 'customer' and request.user.is_verified :
            return True
        raise PermissionDenied(detail="User is not authorized as Customer")


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_type == 'owner' and request.user.is_verified:
            return True
        raise PermissionDenied(detail="User is not authorized as Owner")


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_type == 'admin' and request.user.is_verified:
            return True
        raise PermissionDenied(detail="User is not authorized as Admin")


class IsGuard(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_type == 'guard' and request.user.is_verified:
            return True
        raise PermissionDenied(detail="User is not authorized as Guard")


class IsOwnerOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_type in ['admin', 'owner'] and request.user.is_verified:
            return True
        raise PermissionDenied(detail="User must be Owner or Admin")
