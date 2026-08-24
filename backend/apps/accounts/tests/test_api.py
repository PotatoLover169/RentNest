from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import UserRole


User = get_user_model()


class AuthenticationAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_data = {
            "email": "tenant@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }

        self.user = User.objects.create_user(
            email="existing@example.com",
            password="StrongPassword123!",
            first_name="Existing",
            last_name="User",
        )

    # ========================================================
    # REGISTER
    # ========================================================

    def test_register_user(self):
        response = self.client.post(
            "/api/auth/register/",
            self.user_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            response.data["message"],
            "Account created successfully.",
        )

        self.assertEqual(
            response.data["user"]["email"],
            "tenant@example.com",
        )

        self.assertEqual(
            response.data["user"]["role"],
            UserRole.TENANT,
        )

        self.assertTrue(
            User.objects.filter(
                email="tenant@example.com"
            ).exists()
        )

    def test_register_duplicate_email(self):
        data = self.user_data.copy()

        data["email"] = "existing@example.com"

        response = self.client.post(
            "/api/auth/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "email",
            response.data,
        )

    def test_register_password_mismatch(self):
        data = self.user_data.copy()

        data["password_confirm"] = (
            "DifferentPassword123!"
        )

        response = self.client.post(
            "/api/auth/register/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "password_confirm",
            response.data,
        )

    # ========================================================
    # LOGIN
    # ========================================================

    def test_login_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "existing@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

        self.assertIn(
            "refresh",
            response.data,
        )

    def test_login_invalid_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "email": "existing@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ========================================================
    # ME
    # ========================================================

    def test_me_requires_authentication(self):
        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_me_returns_authenticated_user(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "existing@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get(
            "/api/auth/me/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            "existing@example.com",
        )

        self.assertEqual(
            response.data["role"],
            UserRole.TENANT,
        )

    # ========================================================
    # REFRESH TOKEN
    # ========================================================

    def test_refresh_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "existing@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/api/auth/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "access",
            response.data,
        )

    # ========================================================
    # LOGOUT
    # ========================================================

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(
            "/api/auth/login/",
            {
                "email": "existing@example.com",
                "password": "StrongPassword123!",
            },
            format="json",
        )

        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.post(
            "/api/auth/logout/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_205_RESET_CONTENT,
        )

        refresh_response = self.client.post(
            "/api/auth/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )