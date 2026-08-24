from rest_framework.permissions import BasePermission

from .models import UserRole


class IsAdmin(BasePermission):
    """
    Allows access only to RentNest administrators.
    """

    message = "Administrator access is required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class IsPropertyManager(BasePermission):
    """
    Allows access only to property managers.
    """

    message = "Property manager access is required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROPERTY_MANAGER
        )


class IsTenant(BasePermission):
    """
    Allows access only to tenants.
    """

    message = "Tenant access is required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.TENANT
        )


class IsAdminOrPropertyManager(BasePermission):
    """
    Allows access to administrators and property managers.
    """

    message = "Administrator or property manager access is required."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role in {
            UserRole.ADMIN,
            UserRole.PROPERTY_MANAGER,
        }   