from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class MaintenancePriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    URGENT = "URGENT", "Urgent"


class MaintenanceStatus(models.TextChoices):
    OPEN = "OPEN", "Open"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"
    CANCELLED = "CANCELLED", "Cancelled"


class MaintenanceRequest(models.Model):
    """
    A maintenance issue reported for a rental unit.
    """

    unit = models.ForeignKey(
        "properties.Unit",
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
    )

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
        limit_choices_to={"role": "TENANT"},
    )

    title = models.CharField(
        max_length=200,
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
        default=MaintenanceStatus.OPEN,
        db_index=True,
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_maintenance_requests",
        limit_choices_to={
            "role": "PROPERTY_MANAGER",
        },
    )

    resolution_notes = models.TextField(
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
            fields=["priority", "status"],
            name="maint_priority_status_idx",
        ),
        models.Index(
            fields=["tenant", "status"],
            name="maint_tenant_status_idx",
        ),
    ]

    def __str__(self):
        return (
            f"{self.title} - "
            f"Unit {self.unit.unit_number}"
        )