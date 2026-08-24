from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.accounts.models import UserRole
from apps.accounts.permissions import (
    IsAdmin,
    IsAdminOrPropertyManager,
    IsPropertyManager,
    IsTenant,
)


User = get_user_model()


class PermissionTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
        )

        self.property_manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role=UserRole.PROPERTY_MANAGER,
        )

        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="Tenant",
            last_name="User",
            role=UserRole.TENANT,
        )

    def create_request(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def test_admin_permission(self):
        permission = IsAdmin()

        self.assertTrue(
            permission.has_permission(
                self.create_request(self.admin),
                None,
            )
        )

        self.assertFalse(
            permission.has_permission(
                self.create_request(self.tenant),
                None,
            )
        )

    def test_property_manager_permission(self):
        permission = IsPropertyManager()

        self.assertTrue(
            permission.has_permission(
                self.create_request(self.property_manager),
                None,
            )
        )

        self.assertFalse(
            permission.has_permission(
                self.create_request(self.tenant),
                None,
            )
        )

    def test_tenant_permission(self):
        permission = IsTenant()

        self.assertTrue(
            permission.has_permission(
                self.create_request(self.tenant),
                None,
            )
        )

        self.assertFalse(
            permission.has_permission(
                self.create_request(self.admin),
                None,
            )
        )

    def test_admin_or_property_manager_permission(self):
        permission = IsAdminOrPropertyManager()

        self.assertTrue(
            permission.has_permission(
                self.create_request(self.admin),
                None,
            )
        )

        self.assertTrue(
            permission.has_permission(
                self.create_request(self.property_manager),
                None,
            )
        )

        self.assertFalse(
            permission.has_permission(
                self.create_request(self.tenant),
                None,
            )
        )

    def test_unauthenticated_user_is_denied(self):
        request = self.factory.get("/")

        request.user = type(
            "AnonymousUser",
            (),
            {
                "is_authenticated": False,
            },
        )()

        permissions = [
            IsAdmin(),
            IsPropertyManager(),
            IsTenant(),
            IsAdminOrPropertyManager(),
        ]

        for permission in permissions:
            self.assertFalse(
                permission.has_permission(
                    request,
                    None,
                )
            )