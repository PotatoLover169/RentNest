from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    PAYMENT_CREATED = (
        "PAYMENT_CREATED",
        "Payment Created",
    )
    PAYMENT_PAID = (
        "PAYMENT_PAID",
        "Payment Paid",
    )
    PAYMENT_FAILED = (
        "PAYMENT_FAILED",
        "Payment Failed",
    )
    PAYMENT_REFUNDED = (
        "PAYMENT_REFUNDED",
        "Payment Refunded",
    )
    PAYMENT_CANCELLED = (
        "PAYMENT_CANCELLED",
        "Payment Cancelled",
    )
    TENANCY_CREATED = (
        "TENANCY_CREATED",
        "Tenancy Created",
    )
    TENANCY_UPDATED = (
        "TENANCY_UPDATED",
        "Tenancy Updated",
    )
    GENERAL = (
        "GENERAL",
        "General",
    )


class Notification(models.Model):
    """
    Represents a notification sent to a RentNest user.
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.notification_type} - "
            f"{self.recipient.email}"
        )