from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.accounts.services import AccountService


User = get_user_model()


class AccountServiceTests(TestCase):

    def test_register_user_creates_tenant(self):
        user = AccountService.register_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertIsNotNone(user.pk)
        self.assertEqual(user.email, "tenant@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.role, UserRole.TENANT)
        self.assertTrue(user.is_active)
        self.assertTrue(
            user.check_password("StrongPassword123!")
        )

    def test_register_user_normalizes_email(self):
        user = AccountService.register_user(
            email="Tenant@Example.COM",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(
            user.email,
            "tenant@example.com",
        )
        
    def test_register_user_strips_names(self):
        user = AccountService.register_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="  John  ",
            last_name="  Doe  ",
        )

        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")

    def test_register_user_does_not_allow_public_role_assignment(self):
        user = AccountService.register_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(
            user.role,
            UserRole.TENANT,
        )