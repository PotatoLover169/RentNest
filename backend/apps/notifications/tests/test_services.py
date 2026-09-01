from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.notifications.models import (
    Notification,
    NotificationType,
)
from apps.notifications.services import NotificationService


User = get_user_model()


class NotificationServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
            first_name="Jane",
            last_name="Doe",
        )

    def create_notification(self, **overrides):
        data = {
            "recipient": self.user,
            "notification_type": NotificationType.GENERAL,
            "title": "Test Notification",
            "message": "This is a test notification.",
        }

        data.update(overrides)

        return NotificationService.create_notification(
            **data,
        )

    # ========================================================
    # CREATE NOTIFICATION
    # ========================================================

    def test_create_notification(self):
        notification = self.create_notification()

        self.assertIsInstance(
            notification,
            Notification,
        )

        self.assertEqual(
            notification.recipient,
            self.user,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.GENERAL,
        )

        self.assertEqual(
            notification.title,
            "Test Notification",
        )

        self.assertEqual(
            notification.message,
            "This is a test notification.",
        )

        self.assertFalse(
            notification.is_read,
        )

        self.assertIsNone(
            notification.read_at,
        )

    def test_create_notification_strips_title_and_message(self):
        notification = self.create_notification(
            title="  Payment Update  ",
            message="  Your payment was received.  ",
        )

        self.assertEqual(
            notification.title,
            "Payment Update",
        )

        self.assertEqual(
            notification.message,
            "Your payment was received.",
        )

    def test_create_notification_requires_recipient(self):
        with self.assertRaises(ValidationError):
            NotificationService.create_notification(
                recipient=None,
                notification_type=NotificationType.GENERAL,
                title="Test",
                message="Test message",
            )

    def test_create_notification_rejects_empty_title(self):
        with self.assertRaises(ValidationError):
            self.create_notification(
                title="",
            )

    def test_create_notification_rejects_whitespace_title(self):
        with self.assertRaises(ValidationError):
            self.create_notification(
                title="   ",
            )

    def test_create_notification_rejects_empty_message(self):
        with self.assertRaises(ValidationError):
            self.create_notification(
                message="",
            )

    def test_create_notification_rejects_whitespace_message(self):
        with self.assertRaises(ValidationError):
            self.create_notification(
                message="   ",
            )

    # ========================================================
    # MARK AS READ
    # ========================================================

    def test_mark_notification_as_read(self):
        notification = self.create_notification()

        updated_notification = (
            NotificationService.mark_as_read(
                notification_instance=notification,
            )
        )

        updated_notification.refresh_from_db()

        self.assertTrue(
            updated_notification.is_read,
        )

        self.assertIsNotNone(
            updated_notification.read_at,
        )

    def test_mark_as_read_is_idempotent(self):
        notification = self.create_notification()

        NotificationService.mark_as_read(
            notification_instance=notification,
        )

        updated_notification = (
            NotificationService.mark_as_read(
                notification_instance=notification,
            )
        )

        self.assertTrue(
            updated_notification.is_read,
        )

    # ========================================================
    # MARK AS UNREAD
    # ========================================================

    def test_mark_notification_as_unread(self):
        notification = self.create_notification()

        NotificationService.mark_as_read(
            notification_instance=notification,
        )

        updated_notification = (
            NotificationService.mark_as_unread(
                notification_instance=notification,
            )
        )

        updated_notification.refresh_from_db()

        self.assertFalse(
            updated_notification.is_read,
        )

        self.assertIsNone(
            updated_notification.read_at,
        )

    def test_mark_as_unread_is_idempotent(self):
        notification = self.create_notification()

        updated_notification = (
            NotificationService.mark_as_unread(
                notification_instance=notification,
            )
        )

        self.assertFalse(
            updated_notification.is_read,
        )

    # ========================================================
    # MARK ALL AS READ
    # ========================================================

    def test_mark_all_as_read(self):
        first = self.create_notification(
            title="First",
        )

        second = self.create_notification(
            title="Second",
        )

        other = self.create_notification(
            recipient=self.other_user,
            title="Other",
        )

        updated_count = NotificationService.mark_all_as_read(
            recipient=self.user,
        )

        self.assertEqual(
            updated_count,
            2,
        )

        first.refresh_from_db()
        second.refresh_from_db()
        other.refresh_from_db()

        self.assertTrue(first.is_read)
        self.assertTrue(second.is_read)
        self.assertFalse(other.is_read)

    def test_mark_all_as_read_requires_recipient(self):
        with self.assertRaises(ValidationError):
            NotificationService.mark_all_as_read(
                recipient=None,
            )

    # ========================================================
    # DELETE
    # ========================================================

    def test_delete_notification(self):
        notification = self.create_notification()

        notification_id = notification.id

        NotificationService.delete_notification(
            notification_instance=notification,
        )

        self.assertFalse(
            Notification.objects.filter(
                id=notification_id,
            ).exists()
        )