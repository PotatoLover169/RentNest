from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsPropertyManager(BasePermission):
    """
    Allows access only to authenticated property managers.
    """

    message = "Only property managers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROPERTY_MANAGER
        )


class IsPropertyManagerOwner(BasePermission):
    """
    Allows a property manager to access only properties
    that they manage.
    """

    message = "You do not have permission to access this property."

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROPERTY_MANAGER
            and obj.manager_id == request.user.id
        )


class IsPropertyManagerOrReadOnly(BasePermission):
    """
    Property managers may modify their own properties.
    Authenticated users may have read-only access.
    """

    message = "You do not have permission to modify this property."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return request.user.role == UserRole.PROPERTY_MANAGER

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return (
            request.user.role == UserRole.PROPERTY_MANAGER
            and obj.manager_id == request.user.id
        )