from datetime import date
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

    def test_create_tenancy_through_service(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        self.assertIsNotNone(tenancy.pk)
        self.assertEqual(
            tenancy.tenant,
            self.tenant,
        )
        self.assertEqual(
            tenancy.unit,
            self.unit,
        )
        self.assertEqual(
            tenancy.status,
            TenancyStatus.PENDING,
        )

    def test_multiple_active_tenancies_for_same_unit_are_rejected(self):
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
                tenant=self.tenant,
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

    def test_ended_tenancy_does_not_block_new_active_tenancy(self):
        Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            monthly_rent=Decimal("14000.00"),
            security_deposit=Decimal("14000.00"),
            status=TenancyStatus.ENDED,
        )

        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 1, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ACTIVE,
        )