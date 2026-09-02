from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.notifications.models import (
    Notification,
    NotificationType,
)


User = get_user_model()


class NotificationAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@example.com",
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

        cls.notification = Notification.objects.create(
            recipient=cls.user,
            notification_type=NotificationType.GENERAL,
            title="First Notification",
            message="This notification belongs to the user.",
        )

        cls.second_notification = Notification.objects.create(
            recipient=cls.user,
            notification_type=NotificationType.PAYMENT_CREATED,
            title="Payment Notification",
            message="Your payment has been received.",
        )

        cls.other_notification = Notification.objects.create(
            recipient=cls.other_user,
            notification_type=NotificationType.GENERAL,
            title="Other User Notification",
            message="This notification belongs to another user.",
        )

    def setUp(self):
        self.client = APIClient()

    def authenticate_as(self, user):
        """
        Authenticate the API client using a JWT access token.
        """

        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": user.email,
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            login_response.status_code,
            status.HTTP_200_OK,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {login_response.data['access']}"
            )
        )

    # ========================================================
    # LIST NOTIFICATIONS
    # ========================================================

    def test_list_notifications_requires_authentication(self):
        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_list_own_notifications(self):
        self.authenticate_as(self.user)

        response = self.client.get(
            "/api/notifications/"
        )

        print("LIST RESPONSE:", response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

        notification_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            self.notification.id,
            notification_ids,
        )

        self.assertIn(
            self.second_notification.id,
            notification_ids,
        )

    def test_user_cannot_see_other_user_notifications(self):
        self.authenticate_as(self.user)

        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertNotIn(
            self.other_notification.id,
            notification_ids,
        )

    # ========================================================
    # RETRIEVE NOTIFICATION
    # ========================================================

    def test_retrieve_notification_requires_authentication(self):
        response = self.client.get(
            f"/api/notifications/{self.notification.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_list_own_notifications(self):
        self.authenticate_as(self.user)

        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        notification_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.notification.id,
            notification_ids,
        )

        self.assertIn(
            self.second_notification.id,
            notification_ids,
        )


    def test_user_cannot_see_other_user_notifications(self):
        self.authenticate_as(self.user)

        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notification_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertNotIn(
            self.other_notification.id,
            notification_ids,
        )

    # ========================================================
    # MARK AS READ
    # ========================================================

    def test_mark_notification_as_read_requires_authentication(self):
        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/mark-read/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_mark_own_notification_as_read(self):
        self.authenticate_as(self.user)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/mark-read/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            response.data["is_read"]
        )

        self.assertIsNotNone(
            response.data["read_at"]
        )

        self.notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

    def test_user_cannot_mark_other_user_notification_as_read(self):
        self.authenticate_as(self.user)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.other_notification.id}/mark-read/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ========================================================
    # MARK AS UNREAD
    # ========================================================

    def test_mark_notification_as_unread_requires_authentication(self):
        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/mark-unread/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_mark_notification_as_unread(self):
        self.notification.is_read = True
        self.notification.save()

        self.authenticate_as(self.user)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.notification.id}/mark-unread/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["is_read"]
        )

        self.assertIsNone(
            response.data["read_at"]
        )

        self.notification.refresh_from_db()

        self.assertFalse(
            self.notification.is_read
        )

    def test_user_cannot_mark_other_notification_as_unread(self):
        self.other_notification.is_read = True
        self.other_notification.save()

        self.authenticate_as(self.user)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.other_notification.id}/mark-unread/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ========================================================
    # MARK ALL AS READ
    # ========================================================

    def test_mark_all_notifications_as_read_requires_authentication(self):
        response = self.client.post(
            "/api/notifications/mark-all-read/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_mark_all_own_notifications_as_read(self):
        self.notification.is_read = False
        self.notification.read_at = None
        self.notification.save()

        self.second_notification.is_read = False
        self.second_notification.read_at = None
        self.second_notification.save()

        self.other_notification.is_read = False
        self.other_notification.read_at = None
        self.other_notification.save()

        self.authenticate_as(self.user)

        response = self.client.post(
            "/api/notifications/mark-all-read/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["message"],
            "Notifications marked as read.",
        )

        self.assertEqual(
            response.data["updated_count"],
            2,
        )

        self.notification.refresh_from_db()
        self.second_notification.refresh_from_db()
        self.other_notification.refresh_from_db()

        self.assertTrue(
            self.notification.is_read
        )

        self.assertTrue(
            self.second_notification.is_read
        )

        self.assertFalse(
            self.other_notification.is_read
        )

    # ========================================================
    # DELETE NOTIFICATION
    # ========================================================

    def test_delete_notification_requires_authentication(self):
        response = self.client.delete(
            (
                f"/api/notifications/"
                f"{self.notification.id}/delete/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_delete_own_notification(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type=NotificationType.GENERAL,
            title="Delete Me",
            message="This notification will be deleted.",
        )

        self.authenticate_as(self.user)

        response = self.client.delete(
            (
                f"/api/notifications/"
                f"{notification.id}/delete/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Notification.objects.filter(
                id=notification.id,
            ).exists()
        )

    def test_user_cannot_delete_other_user_notification(self):
        self.authenticate_as(self.user)

        response = self.client.delete(
            (
                f"/api/notifications/"
                f"{self.other_notification.id}/delete/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Notification.objects.filter(
                id=self.other_notification.id,
            ).exists()
        )