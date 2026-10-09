from rest_framework import serializers

from apps.tenancies.models import Tenancy


class TenancySerializer(serializers.ModelSerializer):
    """
    Serializer for rental tenancies.

    Tenant and unit ownership are controlled by the API/service
    layer and are not trusted from arbitrary client input.

    Additional read-only rental information is exposed for the
    tenant portal without allowing the client to modify it.
    """

    tenant = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    unit = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    property_name = serializers.CharField(
        source="unit.property.name",
        read_only=True,
    )

    property_type = serializers.CharField(
        source="unit.property.property_type",
        read_only=True,
    )

    address_line = serializers.CharField(
        source="unit.property.address_line",
        read_only=True,
    )

    city = serializers.CharField(
        source="unit.property.city",
        read_only=True,
    )

    province = serializers.CharField(
        source="unit.property.province",
        read_only=True,
    )

    postal_code = serializers.CharField(
        source="unit.property.postal_code",
        read_only=True,
    )

    unit_number = serializers.CharField(
        source="unit.unit_number",
        read_only=True,
    )

    unit_type = serializers.CharField(
        source="unit.unit_type",
        read_only=True,
    )

    manager_name = serializers.SerializerMethodField()

    manager_email = serializers.EmailField(
        source="unit.property.manager.email",
        read_only=True,
    )

    class Meta:
        model = Tenancy

        fields = [
            "id",
            "tenant",
            "unit",

            "property_name",
            "property_type",
            "address_line",
            "city",
            "province",
            "postal_code",

            "unit_number",
            "unit_type",

            "manager_name",
            "manager_email",

            "start_date",
            "end_date",
            "monthly_rent",
            "security_deposit",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tenant",
            "unit",

            "property_name",
            "property_type",
            "address_line",
            "city",
            "province",
            "postal_code",

            "unit_number",
            "unit_type",

            "manager_name",
            "manager_email",

            "status",
            "created_at",
            "updated_at",
        ]

    def get_manager_name(self, obj):
        manager = obj.unit.property.manager

        full_name = " ".join(
            part
            for part in [
                manager.first_name,
                manager.last_name,
            ]
            if part
        ).strip()

        return full_name or manager.email

    def validate_monthly_rent(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Monthly rent cannot be negative."
            )

        return value

    def validate_security_deposit(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Security deposit cannot be negative."
            )

        return value

    def validate(self, attrs):
        if self.instance and "status" in self.initial_data:
            raise serializers.ValidationError(
                {
                    "status": (
                        "Tenancy status must be changed through "
                        "the appropriate workflow endpoint."
                    )
                }
            )

        start_date = attrs.get(
            "start_date",
            getattr(
                self.instance,
                "start_date",
                None,
            ),
        )

        end_date = attrs.get(
            "end_date",
            getattr(
                self.instance,
                "end_date",
                None,
            ),
        )

        if (
            start_date is not None
            and end_date is not None
            and end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "End date cannot be before "
                        "the tenancy start date."
                    )
                }
            )

        return attrs