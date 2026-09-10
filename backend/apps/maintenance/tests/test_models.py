from decimal import Decimal

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

    def create_request(self, **kwargs):
        """
        Helper for creating a valid maintenance request.
        """

        defaults = {
            "property": self.property,
            "unit": self.unit,
            "tenant": self.tenant,
            "title": "Leaking faucet",
            "description": "The kitchen faucet is leaking.",
        }

        defaults.update(kwargs)

        return MaintenanceRequest.objects.create(
            **defaults
        )

    def test_maintenance_request_can_be_created(self):
        request = self.create_request()

        self.assertEqual(
            request.property,
            self.property,
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
        request = self.create_request(
            title="Broken light",
            description=(
                "The bedroom light is not working."
            ),
        )

        self.assertEqual(
            request.priority,
            MaintenancePriority.MEDIUM,
        )

    def test_default_status_is_pending(self):
        request = self.create_request(
            title="Broken light",
            description=(
                "The bedroom light is not working."
            ),
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.PENDING,
        )

    def test_assigned_manager_can_be_null(self):
        request = self.create_request(
            title="Broken door",
            description=(
                "The front door lock is broken."
            ),
        )

        self.assertIsNone(
            request.assigned_to,
        )

    def test_manager_can_be_assigned(self):
        request = self.create_request(
            title="Broken door",
            description=(
                "The front door lock is broken."
            ),
            assigned_to=self.manager,
        )

        self.assertEqual(
            request.assigned_to,
            self.manager,
        )

    def test_priority_choices_are_supported(self):
        request = self.create_request(
            title="Electrical problem",
            description=(
                "Power outlet is not working."
            ),
            priority=MaintenancePriority.HIGH,
        )

        self.assertEqual(
            request.priority,
            MaintenancePriority.HIGH,
        )

    def test_unit_can_be_null(self):
        request = self.create_request(
            unit=None,
            title="Property issue",
            description=(
                "There is a maintenance issue "
                "in a shared area."
            ),
        )

        self.assertIsNone(
            request.unit,
        )

        self.assertEqual(
            request.property,
            self.property,
        )

    def test_completed_at_can_be_null(self):
        request = self.create_request()

        self.assertIsNone(
            request.completed_at,
        )

    def test_estimated_cost_can_be_null(self):
        request = self.create_request()

        self.assertIsNone(
            request.estimated_cost,
        )

    def test_actual_cost_can_be_null(self):
        request = self.create_request()

        self.assertIsNone(
            request.actual_cost,
        )

    def test_request_can_be_completed(self):
        request = self.create_request(
            title="Broken light",
            description="Bedroom light is broken.",
            status=MaintenanceStatus.COMPLETED,
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.COMPLETED,
        )

    def test_string_representation(self):
        request = self.create_request(
            title="Leaking faucet",
        )

        self.assertEqual(
            str(request),
            "Leaking faucet - Sunrise Apartments",
        )