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
from apps.payments.services import PaymentService


class PaymentServiceTests(TestCase):
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

        cls.other_tenant = User.objects.create_user(
            email="other@example.com",
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

    def create_pending_payment(self):
        return Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
        )

    def test_create_payment_creates_pending_payment(self):
        payment = PaymentService.create_payment(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
            payment_date=date(2026, 8, 1),
            reference_number="GCASH-001",
            notes="August rent.",
        )

        self.assertEqual(
            payment.status,
            PaymentStatus.PENDING,
        )

        self.assertEqual(
            payment.tenant,
            self.tenant,
        )

        self.assertEqual(
            payment.tenancy,
            self.tenancy,
        )

    def test_create_payment_rejects_wrong_tenant(self):
        with self.assertRaises(ValidationError):
            PaymentService.create_payment(
                tenancy=self.tenancy,
                tenant=self.other_tenant,
                amount=Decimal("15000.00"),
                payment_method=PaymentMethod.CASH,
            )

    def test_create_payment_rejects_non_active_tenancy(self):
        self.tenancy.status = TenancyStatus.ENDED
        self.tenancy.end_date = date(2026, 8, 15)
        self.tenancy.save()

        with self.assertRaises(ValidationError):
            PaymentService.create_payment(
                tenancy=self.tenancy,
                tenant=self.tenant,
                amount=Decimal("15000.00"),
                payment_method=PaymentMethod.CASH,
            )

    def test_create_payment_rejects_negative_amount(self):
        with self.assertRaises(ValidationError):
            PaymentService.create_payment(
                tenancy=self.tenancy,
                tenant=self.tenant,
                amount=Decimal("-1.00"),
                payment_method=PaymentMethod.CASH,
            )

    def test_mark_paid_changes_pending_to_paid(self):
        payment = self.create_pending_payment()

        updated_payment = PaymentService.mark_paid(
            payment_instance=payment,
            payment_date=date(2026, 8, 1),
            reference_number="GCASH-PAID-001",
        )

        self.assertEqual(
            updated_payment.status,
            PaymentStatus.PAID,
        )

        self.assertEqual(
            updated_payment.payment_date,
            date(2026, 8, 1),
        )

        self.assertEqual(
            updated_payment.reference_number,
            "GCASH-PAID-001",
        )

    def test_mark_paid_rejects_non_pending_payment(self):
        payment = self.create_pending_payment()

        payment.status = PaymentStatus.PAID
        payment.save()

        with self.assertRaises(ValidationError):
            PaymentService.mark_paid(
                payment_instance=payment,
            )

    def test_mark_failed_changes_pending_to_failed(self):
        payment = self.create_pending_payment()

        updated_payment = PaymentService.mark_failed(
            payment_instance=payment,
            notes="Payment gateway rejected transaction.",
        )

        self.assertEqual(
            updated_payment.status,
            PaymentStatus.FAILED,
        )

        self.assertEqual(
            updated_payment.notes,
            "Payment gateway rejected transaction.",
        )

    def test_mark_failed_rejects_non_pending_payment(self):
        payment = self.create_pending_payment()

        payment.status = PaymentStatus.PAID
        payment.save()

        with self.assertRaises(ValidationError):
            PaymentService.mark_failed(
                payment_instance=payment,
            )

    def test_refund_payment_changes_paid_to_refunded(self):
        payment = self.create_pending_payment()

        payment.status = PaymentStatus.PAID
        payment.save()

        updated_payment = PaymentService.refund_payment(
            payment_instance=payment,
            notes="Refund processed.",
        )

        self.assertEqual(
            updated_payment.status,
            PaymentStatus.REFUNDED,
        )

        self.assertEqual(
            updated_payment.notes,
            "Refund processed.",
        )

    def test_refund_payment_rejects_non_paid_payment(self):
        payment = self.create_pending_payment()

        with self.assertRaises(ValidationError):
            PaymentService.refund_payment(
                payment_instance=payment,
            )

    def test_cancel_payment_changes_pending_to_cancelled(self):
        payment = self.create_pending_payment()

        updated_payment = PaymentService.cancel_payment(
            payment_instance=payment,
            notes="Cancelled by manager.",
        )

        self.assertEqual(
            updated_payment.status,
            PaymentStatus.CANCELLED,
        )

        self.assertEqual(
            updated_payment.notes,
            "Cancelled by manager.",
        )

    def test_cancel_payment_rejects_non_pending_payment(self):
        payment = self.create_pending_payment()

        payment.status = PaymentStatus.PAID
        payment.save()

        with self.assertRaises(ValidationError):
            PaymentService.cancel_payment(
                payment_instance=payment,
            )