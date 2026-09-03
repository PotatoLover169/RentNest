from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.notifications.models import (
    Notification,
    NotificationType,
)
from apps.payments.models import (
    PaymentMethod,
    PaymentStatus,
)
from apps.payments.services import PaymentService
from apps.properties.models import (
    Property,
    PropertyStatus,
    PropertyType,
    Unit,
    UnitStatus,
    UnitType,
)
from apps.tenancies.models import (
    Tenancy,
    TenancyStatus,
)


User = get_user_model()


class PaymentNotificationTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        # ========================================================
        # USERS
        # ========================================================

        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Tenant",
            role="TENANT",
        )

        # ========================================================
        # PROPERTY
        # ========================================================

        cls.property = Property.objects.create(
            manager=cls.manager,
            name="RentNest Apartments",
            property_type=PropertyType.APARTMENT,
            description="Test apartment property.",
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        # ========================================================
        # UNIT
        # ========================================================

        cls.unit = Unit.objects.create(
            property=cls.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("15000.00"),
            status=UnitStatus.OCCUPIED,
            description="Test rental unit.",
        )

        # ========================================================
        # TENANCY
        # ========================================================

        cls.tenancy = Tenancy.objects.create(
            tenant=cls.tenant,
            unit=cls.unit,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            monthly_rent=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

    # ========================================================
    # HELPER
    # ========================================================

    def create_payment(self):
        """
        Create a pending payment through the PaymentService.
        """

        return PaymentService.create_payment(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount=Decimal("15000.00"),
            payment_method=PaymentMethod.GCASH,
            payment_date=date(2026, 8, 1),
            reference_number="PAY-TEST-001",
            notes="Test payment.",
        )

    # ========================================================
    # PAYMENT CREATION
    # ========================================================

    def test_payment_creation_creates_notification_for_tenant(self):

        self.create_payment()

        self.assertTrue(
            Notification.objects.filter(
                recipient=self.tenant,
                notification_type=(
                    NotificationType.PAYMENT_CREATED
                ),
            ).exists()
        )

    def test_payment_creation_notification_has_correct_title(self):

        self.create_payment()

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=(
                NotificationType.PAYMENT_CREATED
            ),
        )

        self.assertEqual(
            notification.title,
            "New Payment Created",
        )

    def test_payment_creation_notification_has_correct_message(self):

        self.create_payment()

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=(
                NotificationType.PAYMENT_CREATED
            ),
        )

        self.assertIn(
            "15000.00",
            notification.message,
        )

        self.assertIn(
            "created",
            notification.message.lower(),
        )

    # ========================================================
    # PAYMENT MARKED AS PAID
    # ========================================================

    def test_marking_payment_paid_creates_notification(self):

        payment = self.create_payment()

        PaymentService.mark_paid(
            payment_instance=payment,
            payment_date=date(2026, 8, 15),
            reference_number="PAID-TEST-001",
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=(
                NotificationType.PAYMENT_PAID
            ),
        )

        self.assertEqual(
            notification.title,
            "Payment Marked as Paid",
        )

        self.assertIn(
            "marked as paid",
            notification.message.lower(),
        )

    # ========================================================
    # PAYMENT FAILED
    # ========================================================

    def test_marking_payment_failed_creates_notification(self):

        payment = self.create_payment()

        PaymentService.mark_failed(
            payment_instance=payment,
            notes="Payment failed at gateway.",
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=(
                NotificationType.PAYMENT_FAILED
            ),
        )

        self.assertEqual(
            notification.title,
            "Payment Failed",
        )

        self.assertIn(
            "marked as failed",
            notification.message.lower(),
        )

    # ========================================================
    # PAYMENT REFUNDED
    # ========================================================

    def test_refunding_payment_creates_notification(self):

        payment = self.create_payment()

        PaymentService.mark_paid(
            payment_instance=payment,
            payment_date=date(2026, 8, 15),
            reference_number="PAID-TEST-001",
        )

        PaymentService.refund_payment(
            payment_instance=payment,
            notes="Refund processed.",
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=(
                NotificationType.PAYMENT_REFUNDED
            ),
        )

        self.assertEqual(
            notification.title,
            "Payment Refunded",
        )

        self.assertIn(
            "refunded",
            notification.message.lower(),
        )

    # ========================================================
    # PAYMENT CANCELLED
    # ========================================================

    def test_cancelling_payment_creates_notification(self):

        payment = self.create_payment()

        PaymentService.cancel_payment(
            payment_instance=payment,
            notes="Payment cancelled.",
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=(
                NotificationType.PAYMENT_CANCELLED
            ),
        )

        self.assertEqual(
            notification.title,
            "Payment Cancelled",
        )

        self.assertIn(
            "cancelled",
            notification.message.lower(),
        )