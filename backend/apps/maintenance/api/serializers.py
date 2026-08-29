from rest_framework import serializers

from apps.maintenance.models import MaintenanceRequest


class MaintenanceRequestSerializer(
    serializers.ModelSerializer
):
    """
    Serializer for maintenance requests.

    Tenant, unit, status, assigned manager and timestamps
    are controlled by the service/API workflow.
    """

    tenant = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    unit = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    assigned_to = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = MaintenanceRequest

        fields = [
            "id",
            "unit",
            "tenant",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "resolution_notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "unit",
            "tenant",
            "status",
            "assigned_to",
            "resolution_notes",
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