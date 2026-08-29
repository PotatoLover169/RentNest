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

from apps.payments.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
)


class PaymentModelTests(TestCase):
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
            status=UnitStatus.OCCUPIED,
        )

        cls.tenancy = Tenancy.objects.create(
            tenant=cls.tenant,
            unit=cls.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

    def test_payment_can_be_created(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
            status=PaymentStatus.PAID,
            payment_date=date(2026, 8, 1),
            reference_number="GCASH-20260801-001",
            notes="August rental payment.",
        )

        self.assertEqual(
            payment.tenancy,
            self.tenancy,
        )

        self.assertEqual(
            payment.tenant,
            self.tenant,
        )

        self.assertEqual(
            payment.amount,
            Decimal("15000.00"),
        )

        self.assertEqual(
            payment.payment_method,
            PaymentMethod.GCASH,
        )

        self.assertEqual(
            payment.status,
            PaymentStatus.PAID,
        )

    def test_default_status_is_pending(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.CASH,
        )

        self.assertEqual(
            payment.status,
            PaymentStatus.PENDING,
        )

    def test_payment_date_can_be_null(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.BANK_TRANSFER,
        )

        self.assertIsNone(
            payment.payment_date,
        )

    def test_reference_number_can_be_blank(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.CASH,
        )

        self.assertEqual(
            payment.reference_number,
            "",
        )

    def test_notes_can_be_blank(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.CASH,
        )

        self.assertEqual(
            payment.notes,
            "",
        )

    def test_negative_amount_is_invalid(self):
        payment = Payment(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("-1.00"),
            payment_method=PaymentMethod.CASH,
        )

        with self.assertRaises(ValidationError):
            payment.full_clean()

    def test_zero_amount_is_allowed(self):
        payment = Payment(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("0.00"),
            payment_method=PaymentMethod.CASH,
        )

        payment.full_clean()

        self.assertEqual(
            payment.amount,
            Decimal("0.00"),
        )

    def test_payment_belongs_to_tenancy(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
        )

        self.assertEqual(
            payment.tenancy.pk,
            self.tenancy.pk,
        )

        self.assertEqual(
            payment.tenancy.unit,
            self.unit,
        )

    def test_payment_belongs_to_tenant(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
        )

        self.assertEqual(
            payment.tenant.pk,
            self.tenant.pk,
        )

    def test_payment_string_representation(self):
        payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
        )

        self.assertEqual(
            str(payment),
            "tenant@example.com - 15000.00 - PENDING",
        )