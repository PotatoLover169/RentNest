from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import User
from apps.properties.models import (
    Property,
    PropertyType,
    Unit,
    UnitStatus,
    UnitType,
)

from apps.tenancies.models import (
    Tenancy,
    TenancyStatus,
)
from apps.tenancies.services import TenancyService


class TenancyServiceTests(TestCase):

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

        cls.second_tenant = User.objects.create_user(
            email="tenant2@example.com",
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
            status=UnitStatus.AVAILABLE,
        )

    def test_create_pending_tenancy(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        self.assertEqual(
            tenancy.status,
            TenancyStatus.PENDING,
        )

        self.unit.refresh_from_db()

        self.assertEqual(
            self.unit.status,
            UnitStatus.AVAILABLE,
        )

    def test_create_active_tenancy_makes_unit_occupied(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ACTIVE,
        )

        self.unit.refresh_from_db()

        self.assertEqual(
            self.unit.status,
            UnitStatus.OCCUPIED,
        )

    def test_second_active_tenancy_for_same_unit_is_rejected(self):
        TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        with self.assertRaises(ValidationError):
            TenancyService.create_tenancy(
                tenant=self.second_tenant,
                unit=self.unit,
                start_date=date(2026, 9, 1),
                monthly_rent=Decimal("15000.00"),
                security_deposit=Decimal("15000.00"),
                status=TenancyStatus.ACTIVE,
            )

        self.assertEqual(
            Tenancy.objects.filter(
                unit=self.unit,
                status=TenancyStatus.ACTIVE,
            ).count(),
            1,
        )

    def test_activate_pending_tenancy_makes_unit_occupied(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        self.assertEqual(
            tenancy.status,
            TenancyStatus.PENDING,
        )

        tenancy = TenancyService.activate_tenancy(
            tenancy_instance=tenancy,
        )

        tenancy.refresh_from_db()
        self.unit.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ACTIVE,
        )

        self.assertEqual(
            self.unit.status,
            UnitStatus.OCCUPIED,
        )

    def test_activate_tenancy_is_rejected_when_unit_has_active_tenancy(self):
        TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        second_unit_tenancy = Tenancy.objects.create(
            tenant=self.second_tenant,
            unit=self.unit,
            start_date=date(2026, 9, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.PENDING,
        )

        with self.assertRaises(ValidationError):
            TenancyService.activate_tenancy(
                tenancy_instance=second_unit_tenancy,
            )

        second_unit_tenancy.refresh_from_db()

        self.assertEqual(
            second_unit_tenancy.status,
            TenancyStatus.PENDING,
        )

        self.assertEqual(
            Tenancy.objects.filter(
                unit=self.unit,
                status=TenancyStatus.ACTIVE,
            ).count(),
            1,
        )

    def test_end_active_tenancy_makes_unit_available(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        tenancy = TenancyService.end_tenancy(
            tenancy_instance=tenancy,
            end_date=date(2026, 8, 31),
        )

        tenancy.refresh_from_db()
        self.unit.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ENDED,
        )

        self.assertEqual(
            tenancy.end_date,
            date(2026, 8, 31),
        )

        self.assertEqual(
            self.unit.status,
            UnitStatus.AVAILABLE,
        )

    def test_pending_tenancy_cannot_be_ended(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        with self.assertRaises(ValidationError):
            TenancyService.end_tenancy(
                tenancy_instance=tenancy,
                end_date=date(2026, 8, 31),
            )

        tenancy.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.PENDING,
        )