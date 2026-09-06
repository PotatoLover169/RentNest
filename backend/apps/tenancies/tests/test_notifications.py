from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.accounts.models import User
from apps.notifications.models import (
    Notification,
    NotificationType,
)
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
from apps.tenancies.services import TenancyService


class TenancyNotificationTests(TestCase):
    """
    Tests for notification creation during important
    tenancy lifecycle events.
    """

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
            status=PropertyStatus.ACTIVE,
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

    # ============================================================
    # HELPERS
    # ============================================================

    def create_pending_tenancy(self):
        return Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 9, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.PENDING,
        )

    # ============================================================
    # TENANCY CREATED
    # ============================================================

    def test_creating_tenancy_creates_notification(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 9, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=NotificationType.TENANCY_CREATED,
        )

        self.assertIsNotNone(notification)

        self.assertEqual(
            notification.recipient,
            self.tenant,
        )

        self.assertEqual(
            notification.notification_type,
            NotificationType.TENANCY_CREATED,
        )

        self.assertTrue(
            tenancy.pk,
        )

    def test_tenancy_created_notification_is_unread(self):
        TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 9, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=NotificationType.TENANCY_CREATED,
        )

        self.assertFalse(
            notification.is_read,
        )

        self.assertIsNone(
            notification.read_at,
        )

    # ============================================================
    # TENANCY ACTIVATED
    # ============================================================

    def test_activating_tenancy_creates_notification(self):
        tenancy = self.create_pending_tenancy()

        activated_tenancy = TenancyService.activate_tenancy(
            tenancy_instance=tenancy,
        )

        notification = Notification.objects.get(
            recipient=self.tenant,
            notification_type=NotificationType.TENANCY_UPDATED,
        )

        self.assertIsNotNone(notification)

        self.assertEqual(
            activated_tenancy.status,
            TenancyStatus.ACTIVE,
        )

        self.assertEqual(
            notification.recipient,
            self.tenant,
        )

    # ============================================================
    # TENANCY ENDED
    # ============================================================

    def test_ending_tenancy_creates_notification(self):
        tenancy = self.create_pending_tenancy()

        TenancyService.activate_tenancy(
            tenancy_instance=tenancy,
        )

        ended_tenancy = TenancyService.end_tenancy(
            tenancy_instance=tenancy,
            end_date=date(2026, 9, 30),
        )

        notifications = Notification.objects.filter(
            recipient=self.tenant,
        )

        self.assertTrue(
            notifications.filter(
                notification_type=NotificationType.TENANCY_UPDATED,
            ).exists()
        )

        self.assertEqual(
            ended_tenancy.status,
            TenancyStatus.ENDED,
        )

    def test_tenancy_lifecycle_creates_multiple_notifications(self):
        tenancy = TenancyService.create_tenancy(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 9, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
        )

        TenancyService.activate_tenancy(
            tenancy_instance=tenancy,
        )

        TenancyService.end_tenancy(
            tenancy_instance=tenancy,
            end_date=date(2026, 9, 30),
        )

        notifications = Notification.objects.filter(
            recipient=self.tenant,
        )

        self.assertEqual(
            notifications.count(),
            3,
        )

        self.assertTrue(
            notifications.filter(
                notification_type=NotificationType.TENANCY_CREATED,
            ).exists()
        )

        self.assertEqual(
            notifications.filter(
                notification_type=NotificationType.TENANCY_UPDATED,
            ).count(),
            2,
        )