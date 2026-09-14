from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.accounts.models import UserRole
from apps.properties.models import Property, Unit


User = get_user_model()


# ============================================================
# UNIT SERIALIZER
# ============================================================

class UnitSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Unit
        fields = [
            "id",
            "property",
            "unit_number",
            "unit_type",
            "bedrooms",
            "bathrooms",
            "monthly_rent",
            "status",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "property",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_monthly_rent(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Monthly rent cannot be negative."
            )

        return value

    def validate_bedrooms(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Bedrooms cannot be negative."
            )

        return value

    def validate_bathrooms(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Bathrooms cannot be negative."
            )

        return value


# ============================================================
# PROPERTY SERIALIZER
# ============================================================

class PropertySerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    manager_id = serializers.PrimaryKeyRelatedField(
        source="manager",
        queryset=User.objects.filter(
            role=UserRole.PROPERTY_MANAGER,
        ),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Property
        fields = [
            "id",
            "manager",
            "manager_id",
            "name",
            "property_type",
            "description",
            "address_line",
            "city",
            "province",
            "postal_code",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "manager",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate_manager_id(self, value):
        if value.role != UserRole.PROPERTY_MANAGER:
            raise serializers.ValidationError(
                "The assigned user must be a property manager."
            )

        return value


class PropertyDetailSerializer(PropertySerializer):
    units = UnitSerializer(
        many=True,
        read_only=True,
    )

    class Meta(PropertySerializer.Meta):
        fields = PropertySerializer.Meta.fields + [
            "units",
        ]