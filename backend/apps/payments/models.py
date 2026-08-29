from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class PaymentStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    FAILED = "FAILED", "Failed"
    REFUNDED = "REFUNDED", "Refunded"
    CANCELLED = "CANCELLED", "Cancelled"


class PaymentMethod(models.TextChoices):
    CASH = "CASH", "Cash"
    BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"
    GCASH = "GCASH", "GCash"
    MAYA = "MAYA", "Maya"
    CARD = "CARD", "Card"


class Payment(models.Model):
    """
    A payment associated with a rental tenancy.
    """

    tenancy = models.ForeignKey(
        "tenancies.Tenancy",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        limit_choices_to={"role": "TENANT"},
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        db_index=True,
    )

    payment_date = models.DateField(
        null=True,
        blank=True,
    )

    reference_number = models.CharField(
        max_length=100,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenancy", "status"],
                name="payment_tenancy_status_idx",
            ),
            models.Index(
                fields=["tenant", "status"],
                name="payment_tenant_status_idx",
            ),
            models.Index(
                fields=["payment_date"],
                name="payment_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.tenant.email} - "
            f"{self.amount} - "
            f"{self.status}"
        )