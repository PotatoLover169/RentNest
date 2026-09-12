from datetime import date

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

from apps.accounts.models import User, UserRole
from apps.properties.models import PropertyStatus, Unit
from apps.properties.permissions import IsPropertyManager

from apps.tenancies.models import Tenancy, TenancyStatus
from apps.tenancies.services import TenancyService

from .serializers import TenancySerializer


# ============================================================
# TENANCY LIST / CREATE
# ============================================================


class TenancyListCreateView(generics.ListCreateAPIView):
    """
    List accessible tenancies and create tenancies
    for units managed by the authenticated property manager.
    """

    serializer_class = TenancySerializer

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

        queryset = Tenancy.objects.select_related(
            "tenant",
            "unit",
            "unit__property",
            "unit__property__manager",
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
        unit_id = self.request.data.get("unit")
        tenant_id = self.request.data.get("tenant")

        if not unit_id:
            raise serializers.ValidationError(
                {
                    "unit": (
                        "Unit is required when creating "
                        "a tenancy."
                    )
                }
            )

        if not tenant_id:
            raise serializers.ValidationError(
                {
                    "tenant": (
                        "Tenant is required when creating "
                        "a tenancy."
                    )
                }
            )

        unit = get_object_or_404(
            Unit.objects.select_related(
                "property",
            ).filter(
                property__manager=self.request.user,
                property__status=PropertyStatus.ACTIVE,
            ),
            pk=unit_id,
        )

        tenant = get_object_or_404(
            User.objects.filter(
                pk=tenant_id,
                role=UserRole.TENANT,
            ),
            pk=tenant_id,
        )

        TenancyService.create_tenancy(
            tenant=tenant,
            unit=unit,
            **serializer.validated_data,
        )


# ============================================================
# TENANCY DETAIL
# ============================================================


class TenancyDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a tenancy.

    Property managers can only modify tenancies belonging
    to units they manage.

    Tenants can view their own tenancies.

    Tenancy status cannot be changed through PUT/PATCH.
    Status changes must use the workflow endpoints.
    """

    serializer_class = TenancySerializer

    def get_permissions(self):
        if self.request.method in (
            "PUT",
            "PATCH",
        ):
            return [
                IsPropertyManager(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self) -> QuerySet:
        user = self.request.user

        queryset = Tenancy.objects.select_related(
            "tenant",
            "unit",
            "unit__property",
            "unit__property__manager",
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
        tenancy = self.get_object()

        # --------------------------------------------------------
        # Status changes must go through service workflows.
        # --------------------------------------------------------

        if "status" in serializer.validated_data:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Tenancy status must be changed through "
                        "the appropriate workflow endpoint."
                    )
                }
            )

        # --------------------------------------------------------
        # Update through service layer.
        # --------------------------------------------------------

        try:
            TenancyService.update_tenancy(
                tenancy_instance=tenancy,
                **serializer.validated_data,
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )


# ============================================================
# TENANCY ACTIVATION
# ============================================================


class TenancyActivateView(generics.GenericAPIView):
    """
    Activate a pending tenancy.

    Business rules are enforced by TenancyService.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = TenancySerializer

    def get_queryset(self):
        return Tenancy.objects.select_related(
            "unit",
            "unit__property",
        ).filter(
            unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        tenancy = self.get_object()

        try:
            tenancy = TenancyService.activate_tenancy(
                tenancy_instance=tenancy,
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            TenancySerializer(tenancy).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# TENANCY END
# ============================================================


class TenancyEndView(generics.GenericAPIView):
    """
    End an active tenancy.

    The unit becomes AVAILABLE through the service workflow.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = TenancySerializer

    def get_queryset(self):
        return Tenancy.objects.select_related(
            "unit",
            "unit__property",
        ).filter(
            unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        tenancy = self.get_object()

        end_date = request.data.get("end_date")

        if not end_date:
            raise serializers.ValidationError(
                {
                    "end_date": "End date is required."
                }
            )

        try:
            parsed_end_date = date.fromisoformat(
                end_date,
            )

        except (TypeError, ValueError):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "Enter a valid date in "
                        "YYYY-MM-DD format."
                    )
                }
            )

        try:
            tenancy = TenancyService.end_tenancy(
                tenancy_instance=tenancy,
                end_date=parsed_end_date,
            )

        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            TenancySerializer(tenancy).data,
            status=status.HTTP_200_OK,
        )