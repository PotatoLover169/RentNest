from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import (
    Notification,
    NotificationType,
)


User = get_user_model()


class NotificationModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
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

        return Notification.objects.create(**data)

    # ========================================================
    # CREATION
    # ========================================================

    def test_create_notification(self):
        notification = self.create_notification()

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

        self.assertFalse(notification.is_read)

        self.assertIsNotNone(notification.created_at)

    # ========================================================
    # READ STATE
    # ========================================================

    def test_notification_is_unread_by_default(self):
        notification = self.create_notification()

        self.assertFalse(notification.is_read)

        self.assertIsNone(notification.read_at)

    def test_notification_can_be_marked_as_read(self):
        notification = self.create_notification()

        notification.is_read = True
        notification.read_at = timezone.now()

        notification.save()

        notification.refresh_from_db()

        self.assertTrue(notification.is_read)

        self.assertIsNotNone(notification.read_at)

    # ========================================================
    # TYPES
    # ========================================================

    def test_notification_type_payment_created(self):
        notification = self.create_notification(
            notification_type=NotificationType.PAYMENT_CREATED,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.PAYMENT_CREATED,
        )

    def test_notification_type_payment_paid(self):
        notification = self.create_notification(
            notification_type=NotificationType.PAYMENT_PAID,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.PAYMENT_PAID,
        )

    def test_notification_type_payment_failed(self):
        notification = self.create_notification(
            notification_type=NotificationType.PAYMENT_FAILED,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.PAYMENT_FAILED,
        )

    def test_notification_type_payment_refunded(self):
        notification = self.create_notification(
            notification_type=NotificationType.PAYMENT_REFUNDED,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.PAYMENT_REFUNDED,
        )

    def test_notification_type_payment_cancelled(self):
        notification = self.create_notification(
            notification_type=NotificationType.PAYMENT_CANCELLED,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.PAYMENT_CANCELLED,
        )

    def test_notification_type_tenancy_created(self):
        notification = self.create_notification(
            notification_type=NotificationType.TENANCY_CREATED,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.TENANCY_CREATED,
        )

    def test_notification_type_tenancy_updated(self):
        notification = self.create_notification(
            notification_type=NotificationType.TENANCY_UPDATED,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.TENANCY_UPDATED,
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def test_notification_string_representation(self):
        notification = self.create_notification(
            notification_type=NotificationType.PAYMENT_PAID,
        )

        self.assertEqual(
            str(notification),
            "PAYMENT_PAID - tenant@example.com",
        )

    # ========================================================
    # ORDERING
    # ========================================================

    def test_notifications_are_ordered_newest_first(self):
        first = self.create_notification(
            title="First Notification",
        )

        second = self.create_notification(
            title="Second Notification",
        )

        notifications = list(Notification.objects.all())

        self.assertEqual(
            notifications[0],
            second,
        )

        self.assertEqual(
            notifications[1],
            first,
        )