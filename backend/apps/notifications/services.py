from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Notification


class NotificationService:
    """
    Business logic for creating and managing notifications.
    """

    @staticmethod
    @transaction.atomic
    def create_notification(
        *,
        recipient,
        notification_type,
        title,
        message,
    ):
        """
        Create a new unread notification.
        """

        if not recipient:
            raise ValidationError(
                "A notification recipient is required."
            )

        if not title or not title.strip():
            raise ValidationError(
                "Notification title cannot be empty."
            )

        if not message or not message.strip():
            raise ValidationError(
                "Notification message cannot be empty."
            )

        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title.strip(),
            message=message.strip(),
        )

    @staticmethod
    @transaction.atomic
    def mark_as_read(*, notification_instance):
        """
        Mark a notification as read.
        """

        notification = Notification.objects.select_for_update().get(
            pk=notification_instance.pk,
        )

        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()

            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                ]
            )

        return notification

    @staticmethod
    @transaction.atomic
    def mark_as_unread(*, notification_instance):
        """
        Mark a notification as unread.
        """

        notification = Notification.objects.select_for_update().get(
            pk=notification_instance.pk,
        )

        if notification.is_read:
            notification.is_read = False
            notification.read_at = None

            notification.save(
                update_fields=[
                    "is_read",
                    "read_at",
                ]
            )

        return notification

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(*, recipient):
        """
        Mark all unread notifications for a recipient as read.

        Returns the number of notifications updated.
        """

        if not recipient:
            raise ValidationError(
                "A notification recipient is required."
            )

        unread_notifications = Notification.objects.filter(
            recipient=recipient,
            is_read=False,
        )

        return unread_notifications.update(
            is_read=True,
            read_at=timezone.now(),
        )

    @staticmethod
    @transaction.atomic
    def delete_notification(*, notification_instance):
        """
        Permanently delete a notification.
        """

        notification = Notification.objects.select_for_update().get(
            pk=notification_instance.pk,
        )

        notification.delete()