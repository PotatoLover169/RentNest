from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.properties.models import (
    PropertyStatus,
    PropertyType,
    UnitStatus,
    UnitType,
)
from apps.properties.services import (
    PropertyService,
    UnitService,
)


User = get_user_model()


class PropertyServiceTests(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

    def test_create_property(self):
        property_instance = PropertyService.create_property(
            manager=self.manager,
            name="Sunrise Residences",
            property_type=PropertyType.APARTMENT,
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            description="Modern apartment building.",
        )

        self.assertEqual(
            property_instance.name,
            "Sunrise Residences",
        )

        self.assertEqual(
            property_instance.manager,
            self.manager,
        )

        self.assertEqual(
            property_instance.status,
            PropertyStatus.ACTIVE,
        )

    def test_update_property(self):
        property_instance = PropertyService.create_property(
            manager=self.manager,
            name="Old Name",
            property_type=PropertyType.APARTMENT,
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
        )

        updated_property = PropertyService.update_property(
            property_instance=property_instance,
            name="New Name",
            city="Mandaue City",
        )

        self.assertEqual(
            updated_property.name,
            "New Name",
        )

        self.assertEqual(
            updated_property.city,
            "Mandaue City",
        )

    def test_deactivate_property(self):
        property_instance = PropertyService.create_property(
            manager=self.manager,
            name="Sunrise Residences",
            property_type=PropertyType.APARTMENT,
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
        )

        PropertyService.deactivate_property(
            property_instance=property_instance,
        )

        property_instance.refresh_from_db()

        self.assertEqual(
            property_instance.status,
            PropertyStatus.INACTIVE,
        )


class UnitServiceTests(TestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

        self.property = PropertyService.create_property(
            manager=self.manager,
            name="Sunrise Residences",
            property_type=PropertyType.APARTMENT,
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
        )

    def test_create_unit(self):
        unit = UnitService.create_unit(
            property_instance=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            monthly_rent=Decimal("15000.00"),
            bedrooms=1,
            bathrooms=1,
        )

        self.assertEqual(
            unit.unit_number,
            "101",
        )

        self.assertEqual(
            unit.monthly_rent,
            Decimal("15000.00"),
        )

        self.assertEqual(
            unit.status,
            UnitStatus.AVAILABLE,
        )

    def test_update_unit(self):
        unit = UnitService.create_unit(
            property_instance=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            monthly_rent=Decimal("15000.00"),
        )

        updated_unit = UnitService.update_unit(
            unit_instance=unit,
            monthly_rent=Decimal("17000.00"),
            description="Recently renovated.",
        )

        self.assertEqual(
            updated_unit.monthly_rent,
            Decimal("17000.00"),
        )

        self.assertEqual(
            updated_unit.description,
            "Recently renovated.",
        )

    def test_change_unit_status(self):
        unit = UnitService.create_unit(
            property_instance=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            monthly_rent=Decimal("15000.00"),
        )

        UnitService.change_status(
            unit_instance=unit,
            status=UnitStatus.OCCUPIED,
        )

        unit.refresh_from_db()

        self.assertEqual(
            unit.status,
            UnitStatus.OCCUPIED,
        )

    def test_deactivate_unit(self):
        unit = UnitService.create_unit(
            property_instance=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            monthly_rent=Decimal("15000.00"),
        )

        UnitService.deactivate_unit(
            unit_instance=unit,
        )

        unit.refresh_from_db()

        self.assertEqual(
            unit.status,
            UnitStatus.INACTIVE,
        )