from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.properties.models import (
    Property,
    PropertyType,
    Unit,
    UnitType,
)

from apps.maintenance.models import (
    MaintenancePriority,
    MaintenanceRequest,
    MaintenanceStatus,
)


class MaintenanceModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            role="PROPERTY_MANAGER",
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            role="TENANT",
        )

        cls.property = Property.objects.create(
            manager=cls.manager,
            name="Sunrise Apartments",
            property_type=PropertyType.APARTMENT,
            description="A residential apartment property.",
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
        )

        cls.unit = Unit.objects.create(
            property=cls.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("15000.00"),
        )

    def test_maintenance_request_can_be_created(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Leaking faucet",
            description="The kitchen faucet is leaking.",
        )

        self.assertEqual(
            request.unit,
            self.unit,
        )

        self.assertEqual(
            request.tenant,
            self.tenant,
        )

        self.assertEqual(
            request.title,
            "Leaking faucet",
        )

    def test_default_priority_is_medium(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Broken light",
            description="The bedroom light is not working.",
        )

        self.assertEqual(
            request.priority,
            MaintenancePriority.MEDIUM,
        )

    def test_default_status_is_open(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Broken light",
            description="The bedroom light is not working.",
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.OPEN,
        )

    def test_assigned_manager_can_be_null(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Broken door",
            description="The front door lock is broken.",
        )

        self.assertIsNone(
            request.assigned_to,
        )

    def test_manager_can_be_assigned(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Broken door",
            description="The front door lock is broken.",
            assigned_to=self.manager,
        )

        self.assertEqual(
            request.assigned_to,
            self.manager,
        )

    def test_priority_choices_are_supported(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Electrical problem",
            description="Power outlet is not working.",
            priority=MaintenancePriority.HIGH,
        )

        self.assertEqual(
            request.priority,
            MaintenancePriority.HIGH,
        )

    def test_resolution_notes_can_be_blank(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Small issue",
            description="Minor maintenance issue.",
        )

        self.assertEqual(
            request.resolution_notes,
            "",
        )

    def test_string_representation(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Leaking faucet",
            description="Kitchen faucet is leaking.",
        )

        self.assertEqual(
            str(request),
            "Leaking faucet - Unit 101",
        )

    def test_request_can_be_resolved(self):
        request = MaintenanceRequest.objects.create(
            unit=self.unit,
            tenant=self.tenant,
            title="Broken light",
            description="Bedroom light is broken.",
            status=MaintenanceStatus.RESOLVED,
            resolution_notes="Bulb replaced.",
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.RESOLVED,
        )

        self.assertEqual(
            request.resolution_notes,
            "Bulb replaced.",
        )