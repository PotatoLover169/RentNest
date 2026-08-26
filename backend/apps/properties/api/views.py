from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.response import Response

from apps.properties.models import Property
from apps.properties.permissions import (
    IsPropertyManager,
    IsPropertyManagerOrReadOnly,
)
from apps.properties.services import PropertyService

from .serializers import (
    PropertyDetailSerializer,
    PropertySerializer,
)


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
            status="ACTIVE",
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

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Property.objects.all()

        if user.role == "PROPERTY_MANAGER":
            return Property.objects.filter(
                manager=user,
            )

        return Property.objects.filter(
            status="ACTIVE",
        )

    def get_permissions(self):
        return [
            IsPropertyManagerOrReadOnly(),
        ]

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

    def get_queryset(self):
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
            status=200,
        )