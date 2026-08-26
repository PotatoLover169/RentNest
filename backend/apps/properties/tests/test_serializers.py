from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.properties.api.serializers import (
    PropertyDetailSerializer,
    PropertySerializer,
    UnitSerializer,
)
from apps.properties.models import Property, PropertyType, Unit, UnitType


User = get_user_model()


class PropertySerializerTests(TestCase):

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

    def test_property_serializes_correctly(self):
        serializer = PropertySerializer(
            self.property
        )

        data = serializer.data

        self.assertEqual(
            data["id"],
            self.property.id,
        )

        self.assertEqual(
            data["name"],
            "Sunrise Residences",
        )

        self.assertEqual(
            data["manager"],
            self.manager.id,
        )

    def test_manager_is_read_only(self):
        serializer = PropertySerializer(
            instance=self.property,
            data={
                "name": "Updated Residence",
                "manager": 999,
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        serializer.save()

        self.property.refresh_from_db()

        self.assertEqual(
            self.property.manager,
            self.manager,
        )

        self.assertEqual(
            self.property.name,
            "Updated Residence",
        )

    def test_status_is_read_only(self):
        serializer = PropertySerializer(
            instance=self.property,
            data={
                "status": "INACTIVE",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        serializer.save()

        self.property.refresh_from_db()

        self.assertNotEqual(
            self.property.status,
            "INACTIVE",
        )


class UnitSerializerTests(TestCase):

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
        )

        self.unit = Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=1,
            monthly_rent=Decimal("15000.00"),
        )

    def test_unit_serializes_correctly(self):
        serializer = UnitSerializer(
            self.unit
        )

        data = serializer.data

        self.assertEqual(
            data["id"],
            self.unit.id,
        )

        self.assertEqual(
            data["unit_number"],
            "101",
        )

        self.assertEqual(
            data["property"],
            self.property.id,
        )

    def test_property_is_read_only(self):
        serializer = UnitSerializer(
            instance=self.unit,
            data={
                "property": 999,
                "monthly_rent": "17000.00",
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        serializer.save()

        self.unit.refresh_from_db()

        self.assertEqual(
            self.unit.property,
            self.property,
        )

        self.assertEqual(
            self.unit.monthly_rent,
            Decimal("17000.00"),
        )

    def test_negative_rent_is_rejected(self):
        serializer = UnitSerializer(
            data={
                "unit_number": "102",
                "unit_type": UnitType.STUDIO,
                "monthly_rent": "-1000.00",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "monthly_rent",
            serializer.errors,
        )

    def test_negative_bedrooms_are_rejected(self):
        serializer = UnitSerializer(
            data={
                "unit_number": "102",
                "unit_type": UnitType.STUDIO,
                "bedrooms": -1,
                "monthly_rent": "10000.00",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "bedrooms",
            serializer.errors,
        )

    def test_negative_bathrooms_are_rejected(self):
        serializer = UnitSerializer(
            data={
                "unit_number": "102",
                "unit_type": UnitType.STUDIO,
                "bathrooms": -1,
                "monthly_rent": "10000.00",
            }
        )

        self.assertFalse(
            serializer.is_valid()
        )

        self.assertIn(
            "bathrooms",
            serializer.errors,
        )


class PropertyDetailSerializerTests(TestCase):

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
        )

        Unit.objects.create(
            property=self.property,
            unit_number="101",
            unit_type=UnitType.STUDIO,
            monthly_rent=Decimal("12000.00"),
        )

    def test_detail_serializer_includes_units(self):
        serializer = PropertyDetailSerializer(
            self.property
        )

        data = serializer.data

        self.assertIn(
            "units",
            data,
        )

        self.assertEqual(
            len(data["units"]),
            1,
        )

        self.assertEqual(
            data["units"][0]["unit_number"],
            "101",
        )