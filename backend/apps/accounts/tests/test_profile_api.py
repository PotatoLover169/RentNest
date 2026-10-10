
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole


class ProfileAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
            role=UserRole.TENANT,
        )

        self.client.force_authenticate(user=self.user)

    def test_user_can_update_own_name(self):
        response = self.client.patch(
            "/api/auth/me/",
            {
                "first_name": "Jane",
                "last_name": "Smith",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "Jane")
        self.assertEqual(self.user.last_name, "Smith")
        self.assertEqual(response.data["full_name"], "Jane Smith")

    def test_profile_rejects_blank_first_name(self):
        response = self.client.patch(
            "/api/auth/me/",
            {"first_name": "   "},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")

    def test_email_and_role_are_read_only(self):
        response = self.client.patch(
            "/api/auth/me/",
            {
                "email": "changed@example.com",
                "role": UserRole.ADMIN,
                "first_name": "Jane",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "tenant@example.com",
        )
        self.assertEqual(self.user.role, UserRole.TENANT)
        self.assertEqual(self.user.first_name, "Jane")

    def test_profile_update_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.patch(
            "/api/auth/me/",
            {"first_name": "Jane"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
