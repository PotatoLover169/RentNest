from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class MaintenancePriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    URGENT = "URGENT", "Urgent"


class MaintenanceStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class MaintenanceRequest(models.Model):
    """
    Represents a maintenance request submitted for a
    property or a specific unit.
    """

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
        limit_choices_to={
            "role": "TENANT",
        },
    )

    property = models.ForeignKey(
        "properties.Property",
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
    )

    unit = models.ForeignKey(
        "properties.Unit",
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
        null=True,
        blank=True,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_maintenance_requests",
        limit_choices_to={
            "role": "PROPERTY_MANAGER",
        },
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=255,
    )

    description = models.TextField()

    priority = models.CharField(
        max_length=20,
        choices=MaintenancePriority.choices,
        default=MaintenancePriority.MEDIUM,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING,
        db_index=True,
    )

    estimated_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
        ],
    )

    actual_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
        ],
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "property",
                    "status",
                ],
                name="maint_prop_status_idx",
            ),
            models.Index(
                fields=[
                    "tenant",
                    "status",
                ],
                name="maint_tenant_status_idx",
            ),
            models.Index(
                fields=[
                    "assigned_to",
                    "status",
                ],
                name="maint_assign_status_idx",
            ),
            models.Index(
                fields=[
                    "priority",
                    "status",
                ],
                name="maint_priority_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.title} - "
            f"{self.property.name}"
        )