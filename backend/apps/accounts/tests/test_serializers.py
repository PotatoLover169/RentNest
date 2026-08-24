from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.api.serializers import RegisterSerializer


User = get_user_model()


class RegisterSerializerTests(TestCase):

    def get_valid_data(self):
        return {
            "email": "tenant@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "StrongPassword123!",
            "password_confirm": "StrongPassword123!",
        }

    def test_valid_registration_data(self):
        serializer = RegisterSerializer(
            data=self.get_valid_data()
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_passwords_must_match(self):
        data = self.get_valid_data()

        data["password_confirm"] = "DifferentPassword123!"

        serializer = RegisterSerializer(data=data)

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "password_confirm",
            serializer.errors,
        )

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="Existing",
            last_name="User",
        )

        serializer = RegisterSerializer(
            data=self.get_valid_data()
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "email",
            serializer.errors,
        )

    def test_weak_password_is_rejected(self):
        data = self.get_valid_data()

        data["password"] = "123"
        data["password_confirm"] = "123"

        serializer = RegisterSerializer(data=data)

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "password",
            serializer.errors,
        )

    def test_registration_creates_user(self):
        serializer = RegisterSerializer(
            data=self.get_valid_data()
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        user = serializer.save()

        self.assertEqual(
            user.email,
            "tenant@example.com",
        )

        self.assertEqual(
            user.first_name,
            "John",
        )

        self.assertEqual(
            user.last_name,
            "Doe",
        )

        self.assertTrue(
            user.check_password(
                "StrongPassword123!"
            )
        )