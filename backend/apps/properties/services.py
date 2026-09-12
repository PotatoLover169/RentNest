from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Property,
    PropertyStatus,
    Unit,
    UnitStatus,
)


class PropertyService:

    @staticmethod
    @transaction.atomic
    def create_property(
        *,
        manager,
        name,
        property_type,
        address_line,
        city,
        province,
        postal_code="",
        description="",
    ):
        return Property.objects.create(
            manager=manager,
            name=name,
            property_type=property_type,
            address_line=address_line,
            city=city,
            province=province,
            postal_code=postal_code,
            description=description,
        )

    @staticmethod
    @transaction.atomic
    def update_property(
        *,
        property_instance,
        **validated_data,
    ):
        for field, value in validated_data.items():
            setattr(property_instance, field, value)

        property_instance.save()

        return property_instance

    @staticmethod
    @transaction.atomic
    def deactivate_property(
        *,
        property_instance,
    ):
        property_instance.status = PropertyStatus.INACTIVE

        property_instance.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return property_instance


class UnitService:

    @staticmethod
    @transaction.atomic
    def create_unit(
        *,
        property_instance,
        unit_number,
        unit_type,
        monthly_rent,
        bedrooms=0,
        bathrooms=Decimal("1.0"),
        description="",
    ):
        return Unit.objects.create(
            property=property_instance,
            unit_number=unit_number,
            unit_type=unit_type,
            monthly_rent=monthly_rent,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            description=description,
        )

    @staticmethod
    @transaction.atomic
    def update_unit(
        *,
        unit_instance,
        **validated_data,
    ):
        for field, value in validated_data.items():
            setattr(unit_instance, field, value)

        unit_instance.save()

        return unit_instance

    @staticmethod
    @transaction.atomic
    def change_status(
        *,
        unit_instance,
        status,
    ):
        """
        Safely change a unit's operational status.

        Business rules:
        - OCCUPIED is controlled by the tenancy workflow.
        - INACTIVE is controlled by deactivate_unit().
        - AVAILABLE and MAINTENANCE may be changed manually.
        - An occupied unit cannot be manually changed to another status.
        """

        unit = (
            Unit.objects
            .select_for_update()
            .get(pk=unit_instance.pk)
        )

        valid_statuses = {
            choice[0]
            for choice in UnitStatus.choices
        }

        if status not in valid_statuses:
            raise ValidationError(
                "Invalid unit status."
            )

        if status == UnitStatus.INACTIVE:
            raise ValidationError(
                "Use the unit deactivation workflow "
                "to deactivate a unit."
            )

        if status == UnitStatus.OCCUPIED:
            raise ValidationError(
                "A unit becomes occupied through an active tenancy."
            )

        if unit.status == UnitStatus.OCCUPIED:
            raise ValidationError(
                "An occupied unit cannot have its status changed "
                "manually. End the active tenancy first."
            )

        unit.status = status

        unit.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return unit

    @staticmethod
    @transaction.atomic
    def deactivate_unit(
        *,
        unit_instance,
    ):
        unit = (
            Unit.objects
            .select_for_update()
            .get(pk=unit_instance.pk)
        )

        if unit.status == UnitStatus.OCCUPIED:
            raise ValidationError(
                "An occupied unit cannot be deactivated. "
                "End the active tenancy first."
            )

        unit.status = UnitStatus.INACTIVE

        unit.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return unit