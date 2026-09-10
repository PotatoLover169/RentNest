from rest_framework import serializers

from apps.maintenance.models import MaintenanceRequest
from apps.properties.models import Unit


class MaintenanceRequestSerializer(
    serializers.ModelSerializer
):
    """
    Serializer for maintenance requests.

    Tenant, property, status, assigned manager and
    workflow timestamps are controlled by the
    service/API workflow.
    """

    tenant = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.select_related(
            "property",
        ),
        required=True,
    )

    assigned_to = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = MaintenanceRequest

        fields = [
            "id",
            "tenant",
            "property",
            "unit",
            "assigned_to",
            "title",
            "description",
            "priority",
            "status",
            "estimated_cost",
            "actual_cost",
            "completed_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tenant",
            "property",
            "assigned_to",
            "status",
            "actual_cost",
            "completed_at",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Title cannot be empty."
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Description cannot be empty."
            )

        return value