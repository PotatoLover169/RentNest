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
from apps.maintenance.models import (
    MaintenanceRequest,
)
from apps.maintenance.services import (
    MaintenanceService,
)
from apps.properties.permissions import IsPropertyManager

from .serializers import MaintenanceRequestSerializer


# ============================================================
# LIST / CREATE
# ============================================================


class MaintenanceListCreateView(
    generics.ListCreateAPIView
):
    """
    List maintenance requests accessible to the user.

    Tenants can create requests for their active unit.

    Property managers can view requests for properties
    they manage.
    """

    serializer_class = MaintenanceRequestSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                permissions.IsAuthenticated(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = MaintenanceRequest.objects.select_related(
            "tenant",
            "unit",
            "unit__property",
            "unit__property__manager",
            "assigned_to",
        )

        if user.is_staff:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                unit__property__manager=user,
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

        unit_id = self.request.data.get("unit")

        if not unit_id:
            raise serializers.ValidationError(
                {
                    "unit": (
                        "Unit is required when creating "
                        "a maintenance request."
                    )
                }
            )

        from apps.properties.models import Unit

        unit = get_object_or_404(
            Unit.objects.select_related(
                "property",
            ),
            pk=unit_id,
        )

        try:
            MaintenanceService.create_request(
                tenant=user,
                unit=unit,
                **serializer.validated_data,
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )


# ============================================================
# DETAIL
# ============================================================


class MaintenanceDetailView(
    generics.RetrieveUpdateAPIView
):
    """
    Retrieve or update a maintenance request.

    Status and workflow fields cannot be changed through
    normal PATCH/PUT requests.
    """

    serializer_class = MaintenanceRequestSerializer

    def get_permissions(self):
        if self.request.method in (
            "PUT",
            "PATCH",
        ):
            return [
                permissions.IsAuthenticated(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = MaintenanceRequest.objects.select_related(
            "tenant",
            "unit",
            "unit__property",
            "unit__property__manager",
            "assigned_to",
        )

        if user.is_staff:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                unit__property__manager=user,
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
            "resolution_notes",
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
    Start work on an OPEN maintenance request.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            unit__property__manager=self.request.user,
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
# RESOLVE
# ============================================================


class MaintenanceResolveView(
    generics.GenericAPIView
):
    """
    Resolve an IN_PROGRESS maintenance request.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        maintenance_request = self.get_object()

        resolution_notes = request.data.get(
            "resolution_notes"
        )

        if resolution_notes is None:
            raise serializers.ValidationError(
                {
                    "resolution_notes": (
                        "Resolution notes are required."
                    )
                }
            )

        try:
            maintenance_request = (
                MaintenanceService.resolve_request(
                    request_instance=maintenance_request,
                    manager=request.user,
                    resolution_notes=resolution_notes,
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
# CLOSE
# ============================================================


class MaintenanceCloseView(
    generics.GenericAPIView
):
    """
    Close a RESOLVED maintenance request.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = MaintenanceRequestSerializer

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(
            unit__property__manager=self.request.user,
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
                MaintenanceService.close_request(
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
# CANCEL
# ============================================================


class MaintenanceCancelView(
    generics.GenericAPIView
):
    """
    Cancel an OPEN maintenance request.

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