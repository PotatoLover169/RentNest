from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.maintenance.models import MaintenanceStatus
from apps.maintenance.services import MaintenanceService
from apps.properties.models import (
    Property,
    PropertyType,
    Unit,
    UnitType,
)
from apps.tenancies.models import TenancyStatus
from apps.tenancies.services import TenancyService


class MaintenanceServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            role="PROPERTY_MANAGER",
        )

        cls.other_manager = User.objects.create_user(
            email="other-manager@example.com",
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
            description="Residential property.",
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

    # ============================================================
    # HELPERS
    # ============================================================

    def create_active_tenancy(self):
        return TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date="2026-08-01",
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

    def create_request(self):
        self.create_active_tenancy()

        return MaintenanceService.create_request(
            tenant=self.tenant,
            unit=self.unit,
            title="Leaking faucet",
            description="Kitchen faucet is leaking.",
        )

    # ============================================================
    # CREATE REQUEST
    # ============================================================

    def test_tenant_can_create_request(self):
        request = self.create_request()

        self.assertEqual(
            request.status,
            MaintenanceStatus.PENDING,
        )

        self.assertEqual(
            request.tenant,
            self.tenant,
        )

        self.assertEqual(
            request.property,
            self.property,
        )

        self.assertEqual(
            request.unit,
            self.unit,
        )

    def test_non_tenant_cannot_create_request(self):
        with self.assertRaises(ValidationError):
            MaintenanceService.create_request(
                tenant=self.manager,
                unit=self.unit,
                title="Test",
                description="Test request.",
            )

    def test_tenant_without_active_tenancy_cannot_create_request(
        self,
    ):
        with self.assertRaises(ValidationError):
            MaintenanceService.create_request(
                tenant=self.tenant,
                unit=self.unit,
                title="Test",
                description="Test request.",
            )

    # ============================================================
    # START REQUEST
    # ============================================================

    def test_manager_can_start_request(self):
        request = self.create_request()

        request = MaintenanceService.start_request(
            request_instance=request,
            manager=self.manager,
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.IN_PROGRESS,
        )

        self.assertEqual(
            request.assigned_to,
            self.manager,
        )

    def test_other_manager_cannot_manage_request(self):
        request = self.create_request()

        with self.assertRaises(ValidationError):
            MaintenanceService.start_request(
                request_instance=request,
                manager=self.other_manager,
            )

    # ============================================================
    # COMPLETE REQUEST
    # ============================================================

    def test_manager_can_complete_request(self):
        request = self.create_request()

        request = MaintenanceService.start_request(
            request_instance=request,
            manager=self.manager,
        )

        request = MaintenanceService.complete_request(
            request_instance=request,
            manager=self.manager,
            actual_cost=Decimal("2500.00"),
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.COMPLETED,
        )

        self.assertEqual(
            request.actual_cost,
            Decimal("2500.00"),
        )

        self.assertIsNotNone(
            request.completed_at,
        )

    def test_pending_request_cannot_be_completed_directly(
        self,
    ):
        request = self.create_request()

        with self.assertRaises(ValidationError):
            MaintenanceService.complete_request(
                request_instance=request,
                manager=self.manager,
            )

    def test_completed_request_cannot_be_completed_again(
        self,
    ):
        request = self.create_request()

        request = MaintenanceService.start_request(
            request_instance=request,
            manager=self.manager,
        )

        request = MaintenanceService.complete_request(
            request_instance=request,
            manager=self.manager,
        )

        with self.assertRaises(ValidationError):
            MaintenanceService.complete_request(
                request_instance=request,
                manager=self.manager,
            )

    # ============================================================
    # CANCEL REQUEST
    # ============================================================

    def test_pending_request_can_be_cancelled_by_tenant(
        self,
    ):
        request = self.create_request()

        request = MaintenanceService.cancel_request(
            request_instance=request,
            tenant=self.tenant,
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.CANCELLED,
        )

    def test_in_progress_request_cannot_be_cancelled(
        self,
    ):
        request = self.create_request()

        request = MaintenanceService.start_request(
            request_instance=request,
            manager=self.manager,
        )

        with self.assertRaises(ValidationError):
            MaintenanceService.cancel_request(
                request_instance=request,
                tenant=self.tenant,
            )

    def test_other_tenant_cannot_cancel_request(
        self,
    ):
        from apps.accounts.models import User

        other_tenant = User.objects.create_user(
            email="other-tenant@example.com",
            password="StrongPassword123!",
            role="TENANT",
        )

        request = self.create_request()

        with self.assertRaises(ValidationError):
            MaintenanceService.cancel_request(
                request_instance=request,
                tenant=other_tenant,
            )