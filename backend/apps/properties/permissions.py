from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsPropertyManager(BasePermission):
    message = "Only property managers can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROPERTY_MANAGER
        )


class IsPropertyManagerOwner(BasePermission):
    message = "You do not have permission to access this property."

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.PROPERTY_MANAGER
            and obj.manager_id == request.user.id
        )


class IsPropertyManagerOrReadOnly(BasePermission):
    message = "You do not have permission to modify this property."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Anyone authenticated can read properties.
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # ADMIN and PROPERTY_MANAGER can modify properties.
        return request.user.role in {
            UserRole.ADMIN,
            UserRole.PROPERTY_MANAGER,
        }

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Anyone authenticated can read a property that is
        # available through the view's queryset.
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # ADMIN has full property access.
        if request.user.role == UserRole.ADMIN:
            return True

        # PROPERTY_MANAGER can only modify their own properties.
        return (
            request.user.role == UserRole.PROPERTY_MANAGER
            and obj.manager_id == request.user.id
        )