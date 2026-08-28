from rest_framework import serializers

from apps.tenancies.models import Tenancy


class TenancySerializer(serializers.ModelSerializer):
    """
    Serializer for rental tenancies.

    Tenant and unit ownership are controlled by the API/service
    layer and are not trusted from arbitrary client input.
    """

    tenant = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    unit = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Tenancy

        fields = [
            "id",
            "tenant",
            "unit",
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

    def validate_security_deposit(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Security deposit cannot be negative."
            )

        return value

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )

        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None),
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