from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TenancyStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACTIVE = "ACTIVE", "Active"
    ENDED = "ENDED", "Ended"
    CANCELLED = "CANCELLED", "Cancelled"


class Tenancy(models.Model):
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tenancies",
        limit_choices_to={"role": "TENANT"},
    )

    unit = models.ForeignKey(
        "properties.Unit",
        on_delete=models.PROTECT,
        related_name="tenancies",
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    monthly_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    security_deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=TenancyStatus.choices,
        default=TenancyStatus.PENDING,
        db_index=True,
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

        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__isnull=True)
                | Q(end_date__gte=models.F("start_date")),
                name="tenancy_end_date_after_start_date",
            ),
        ]

        indexes = [
            models.Index(
                fields=["tenant", "status"],
                name="tenancy_tenant_status_idx",
            ),
            models.Index(
                fields=["unit", "status"],
                name="tenancy_unit_status_idx",
            ),
            models.Index(
                fields=["start_date", "end_date"],
                name="tenancy_date_range_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.tenant.email} - "
            f"{self.unit.property.name} - "
            f"Unit {self.unit.unit_number}"
        )