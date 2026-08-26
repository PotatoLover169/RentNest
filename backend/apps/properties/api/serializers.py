from rest_framework import serializers

from apps.properties.models import Property, Unit


class UnitSerializer(serializers.ModelSerializer):
    """
    Serializer for rental units.

    Property ownership is intentionally not writable through
    the API. The service layer determines the property.
    """

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


class PropertySerializer(serializers.ModelSerializer):
    """
    Main serializer for rental properties.

    The manager is never accepted from client input.
    Ownership is assigned by the authenticated backend user.
    """

    manager = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Property

        fields = [
            "id",
            "manager",
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

class PropertyDetailSerializer(PropertySerializer):
    """
    Detailed property representation including its units.
    """

    units = UnitSerializer(
        many=True,
        read_only=True,
    )

    class Meta(PropertySerializer.Meta):
        fields = PropertySerializer.Meta.fields + [
            "units",
        ]