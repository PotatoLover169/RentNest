from datetime import date

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.accounts.models import User, UserRole
from apps.properties.models import PropertyStatus
from apps.tenancies.models import Tenancy

from apps.payments.models import Payment
from apps.payments.services import PaymentService

from .serializers import PaymentSerializer


# ============================================================
# PAYMENT LIST / CREATE
# ============================================================


class PaymentListCreateView(generics.ListCreateAPIView):
    """
    List and create rental payments.
    """

    serializer_class = PaymentSerializer

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
        user = self.request.user

        if user.role != UserRole.PROPERTY_MANAGER:
            raise PermissionDenied(
                "Only property managers can create payments."
            )

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
                unit__property__manager=user,
                unit__property__status=PropertyStatus.ACTIVE,
            ),
            pk=tenancy_id,
        )

        tenant = get_object_or_404(
            User.objects.filter(
                pk=tenant_id,
                role=UserRole.TENANT,
            )
        )

        if tenancy.tenant_id != tenant.id:
            raise serializers.ValidationError(
                {
                    "tenant": (
                        "This tenancy does not belong to "
                        "the specified tenant."
                    )
                }
            )

        try:
            payment = PaymentService.create_payment(
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

        serializer.instance = payment


# ============================================================
# PAYMENT DETAIL
# ============================================================


class PaymentDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a payment.
    """

    serializer_class = PaymentSerializer

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

    def update(self, request, *args, **kwargs):
        if request.user.role != UserRole.PROPERTY_MANAGER:
            raise PermissionDenied(
                "Only property managers can update payments."
            )

        protected_fields = {
            "status",
            "tenant",
            "tenancy",
        }

        attempted_protected_fields = (
            protected_fields
            & set(request.data.keys())
        )

        if attempted_protected_fields:
            raise serializers.ValidationError(
                {
                    field: (
                        "This field cannot be changed directly. "
                        "Use the appropriate payment workflow endpoint."
                    )
                    for field in attempted_protected_fields
                }
            )

        return super().update(request, *args, **kwargs)


# ============================================================
# MARK PAYMENT AS PAID
# ============================================================


class PaymentMarkPaidView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
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
        if request.user.role != UserRole.PROPERTY_MANAGER:
            raise PermissionDenied(
                "Only property managers can update payment status."
            )

        payment = self.get_object()

        payment_date = request.data.get("payment_date")
        reference_number = request.data.get("reference_number")

        if payment_date:
            try:
                payment_date = date.fromisoformat(payment_date)
            except ValueError:
                raise serializers.ValidationError(
                    {
                        "payment_date": (
                            "Payment date must use YYYY-MM-DD format."
                        )
                    }
                )

        try:
            payment = PaymentService.mark_paid(
                payment_instance=payment,
                payment_date=payment_date,
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
# MARK PAYMENT AS FAILED
# ============================================================


class PaymentMarkFailedView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
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
        if request.user.role != UserRole.PROPERTY_MANAGER:
            raise PermissionDenied(
                "Only property managers can update payment status."
            )

        payment = self.get_object()

        try:
            payment = PaymentService.mark_failed(
                payment_instance=payment,
                notes=request.data.get("notes"),
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
# REFUND PAYMENT
# ============================================================


class PaymentRefundView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
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
        if request.user.role != UserRole.PROPERTY_MANAGER:
            raise PermissionDenied(
                "Only property managers can update payment status."
            )

        payment = self.get_object()

        try:
            payment = PaymentService.refund_payment(
                payment_instance=payment,
                notes=request.data.get("notes"),
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
# CANCEL PAYMENT
# ============================================================


class PaymentCancelView(generics.GenericAPIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related(
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
        if request.user.role != UserRole.PROPERTY_MANAGER:
            raise PermissionDenied(
                "Only property managers can update payment status."
            )

        payment = self.get_object()

        try:
            payment = PaymentService.cancel_payment(
                payment_instance=payment,
                notes=request.data.get("notes"),
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