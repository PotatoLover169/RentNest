from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.properties.models import (
    Property,
    PropertyStatus,
    Unit,
    UnitStatus,
)
from apps.properties.permissions import (
    IsPropertyManager,
    IsPropertyManagerOrReadOnly,
)
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
    """
    List properties accessible to the authenticated user
    and create properties for the authenticated property manager.
    """

    serializer_class = PropertySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsPropertyManager(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.is_staff:
            return Property.objects.all()

        if user.role == "PROPERTY_MANAGER":
            return Property.objects.filter(
                manager=user,
            )

        return Property.objects.filter(
            status=PropertyStatus.ACTIVE,
        )

    def perform_create(self, serializer):
        PropertyService.create_property(
            manager=self.request.user,
            **serializer.validated_data,
        )


class PropertyDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update a property.

    Property managers can only modify properties they manage.
    """

    serializer_class = PropertySerializer

    def get_permissions(self):
        return [
            IsPropertyManagerOrReadOnly(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        if user.is_staff:
            return Property.objects.all()

        if user.role == "PROPERTY_MANAGER":
            return Property.objects.filter(
                manager=user,
            )

        return Property.objects.filter(
            status=PropertyStatus.ACTIVE,
        )

    def perform_update(self, serializer):
        PropertyService.update_property(
            property_instance=self.get_object(),
            **serializer.validated_data,
        )


class PropertyDeactivateView(generics.GenericAPIView):
    """
    Deactivate a property instead of permanently deleting it.

    This preserves historical rental/property data.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = PropertySerializer

    def get_queryset(self) -> QuerySet:
        return Property.objects.filter(
            manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        property_instance = self.get_object()

        PropertyService.deactivate_property(
            property_instance=property_instance,
        )

        return Response(
            PropertySerializer(property_instance).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# UNIT API
# ============================================================


class UnitListCreateView(generics.ListCreateAPIView):
    """
    List units accessible to the authenticated user
    and create units for properties managed by the
    authenticated property manager.
    """

    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsPropertyManager(),
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

        if user.is_staff:
            return queryset

        if user.role == "PROPERTY_MANAGER":
            return queryset.filter(
                property__manager=user,
            )

        return queryset.filter(
            property__status=PropertyStatus.ACTIVE,
            status=UnitStatus.AVAILABLE,
        )

    def perform_create(self, serializer):
        property_id = self.request.data.get("property")

        if not property_id:
            raise ValidationError(
                {
                    "property": (
                        "Property is required when creating a unit."
                    )
                }
            )

        property_instance = get_object_or_404(
            Property.objects.filter(
                manager=self.request.user,
            ),
            pk=property_id,
        )

        UnitService.create_unit(
            property_instance=property_instance,
            **serializer.validated_data,
        )


class UnitDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a unit.

    Property managers can only modify units belonging
    to properties they manage.
    """

    serializer_class = UnitSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH"]:
            return [
                IsPropertyManager(),
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

        if user.is_staff:
            return queryset

        if user.role == "PROPERTY_MANAGER":
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
    """
    Change the operational status of a unit.

    Only the property manager responsible for the
    property can change its status.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = UnitSerializer

    def get_queryset(self) -> QuerySet:
        return Unit.objects.select_related(
            "property",
            "property__manager",
        ).filter(
            property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        unit_instance = self.get_object()

        new_status = request.data.get("status")

        valid_statuses = {
            choice[0]
            for choice in UnitStatus.choices
        }

        if new_status not in valid_statuses:
            raise ValidationError(
                {
                    "status": "Invalid unit status.",
                }
            )

        UnitService.change_status(
            unit_instance=unit_instance,
            status=new_status,
        )

        return Response(
            UnitSerializer(unit_instance).data,
            status=status.HTTP_200_OK,
        )


class UnitDeactivateView(generics.GenericAPIView):
    """
    Deactivate a unit instead of deleting it.

    Historical rental/property data is preserved.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = UnitSerializer

    def get_queryset(self) -> QuerySet:
        return Unit.objects.select_related(
            "property",
            "property__manager",
        ).filter(
            property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        unit_instance = self.get_object()

        UnitService.deactivate_unit(
            unit_instance=unit_instance,
        )

        return Response(
            UnitSerializer(unit_instance).data,
            status=status.HTTP_200_OK,
        )