from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.maintenance.models import MaintenanceRequest, MaintenanceStatus
from apps.notifications.models import Notification
from apps.payments.models import Payment, PaymentMethod, PaymentStatus
from apps.properties.models import (
    Property,
    PropertyStatus,
    PropertyType,
    Unit,
    UnitStatus,
    UnitType,
)
from apps.tenancies.models import Tenancy, TenancyStatus


class DashboardSummaryAPITests(APITestCase):
    def setUp(self):
        self.url = reverse("dashboard:summary")

        self.admin = User.objects.create_user(
            email="admin-dashboard@example.com",
            first_name="Admin",
            last_name="User",
            password="TestPass123!",
            role=UserRole.ADMIN,
        )

        self.manager = User.objects.create_user(
            email="manager-dashboard@example.com",
            first_name="Property",
            last_name="Manager",
            password="TestPass123!",
            role=UserRole.PROPERTY_MANAGER,
        )

        self.other_manager = User.objects.create_user(
            email="other-manager-dashboard@example.com",
            first_name="Other",
            last_name="Manager",
            password="TestPass123!",
            role=UserRole.PROPERTY_MANAGER,
        )

        self.tenant = User.objects.create_user(
            email="tenant-dashboard@example.com",
            first_name="Test",
            last_name="Tenant",
            password="TestPass123!",
            role=UserRole.TENANT,
        )

        self.other_tenant = User.objects.create_user(
            email="other-tenant-dashboard@example.com",
            first_name="Other",
            last_name="Tenant",
            password="TestPass123!",
            role=UserRole.TENANT,
        )

        self.manager_property = self.create_property(
            manager=self.manager,
            name="Manager Property",
        )
        self.other_property = self.create_property(
            manager=self.other_manager,
            name="Other Manager Property",
        )

        self.manager_unit = self.create_unit(
            property_obj=self.manager_property,
            unit_number="M-101",
        )
        self.other_unit = self.create_unit(
            property_obj=self.other_property,
            unit_number="O-101",
        )

        self.manager_tenancy = self.create_tenancy(
            tenant=self.tenant,
            unit=self.manager_unit,
        )
        self.other_tenancy = self.create_tenancy(
            tenant=self.other_tenant,
            unit=self.other_unit,
        )

        self.manager_payment = self.create_payment(
            tenancy=self.manager_tenancy,
            tenant=self.tenant,
        )
        self.other_payment = self.create_payment(
            tenancy=self.other_tenancy,
            tenant=self.other_tenant,
        )

        self.manager_maintenance = self.create_maintenance_request(
            tenant=self.tenant,
            property_obj=self.manager_property,
            unit=self.manager_unit,
            title="Leaking kitchen faucet",
        )
        self.other_maintenance = self.create_maintenance_request(
            tenant=self.other_tenant,
            property_obj=self.other_property,
            unit=self.other_unit,
            title="Broken window",
        )

        self.tenant_notification = Notification.objects.create(
            recipient=self.tenant,
            title="Payment reminder",
            message="Your rental payment is pending.",
        )
        self.other_notification = Notification.objects.create(
            recipient=self.other_tenant,
            title="Private notification",
            message="This belongs to another tenant.",
        )

    @staticmethod
    def create_property(manager, name):
        return Property.objects.create(
            manager=manager,
            name=name,
            property_type=PropertyType.APARTMENT,
            description="Test rental property",
            address_line="123 Test Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

    @staticmethod
    def create_unit(property_obj, unit_number):
        return Unit.objects.create(
            property=property_obj,
            unit_number=unit_number,
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("12000.00"),
            status=UnitStatus.OCCUPIED,
        )

    @staticmethod
    def create_tenancy(tenant, unit):
        return Tenancy.objects.create(
            tenant=tenant,
            unit=unit,
            start_date=date(2026, 1, 1),
            monthly_rent=Decimal("12000.00"),
            security_deposit=Decimal("12000.00"),
            status=TenancyStatus.ACTIVE,
        )

    @staticmethod
    def create_payment(tenancy, tenant):
        return Payment.objects.create(
            tenancy=tenancy,
            tenant=tenant,
            amount=Decimal("12000.00"),
            payment_method=PaymentMethod.CASH,
            status=PaymentStatus.PENDING,
        )

    @staticmethod
    def create_maintenance_request(
        tenant,
        property_obj,
        unit,
        title,
    ):
        return MaintenanceRequest.objects.create(
            tenant=tenant,
            property=property_obj,
            unit=unit,
            title=title,
            description="Test maintenance request",
            status=MaintenanceStatus.PENDING,
        )

    def test_dashboard_requires_authentication(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_admin_receives_platform_wide_counts(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], UserRole.ADMIN)

        summary = response.data["summary"]

        self.assertEqual(summary["properties"], 2)
        self.assertEqual(summary["units"], 2)
        self.assertEqual(summary["active_tenancies"], 2)
        self.assertEqual(summary["pending_payments"], 2)
        self.assertEqual(summary["open_maintenance_requests"], 2)
        self.assertEqual(summary["unread_notifications"], 0)
        self.assertEqual(summary["total_users"], 5)
        self.assertEqual(summary["total_tenancies"], 2)
        self.assertEqual(summary["total_payments"], 2)
        self.assertEqual(summary["total_maintenance_requests"], 2)

    def test_manager_only_receives_their_property_activity(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        summary = response.data["summary"]

        self.assertEqual(summary["properties"], 1)
        self.assertEqual(summary["units"], 1)
        self.assertEqual(summary["active_tenancies"], 1)
        self.assertEqual(summary["pending_payments"], 1)
        self.assertEqual(summary["open_maintenance_requests"], 1)

        self.assertNotIn("total_users", summary)
        self.assertNotIn("total_payments", summary)

    def test_tenant_only_receives_their_own_activity(self):
        self.client.force_authenticate(user=self.tenant)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        summary = response.data["summary"]

        self.assertEqual(summary["active_tenancies"], 1)
        self.assertEqual(summary["pending_payments"], 1)
        self.assertEqual(summary["open_maintenance_requests"], 1)
        self.assertEqual(summary["unread_notifications"], 1)

        self.assertNotIn("properties", summary)
        self.assertNotIn("units", summary)
        self.assertNotIn("total_users", summary)

    def test_recent_notifications_belong_to_signed_in_user(self):
        self.client.force_authenticate(user=self.tenant)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notifications = response.data["recent_notifications"]
        notification_ids = {
            notification["id"] for notification in notifications
        }

        self.assertIn(self.tenant_notification.id, notification_ids)
        self.assertNotIn(self.other_notification.id, notification_ids)

    def test_manager_cannot_see_other_managers_counts(self):
        self.client.force_authenticate(user=self.other_manager)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        summary = response.data["summary"]

        self.assertEqual(summary["properties"], 1)
        self.assertEqual(summary["units"], 1)
        self.assertEqual(summary["active_tenancies"], 1)
        self.assertEqual(summary["pending_payments"], 1)
        self.assertEqual(summary["open_maintenance_requests"], 1)
