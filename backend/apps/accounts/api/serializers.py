from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from ..models import UserRole


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for exposing safe user information.

    Passwords are intentionally excluded.
    """

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "date_joined",
        ]

        read_only_fields = [
            "id",
            "full_name",
            "role",
            "date_joined",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for public user registration.
    """

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User

        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate_email(self, value):
        email = value.strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )

        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {
                    "password_confirm": "Passwords do not match."
                }
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        from ..services import AccountService

        return AccountService.register_user(
            password=password,
            **validated_data,
        )