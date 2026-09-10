from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from rest_framework import (
    generics,
    permissions,
    serializers,
    status,
)
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.maintenance.models import MaintenanceRequest
from apps.maintenance.services import MaintenanceService
from apps.properties.permissions import IsPropertyManager

from .serializers import MaintenanceRequestSerializer


# ============================================================
# LIST / CREATE
# ============================================================


class MaintenanceListCreateView(
    generics.ListCreateAPIView
):
    """
    List and create maintenance requests.

    Tenants can create requests for units where they
    have an active tenancy.

    Property managers can view requests for properties
    they manage.
    """

    serializer_class = MaintenanceRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = MaintenanceRequest.objects.select_related(
            "tenant",
            "property",
            "property__manager",
            "unit",
            "assigned_to",
        )

        if user.is_staff:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                property__manager=user,
            )

        if user.role == UserRole.TENANT:
            return queryset.filter(
                tenant=user,
            )

        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role != UserRole.TENANT:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Only tenants can submit "
                        "maintenance requests."
                    )
                }
            )

        unit = serializer.validated_data.get(
            "unit"
        )

        if unit is None:
            raise serializers.ValidationError(
                {
                    "unit": (
                        "Unit is required when creating "
                        "a maintenance request."
                    )
                }
            )

        try:
            MaintenanceService.create_request(
                tenant=user,
                unit=unit,
                title=serializer.validated_data[
                    "title"
                ],
                description=serializer.validated_data[
                    "description"
                ],
                priority=serializer.validated_data.get(
                    "priority"
                ),
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )


# ============================================================
# DETAIL / UPDATE
# ============================================================


class MaintenanceDetailView(
    generics.RetrieveUpdateAPIView
):
    """
    Retrieve or update a maintenance request.

    Workflow-related fields cannot be changed through
    normal PATCH or PUT requests.
    """

    serializer_class = MaintenanceRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = MaintenanceRequest.objects.select_related(
            "tenant",
            "property",
            "property__manager",
            "unit",
            "assigned_to",
        )

        if user.is_staff:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                property__manager=user,
            )

        if user.role == UserRole.TENANT:
            return queryset.filter(
                tenant=user,
            )

        return queryset.none()

    def perform_update(self, serializer):
        if self.request.user.role != (
            UserRole.PROPERTY_MANAGER
        ):
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Only property managers can "
                        "update maintenance requests."
                    )
                }
            )

        forbidden_fields = {
            "status",
            "assigned_to",
            "actual_cost",
            "completed_at",
        }

        attempted_fields = (
            forbidden_fields
            & set(self.request.data.keys())
        )

        if attempted_fields:
            raise serializers.ValidationError(
                {
                    field: (
                        "This field must be changed through "
                        "the appropriate workflow endpoint."
                    )
                    for field in attempted_fields
                }
            )

        serializer.save()


# ============================================================
# START
# ============================================================


class MaintenanceStartView(
    generics.GenericAPIView
):
    """
    Start work on a PENDING maintenance request.

    Only the property manager who manages the property
    can start the request.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        maintenance_request = self.get_object()

        try:
            maintenance_request = (
                MaintenanceService.start_request(
                    request_instance=maintenance_request,
                    manager=request.user,
                )
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            MaintenanceRequestSerializer(
                maintenance_request
            ).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# COMPLETE
# ============================================================


class MaintenanceCompleteView(
    generics.GenericAPIView
):
    """
    Complete an IN_PROGRESS maintenance request.

    Only the property manager who manages the property
    can complete the request.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        maintenance_request = self.get_object()

        actual_cost = request.data.get(
            "actual_cost",
            None,
        )

        if actual_cost is not None:
            try:
                actual_cost = float(
                    actual_cost
                )
            except (
                TypeError,
                ValueError,
            ):
                raise serializers.ValidationError(
                    {
                        "actual_cost": (
                            "Actual cost must be a valid "
                            "number."
                        )
                    }
                )

        try:
            maintenance_request = (
                MaintenanceService.complete_request(
                    request_instance=maintenance_request,
                    manager=request.user,
                    actual_cost=actual_cost,
                )
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            MaintenanceRequestSerializer(
                maintenance_request
            ).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# CANCEL
# ============================================================


class MaintenanceCancelView(
    generics.GenericAPIView
):
    """
    Cancel a PENDING maintenance request.

    Only the tenant who created the request can cancel it.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            tenant=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        maintenance_request = self.get_object()

        try:
            maintenance_request = (
                MaintenanceService.cancel_request(
                    request_instance=maintenance_request,
                    tenant=request.user,
                )
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            MaintenanceRequestSerializer(
                maintenance_request
            ).data,
            status=status.HTTP_200_OK,
        )