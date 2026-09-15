from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsAdminOrPropertyManager(BasePermission):
    """
    Allow only administrators and property managers.
    """

    message = (
        "Administrator or property manager access is required."
    )

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role
            in {
                UserRole.ADMIN,
                UserRole.PROPERTY_MANAGER,
            }
        )


class IsTenant(BasePermission):
    """
    Allow only tenants.
    """

    message = "Tenant access is required."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.TENANT
        )