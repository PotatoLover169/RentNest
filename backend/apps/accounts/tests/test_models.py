from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole


User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(user.email, "tenant@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.role, UserRole.TENANT)

        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_email_is_normalized(self):
        user = User.objects.create_user(
            email="Tenant@Example.COM",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(
            user.email,
            "Tenant@example.com",
        )

    def test_password_is_hashed(self):
        password = "StrongPassword123!"

        user = User.objects.create_user(
            email="tenant@example.com",
            password=password,
            first_name="John",
            last_name="Doe",
        )

        self.assertNotEqual(
            user.password,
            password,
        )

        self.assertTrue(
            user.check_password(password)
        )

    def test_email_is_username_field(self):
        self.assertEqual(
            User.USERNAME_FIELD,
            "email",
        )

    def test_full_name(self):
        user = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.assertEqual(
            user.full_name,
            "John Doe",
        )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPassword123!",
            first_name="Admin",
            last_name="User",
        )

        self.assertEqual(
            user.role,
            UserRole.ADMIN,
        )

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)