from decimal import Decimal

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
        unit_instance.status = status

        unit_instance.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return unit_instance

    @staticmethod
    @transaction.atomic
    def deactivate_unit(
        *,
        unit_instance,
    ):
        unit_instance.status = UnitStatus.INACTIVE

        unit_instance.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return unit_instance