from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.notifications.models import (
    Notification,
    NotificationType,
)


User = get_user_model()


class NotificationAuthorizationTests(TestCase):
    """
    Authorization and ownership tests for the Notifications module.

    Notifications are user-owned resources.

    ADMIN
        - Can access their own notifications.
        - Cannot access another user's notifications.

    PROPERTY_MANAGER
        - Can access their own notifications.
        - Cannot access another user's notifications.

    TENANT
        - Can access their own notifications.
        - Cannot access another user's notifications.

    All roles:
        - Can mark their own notifications as read/unread.
        - Can mark all of their own notifications as read.
        - Can delete their own notifications.
        - Cannot manipulate another user's notifications.

    Notifications are not created through a public API endpoint.
    They are created internally through NotificationService.
    """

    @classmethod
    def setUpTestData(cls):
        # =====================================================
        # USERS
        # =====================================================

        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            first_name="System",
            last_name="Admin",
        )
        cls.admin.role = UserRole.ADMIN
        cls.admin.is_staff = False
        cls.admin.is_superuser = False
        cls.admin.save(
            update_fields=[
                "role",
                "is_staff",
                "is_superuser",
            ]
        )

        cls.property_manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
        )
        cls.property_manager.role = UserRole.PROPERTY_MANAGER
        cls.property_manager.save(
            update_fields=["role"]
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Tenant",
        )
        cls.tenant.role = UserRole.TENANT
        cls.tenant.save(
            update_fields=["role"]
        )

        # =====================================================
        # NOTIFICATIONS
        # =====================================================

        cls.admin_notification = Notification.objects.create(
            recipient=cls.admin,
            notification_type=NotificationType.GENERAL,
            title="Admin Notification",
            message="Notification belonging to the administrator.",
        )

        cls.manager_notification = Notification.objects.create(
            recipient=cls.property_manager,
            notification_type=NotificationType.GENERAL,
            title="Manager Notification",
            message="Notification belonging to the property manager.",
        )

        cls.tenant_notification = Notification.objects.create(
            recipient=cls.tenant,
            notification_type=NotificationType.GENERAL,
            title="Tenant Notification",
            message="Notification belonging to the tenant.",
        )

        cls.admin_payment_notification = Notification.objects.create(
            recipient=cls.admin,
            notification_type=NotificationType.PAYMENT_CREATED,
            title="Admin Payment Notification",
            message="Payment notification for administrator.",
        )

    def setUp(self):
        self.client = APIClient()

    # ========================================================
    # AUTHENTICATION HELPER
    # ========================================================

    def authenticate_as(self, user):
        """
        Authenticate using a JWT access token.
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
    # LIST AUTHORIZATION
    # ========================================================

    def test_admin_can_list_only_own_notifications(self):
        self.authenticate_as(self.admin)

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
            self.admin_notification.id,
            notification_ids,
        )

        self.assertIn(
            self.admin_payment_notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.manager_notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.tenant_notification.id,
            notification_ids,
        )

    def test_property_manager_can_list_only_own_notifications(
        self,
    ):
        self.authenticate_as(self.property_manager)

        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        notification_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.manager_notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.admin_notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.tenant_notification.id,
            notification_ids,
        )

    def test_tenant_can_list_only_own_notifications(self):
        self.authenticate_as(self.tenant)

        response = self.client.get(
            "/api/notifications/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        notification_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.tenant_notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.admin_notification.id,
            notification_ids,
        )

        self.assertNotIn(
            self.manager_notification.id,
            notification_ids,
        )

    # ========================================================
    # RETRIEVE AUTHORIZATION
    # ========================================================

    def test_admin_cannot_retrieve_manager_notification(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            (
                f"/api/notifications/"
                f"{self.manager_notification.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_property_manager_cannot_retrieve_admin_notification(
        self,
    ):
        self.authenticate_as(self.property_manager)

        response = self.client.get(
            (
                f"/api/notifications/"
                f"{self.admin_notification.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_tenant_cannot_retrieve_admin_notification(self):
        self.authenticate_as(self.tenant)

        response = self.client.get(
            (
                f"/api/notifications/"
                f"{self.admin_notification.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ========================================================
    # MARK READ AUTHORIZATION
    # ========================================================

    def test_admin_cannot_mark_manager_notification_as_read(
        self,
    ):
        self.authenticate_as(self.admin)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.manager_notification.id}/mark-read/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.manager_notification.refresh_from_db()

        self.assertFalse(
            self.manager_notification.is_read
        )

    def test_property_manager_cannot_mark_tenant_notification_as_read(
        self,
    ):
        self.authenticate_as(self.property_manager)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.tenant_notification.id}/mark-read/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.tenant_notification.refresh_from_db()

        self.assertFalse(
            self.tenant_notification.is_read
        )

    def test_tenant_cannot_mark_admin_notification_as_read(
        self,
    ):
        self.authenticate_as(self.tenant)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.admin_notification.id}/mark-read/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.admin_notification.refresh_from_db()

        self.assertFalse(
            self.admin_notification.is_read
        )

    # ========================================================
    # MARK UNREAD AUTHORIZATION
    # ========================================================

    def test_admin_cannot_mark_manager_notification_as_unread(
        self,
    ):
        self.manager_notification.is_read = True
        self.manager_notification.save()

        self.authenticate_as(self.admin)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.manager_notification.id}/mark-unread/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.manager_notification.refresh_from_db()

        self.assertTrue(
            self.manager_notification.is_read
        )

    def test_property_manager_cannot_mark_admin_notification_as_unread(
        self,
    ):
        self.admin_notification.is_read = True
        self.admin_notification.save()

        self.authenticate_as(self.property_manager)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.admin_notification.id}/mark-unread/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.admin_notification.refresh_from_db()

        self.assertTrue(
            self.admin_notification.is_read
        )

    def test_tenant_cannot_mark_manager_notification_as_unread(
        self,
    ):
        self.manager_notification.is_read = True
        self.manager_notification.save()

        self.authenticate_as(self.tenant)

        response = self.client.post(
            (
                f"/api/notifications/"
                f"{self.manager_notification.id}/mark-unread/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.manager_notification.refresh_from_db()

        self.assertTrue(
            self.manager_notification.is_read
        )

    # ========================================================
    # DELETE AUTHORIZATION
    # ========================================================

    def test_admin_cannot_delete_manager_notification(self):
        self.authenticate_as(self.admin)

        response = self.client.delete(
            (
                f"/api/notifications/"
                f"{self.manager_notification.id}/delete/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Notification.objects.filter(
                id=self.manager_notification.id,
            ).exists()
        )

    def test_property_manager_cannot_delete_tenant_notification(
        self,
    ):
        self.authenticate_as(self.property_manager)

        response = self.client.delete(
            (
                f"/api/notifications/"
                f"{self.tenant_notification.id}/delete/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Notification.objects.filter(
                id=self.tenant_notification.id,
            ).exists()
        )

    def test_tenant_cannot_delete_admin_notification(self):
        self.authenticate_as(self.tenant)

        response = self.client.delete(
            (
                f"/api/notifications/"
                f"{self.admin_notification.id}/delete/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertTrue(
            Notification.objects.filter(
                id=self.admin_notification.id,
            ).exists()
        )

    # ========================================================
    # MARK ALL READ OWNERSHIP
    # ========================================================

    def test_admin_mark_all_read_only_affects_admin_notifications(
        self,
    ):
        self.admin_notification.is_read = False
        self.admin_notification.read_at = None
        self.admin_notification.save()

        self.admin_payment_notification.is_read = False
        self.admin_payment_notification.read_at = None
        self.admin_payment_notification.save()

        self.manager_notification.is_read = False
        self.manager_notification.read_at = None
        self.manager_notification.save()

        self.tenant_notification.is_read = False
        self.tenant_notification.read_at = None
        self.tenant_notification.save()

        self.authenticate_as(self.admin)

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
            response.data["updated_count"],
            2,
        )

        self.admin_notification.refresh_from_db()
        self.admin_payment_notification.refresh_from_db()
        self.manager_notification.refresh_from_db()
        self.tenant_notification.refresh_from_db()

        self.assertTrue(
            self.admin_notification.is_read
        )

        self.assertTrue(
            self.admin_payment_notification.is_read
        )

        self.assertFalse(
            self.manager_notification.is_read
        )

        self.assertFalse(
            self.tenant_notification.is_read
        )

    def test_property_manager_mark_all_read_only_affects_manager_notifications(
        self,
    ):
        self.manager_notification.is_read = False
        self.manager_notification.read_at = None
        self.manager_notification.save()

        self.admin_notification.is_read = False
        self.admin_notification.read_at = None
        self.admin_notification.save()

        self.tenant_notification.is_read = False
        self.tenant_notification.read_at = None
        self.tenant_notification.save()

        self.authenticate_as(self.property_manager)

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
            response.data["updated_count"],
            1,
        )

        self.manager_notification.refresh_from_db()
        self.admin_notification.refresh_from_db()
        self.tenant_notification.refresh_from_db()

        self.assertTrue(
            self.manager_notification.is_read
        )

        self.assertFalse(
            self.admin_notification.is_read
        )

        self.assertFalse(
            self.tenant_notification.is_read
        )

    def test_tenant_mark_all_read_only_affects_tenant_notifications(
        self,
    ):
        self.tenant_notification.is_read = False
        self.tenant_notification.read_at = None
        self.tenant_notification.save()

        self.admin_notification.is_read = False
        self.admin_notification.read_at = None
        self.admin_notification.save()

        self.manager_notification.is_read = False
        self.manager_notification.read_at = None
        self.manager_notification.save()

        self.authenticate_as(self.tenant)

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
            response.data["updated_count"],
            1,
        )

        self.tenant_notification.refresh_from_db()
        self.admin_notification.refresh_from_db()
        self.manager_notification.refresh_from_db()

        self.assertTrue(
            self.tenant_notification.is_read
        )

        self.assertFalse(
            self.admin_notification.is_read
        )

        self.assertFalse(
            self.manager_notification.is_read
        )