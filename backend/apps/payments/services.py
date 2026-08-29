from django.core.exceptions import ValidationError
from django.db import transaction

from apps.tenancies.models import Tenancy, TenancyStatus

from .models import Payment, PaymentStatus


class PaymentService:
    """
    Business logic for rental payments.

    API views should use this service instead of directly
    changing payment statuses.
    """

    @staticmethod
    @transaction.atomic
    def create_payment(
        *,
        tenancy,
        tenant,
        amount,
        payment_method,
        payment_date=None,
        reference_number="",
        notes="",
    ):
        """
        Create a pending payment for a tenant's tenancy.

        Rules:
        - Tenancy must exist.
        - Tenancy must belong to the supplied tenant.
        - Tenancy must be ACTIVE.
        - Payment amount cannot be negative.
        - Newly created payments always start as PENDING.
        """

        tenancy = Tenancy.objects.select_for_update().select_related(
            "tenant",
        ).get(
            pk=tenancy.pk,
        )

        if tenancy.tenant_id != tenant.id:
            raise ValidationError(
                "This tenancy does not belong to the specified tenant."
            )

        if tenancy.status != TenancyStatus.ACTIVE:
            raise ValidationError(
                "Payments can only be created for active tenancies."
            )

        if amount < 0:
            raise ValidationError(
                "Payment amount cannot be negative."
            )

        return Payment.objects.create(
            tenancy=tenancy,
            tenant=tenant,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            payment_date=payment_date,
            reference_number=reference_number,
            notes=notes,
        )

    @staticmethod
    @transaction.atomic
    def mark_paid(
        *,
        payment_instance,
        payment_date=None,
        reference_number=None,
    ):
        """
        Mark a pending payment as PAID.

        Rules:
        - Only PENDING payments can be marked as PAID.
        """

        payment = Payment.objects.select_for_update().get(
            pk=payment_instance.pk,
        )

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError(
                "Only pending payments can be marked as paid."
            )

        payment.status = PaymentStatus.PAID

        if payment_date is not None:
            payment.payment_date = payment_date

        if reference_number is not None:
            payment.reference_number = reference_number

        payment.save(
            update_fields=[
                "status",
                "payment_date",
                "reference_number",
                "updated_at",
            ]
        )

        return payment

    @staticmethod
    @transaction.atomic
    def mark_failed(
        *,
        payment_instance,
        notes=None,
    ):
        """
        Mark a pending payment as FAILED.

        Rules:
        - Only PENDING payments can be marked as FAILED.
        """

        payment = Payment.objects.select_for_update().get(
            pk=payment_instance.pk,
        )

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError(
                "Only pending payments can be marked as failed."
            )

        payment.status = PaymentStatus.FAILED

        if notes is not None:
            payment.notes = notes

        payment.save(
            update_fields=[
                "status",
                "notes",
                "updated_at",
            ]
        )

        return payment

    @staticmethod
    @transaction.atomic
    def refund_payment(
        *,
        payment_instance,
        notes=None,
    ):
        """
        Refund a paid payment.

        Rules:
        - Only PAID payments can be refunded.
        """

        payment = Payment.objects.select_for_update().get(
            pk=payment_instance.pk,
        )

        if payment.status != PaymentStatus.PAID:
            raise ValidationError(
                "Only paid payments can be refunded."
            )

        payment.status = PaymentStatus.REFUNDED

        if notes is not None:
            payment.notes = notes

        payment.save(
            update_fields=[
                "status",
                "notes",
                "updated_at",
            ]
        )

        return payment

    @staticmethod
    @transaction.atomic
    def cancel_payment(
        *,
        payment_instance,
        notes=None,
    ):
        """
        Cancel a pending payment.

        Rules:
        - Only PENDING payments can be cancelled.
        """

        payment = Payment.objects.select_for_update().get(
            pk=payment_instance.pk,
        )

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError(
                "Only pending payments can be cancelled."
            )

        payment.status = PaymentStatus.CANCELLED

        if notes is not None:
            payment.notes = notes

        payment.save(
            update_fields=[
                "status",
                "notes",
                "updated_at",
            ]
        )

        return payment