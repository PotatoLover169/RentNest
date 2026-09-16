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

    The unit may be selected when creating a request,
    but cannot be changed after the request has been
    created. This preserves the relationship between
    the maintenance request's property and unit.
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

    def validate(self, attrs):
        """
        Prevent changing the unit after creation.

        The unit determines the property associated with
        the maintenance request. Allowing the unit to change
        independently could create an inconsistent
        property/unit relationship.
        """

        if self.instance is not None:
            if "unit" in attrs:
                raise serializers.ValidationError(
                    {
                        "unit": (
                            "The unit cannot be changed after "
                            "a maintenance request has been created."
                        )
                    }
                )

        return attrs

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