from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import IsAdminOrPropertyManager

from apps.properties.models import (
    Property,
    PropertyStatus,
    Unit,
    UnitStatus,
)
from apps.properties.permissions import IsPropertyManagerOrReadOnly
from apps.properties.services import (
    PropertyService,
    UnitService,
)

from .serializers import (
    PropertySerializer,
    UnitSerializer,
)


# ============================================================
# PROPERTY API
# ============================================================

class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsPropertyManagerOrReadOnly(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Property.objects.all()

        if user.role == UserRole.PROPERTY_MANAGER:
            return Property.objects.filter(
                manager=user,
            )

        return Property.objects.filter(
            status=PropertyStatus.ACTIVE,
        )

    def perform_create(self, serializer):
        user = self.request.user

        # ------------------------------------------------------
        # ADMIN
        # ------------------------------------------------------
        if user.role == UserRole.ADMIN:
            manager = serializer.validated_data.get(
                "manager",
            )

            if manager is None:
                raise ValidationError(
                    {
                        "manager_id": (
                            "A property manager is required "
                            "when an administrator creates "
                            "a property."
                        )
                    }
                )

            PropertyService.create_property(
                manager=manager,
                **{
                    key: value
                    for key, value in serializer.validated_data.items()
                    if key != "manager"
                },
            )

            return

        # ------------------------------------------------------
        # PROPERTY MANAGER
        # ------------------------------------------------------
        if user.role == UserRole.PROPERTY_MANAGER:
            if "manager" in serializer.validated_data:
                raise ValidationError(
                    {
                        "manager_id": (
                            "Property managers cannot assign "
                            "properties to another manager."
                        )
                    }
                )

            PropertyService.create_property(
                manager=user,
                **serializer.validated_data,
            )

            return

        # ------------------------------------------------------
        # ALL OTHER ROLES
        # ------------------------------------------------------
        raise ValidationError(
            "Only administrators and property managers "
            "can create properties."
        )


class PropertyDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PropertySerializer

    def get_permissions(self):
        return [
            IsPropertyManagerOrReadOnly(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Property.objects.all()

        if user.role == UserRole.PROPERTY_MANAGER:
            return Property.objects.filter(
                manager=user,
            )

        return Property.objects.filter(
            status=PropertyStatus.ACTIVE,
        )

    def perform_update(self, serializer):
        if "manager" in serializer.validated_data:
            raise ValidationError(
                {
                    "manager_id": (
                        "The property manager cannot be changed "
                        "through the property update workflow."
                    )
                }
            )

        PropertyService.update_property(
            property_instance=self.get_object(),
            **serializer.validated_data,
        )


class PropertyDeactivateView(generics.GenericAPIView):
    serializer_class = PropertySerializer

    def get_permissions(self):
        return [
            IsAdminOrPropertyManager(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Property.objects.all()

        if user.role == UserRole.PROPERTY_MANAGER:
            return Property.objects.filter(
                manager=user,
            )

        return Property.objects.none()

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        property_instance = self.get_object()

        try:
            property_instance = PropertyService.deactivate_property(
                property_instance=property_instance,
            )
        except ValidationError as exc:
            raise ValidationError(
                {
                    "status": exc.messages,
                }
            )

        return Response(
            PropertySerializer(property_instance).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# UNIT API
# ============================================================

class UnitListCreateView(generics.ListCreateAPIView):
    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsAdminOrPropertyManager(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = Unit.objects.select_related(
            "property",
            "property__manager",
        )

        if user.role == UserRole.ADMIN:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                property__manager=user,
            )

        return queryset.filter(
            property__status=PropertyStatus.ACTIVE,
            status=UnitStatus.AVAILABLE,
        )

    def perform_create(self, serializer):
        user = self.request.user

        property_id = self.request.data.get(
            "property",
        )

        if not property_id:
            raise ValidationError(
                {
                    "property": (
                        "Property is required when creating a unit."
                    )
                }
            )

        # ------------------------------------------------------
        # ADMIN
        # ------------------------------------------------------
        if user.role == UserRole.ADMIN:
            property_instance = get_object_or_404(
                Property.objects.all(),
                pk=property_id,
            )

        # ------------------------------------------------------
        # PROPERTY MANAGER
        # ------------------------------------------------------
        else:
            property_instance = get_object_or_404(
                Property.objects.filter(
                    manager=user,
                ),
                pk=property_id,
            )

        UnitService.create_unit(
            property_instance=property_instance,
            **serializer.validated_data,
        )


class UnitDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [
                IsAdminOrPropertyManager(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = Unit.objects.select_related(
            "property",
            "property__manager",
        )

        if user.role == UserRole.ADMIN:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                property__manager=user,
            )

        return queryset.filter(
            property__status=PropertyStatus.ACTIVE,
            status=UnitStatus.AVAILABLE,
        )

    def perform_update(self, serializer):
        UnitService.update_unit(
            unit_instance=self.get_object(),
            **serializer.validated_data,
        )


class UnitStatusView(generics.GenericAPIView):
    serializer_class = UnitSerializer

    def get_permissions(self):
        return [
            IsAdminOrPropertyManager(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Unit.objects.select_related(
                "property",
                "property__manager",
            )

        if user.role == UserRole.PROPERTY_MANAGER:
            return Unit.objects.select_related(
                "property",
                "property__manager",
            ).filter(
                property__manager=user,
            )

        return Unit.objects.none()

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        unit_instance = self.get_object()

        new_status = request.data.get(
            "status",
        )

        try:
            unit_instance = UnitService.change_status(
                unit_instance=unit_instance,
                status=new_status,
            )
        except ValidationError as exc:
            raise ValidationError(
                {
                    "status": exc.messages,
                }
            )

        return Response(
            UnitSerializer(unit_instance).data,
            status=status.HTTP_200_OK,
        )


class UnitDeactivateView(generics.GenericAPIView):
    serializer_class = UnitSerializer

    def get_permissions(self):
        return [
            IsAdminOrPropertyManager(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Unit.objects.select_related(
                "property",
                "property__manager",
            )

        if user.role == UserRole.PROPERTY_MANAGER:
            return Unit.objects.select_related(
                "property",
                "property__manager",
            ).filter(
                property__manager=user,
            )

        return Unit.objects.none()

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        unit_instance = self.get_object()

        try:
            unit_instance = UnitService.deactivate_unit(
                unit_instance=unit_instance,
            )
        except ValidationError as exc:
            raise ValidationError(
                {
                    "status": exc.messages,
                }
            )

        return Response(
            UnitSerializer(unit_instance).data,
            status=status.HTTP_200_OK,
        )