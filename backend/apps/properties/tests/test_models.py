from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.properties.models import (
    Property,
    PropertyStatus,
    PropertyType,
    Unit,
    UnitStatus,
    UnitType,
)


User = get_user_model()


class PropertyModelTests(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

        self.property = Property.objects.create(
            manager=self.manager,
            name="Sunrise Residences",
            property_type=PropertyType.APARTMENT,
            description="Modern residential property.",
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
        )

    def test_property_is_created(self):
        self.assertEqual(
            self.property.name,
            "Sunrise Residences",
        )

        self.assertEqual(
            self.property.status,
            PropertyStatus.ACTIVE,
        )

    def test_property_belongs_to_manager(self):
        self.assertEqual(
            self.property.manager,
            self.manager,
        )

    def test_property_string_representation(self):
        self.assertEqual(
            str(self.property),
            "Sunrise Residences",
        )


class UnitModelTests(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

        self.property = Property.objects.create(
            manager=self.manager,
            name="Sunrise Residences",
            property_type=PropertyType.APARTMENT,
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
        )

    def test_unit_is_created(self):
        unit = Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=1,
            monthly_rent=Decimal("15000.00"),
        )

        self.assertEqual(
            unit.unit_number,
            "101",
        )

        self.assertEqual(
            unit.status,
            UnitStatus.AVAILABLE,
        )

    def test_unit_belongs_to_property(self):
        unit = Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.STUDIO,
            monthly_rent=Decimal("12000.00"),
        )

        self.assertEqual(
            unit.property,
            self.property,
        )

    def test_unit_string_representation(self):
        unit = Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            monthly_rent=Decimal("15000.00"),
        )

        self.assertEqual(
            str(unit),
            "Sunrise Residences - Unit 101",
        )

    def test_unit_number_must_be_unique_within_property(self):
        Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.STUDIO,
            monthly_rent=Decimal("12000.00"),
        )

        with self.assertRaises(IntegrityError):
            Unit.objects.create(
                property=self.property,
                unit_number="101",
                unit_type=UnitType.STUDIO,
                monthly_rent=Decimal("12000.00"),
            )

    def test_same_unit_number_allowed_on_different_properties(self):
        second_property = Property.objects.create(
            manager=self.manager,
            name="Ocean View Apartments",
            property_type=PropertyType.APARTMENT,
            address_line="456 Beach Road",
            city="Cebu City",
            province="Cebu",
        )

        Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.STUDIO,
            monthly_rent=Decimal("12000.00"),
        )

        second_unit = Unit.objects.create(
            property=second_property,
            unit_number="101",
            unit_type=UnitType.STUDIO,
            monthly_rent=Decimal("12000.00"),
        )

        self.assertEqual(
            second_unit.unit_number,
            "101",
        )

    def test_negative_rent_is_invalid(self):
        unit = Unit(
            property=self.property,
            unit_number="102",
            unit_type=UnitType.STUDIO,
            monthly_rent=Decimal("-1000.00"),
        )

        with self.assertRaises(ValidationError):
            unit.full_clean()