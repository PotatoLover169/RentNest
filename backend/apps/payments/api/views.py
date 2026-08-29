from datetime import date

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response

from apps.accounts.models import User, UserRole
from apps.properties.models import PropertyStatus, Unit
from apps.properties.permissions import IsPropertyManager

from apps.tenancies.models import Tenancy

from apps.payments.models import Payment
from apps.payments.services import PaymentService

from .serializers import PaymentSerializer


# ============================================================
# PAYMENT LIST / CREATE
# ============================================================


class PaymentListCreateView(generics.ListCreateAPIView):
    """
    List accessible payments and create payments for
    tenancies managed by the authenticated property manager.
    """

    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsPropertyManager(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self):
        user = self.request.user

        queryset = Payment.objects.select_related(
            "tenant",
            "tenancy",
            "tenancy__unit",
            "tenancy__unit__property",
            "tenancy__unit__property__manager",
        )

        if user.is_staff:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                tenancy__unit__property__manager=user,
            )

        if user.role == UserRole.TENANT:
            return queryset.filter(
                tenant=user,
            )

        return queryset.none()

    def perform_create(self, serializer):
        tenancy_id = self.request.data.get("tenancy")
        tenant_id = self.request.data.get("tenant")

        if not tenancy_id:
            raise serializers.ValidationError(
                {
                    "tenancy": (
                        "Tenancy is required when creating a payment."
                    )
                }
            )

        if not tenant_id:
            raise serializers.ValidationError(
                {
                    "tenant": (
                        "Tenant is required when creating a payment."
                    )
                }
            )

        tenancy = get_object_or_404(
            Tenancy.objects.select_related(
                "tenant",
                "unit",
                "unit__property",
            ).filter(
                unit__property__manager=self.request.user,
                unit__property__status=PropertyStatus.ACTIVE,
            ),
            pk=tenancy_id,
        )

        tenant = get_object_or_404(
            User.objects.filter(
                pk=tenant_id,
                role=UserRole.TENANT,
            ),
            pk=tenant_id,
        )

        if tenancy.tenant_id != tenant.id:
            raise serializers.ValidationError(
                {
                    "tenant": (
                        "The selected tenant does not belong "
                        "to this tenancy."
                    )
                }
            )

        try:
            PaymentService.create_payment(
                tenancy=tenancy,
                tenant=tenant,
                **serializer.validated_data,
            )
        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )


# ============================================================
# PAYMENT DETAIL
# ============================================================


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a payment.

    Property managers can modify payments belonging to
    units they manage.

    Tenants can view their own payments.

    Payment status cannot be changed through PATCH/PUT.
    Status changes must use the dedicated workflow endpoints.
    """

    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [
                IsPropertyManager(),
            ]

        return [
            permissions.IsAuthenticated(),
        ]

    def get_queryset(self):
        user = self.request.user

        queryset = Payment.objects.select_related(
            "tenant",
            "tenancy",
            "tenancy__unit",
            "tenancy__unit__property",
            "tenancy__unit__property__manager",
        )

        if user.is_staff:
            return queryset

        if user.role == UserRole.PROPERTY_MANAGER:
            return queryset.filter(
                tenancy__unit__property__manager=user,
            )

        if user.role == UserRole.TENANT:
            return queryset.filter(
                tenant=user,
            )

        return queryset.none()

    def perform_update(self, serializer):
        payment = self.get_object()

        if "status" in serializer.validated_data:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Payment status must be changed through "
                        "the appropriate workflow endpoint."
                    )
                }
            )

        if "tenant" in serializer.validated_data:
            raise serializers.ValidationError(
                {
                    "tenant": (
                        "Payment tenant cannot be changed."
                    )
                }
            )

        if "tenancy" in serializer.validated_data:
            raise serializers.ValidationError(
                {
                    "tenancy": (
                        "Payment tenancy cannot be changed."
                    )
                }
            )

        serializer.save()


# ============================================================
# PAYMENT MARK PAID
# ============================================================


class PaymentMarkPaidView(generics.GenericAPIView):
    """
    Mark a pending payment as PAID.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
            "tenant",
            "tenancy",
            "tenancy__unit",
            "tenancy__unit__property",
        ).filter(
            tenancy__unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        payment = self.get_object()

        payment_date = request.data.get("payment_date")
        reference_number = request.data.get("reference_number")

        parsed_payment_date = None

        if payment_date:
            try:
                parsed_payment_date = date.fromisoformat(
                    payment_date,
                )
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {
                        "payment_date": (
                            "Enter a valid date in YYYY-MM-DD format."
                        )
                    }
                )

        try:
            payment = PaymentService.mark_paid(
                payment_instance=payment,
                payment_date=parsed_payment_date,
                reference_number=reference_number,
            )
        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# PAYMENT MARK FAILED
# ============================================================


class PaymentMarkFailedView(generics.GenericAPIView):
    """
    Mark a pending payment as FAILED.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
            "tenant",
            "tenancy",
            "tenancy__unit",
            "tenancy__unit__property",
        ).filter(
            tenancy__unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        payment = self.get_object()

        notes = request.data.get("notes")

        try:
            payment = PaymentService.mark_failed(
                payment_instance=payment,
                notes=notes,
            )
        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# PAYMENT REFUND
# ============================================================


class PaymentRefundView(generics.GenericAPIView):
    """
    Refund a paid payment.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
            "tenant",
            "tenancy",
            "tenancy__unit",
            "tenancy__unit__property",
        ).filter(
            tenancy__unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        payment = self.get_object()

        notes = request.data.get("notes")

        try:
            payment = PaymentService.refund_payment(
                payment_instance=payment,
                notes=notes,
            )
        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )


# ============================================================
# PAYMENT CANCEL
# ============================================================


class PaymentCancelView(generics.GenericAPIView):
    """
    Cancel a pending payment.
    """

    permission_classes = [
        IsPropertyManager,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
            "tenant",
            "tenancy",
            "tenancy__unit",
            "tenancy__unit__property",
        ).filter(
            tenancy__unit__property__manager=self.request.user,
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs["pk"],
        )

    def post(self, request, *args, **kwargs):
        payment = self.get_object()

        notes = request.data.get("notes")

        try:
            payment = PaymentService.cancel_payment(
                payment_instance=payment,
                notes=notes,
            )
        except ValidationError as exc:
            raise serializers.ValidationError(
                {
                    "detail": exc.messages,
                }
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_200_OK,
        )   