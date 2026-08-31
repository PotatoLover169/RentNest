from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.payments.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
)
from apps.properties.models import (
    Property,
    PropertyStatus,
    PropertyType,
    Unit,
    UnitStatus,
)
from apps.tenancies.models import (
    Tenancy,
    TenancyStatus,
)


User = get_user_model()


class PaymentAPITests(TestCase):
    """
    API tests for the Payments module.

    Covers:
    - Authentication
    - Payment creation
    - Payment listing
    - Payment detail access
    - Payment updates
    - Protected status changes
    - Mark paid
    - Mark failed
    - Refund
    - Cancel
    - Ownership isolation
    """

    def setUp(self):
        self.client = APIClient()

        # ========================================================
        # USERS
        # ========================================================

        self.property_manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
        )

        self.property_manager.role = UserRole.PROPERTY_MANAGER
        self.property_manager.save(
            update_fields=["role"]
        )

        self.other_manager = User.objects.create_user(
            email="othermanager@example.com",
            password="StrongPassword123!",
            first_name="Other",
            last_name="Manager",
        )

        self.other_manager.role = UserRole.PROPERTY_MANAGER
        self.other_manager.save(
            update_fields=["role"]
        )

        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        self.tenant.role = UserRole.TENANT
        self.tenant.save(
            update_fields=["role"]
        )

        self.other_tenant = User.objects.create_user(
            email="othertenant@example.com",
            password="StrongPassword123!",
            first_name="Jane",
            last_name="Smith",
        )

        self.other_tenant.role = UserRole.TENANT
        self.other_tenant.save(
            update_fields=["role"]
        )

        # ========================================================
        # PROPERTY
        # ========================================================

        self.property = Property.objects.create(
            manager=self.property_manager,
            name="Sunrise Apartments",
            property_type=PropertyType.APARTMENT,
            description="Main rental property.",
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        self.other_property = Property.objects.create(
            manager=self.other_manager,
            name="Ocean View Apartments",
            property_type=PropertyType.APARTMENT,
            description="Other manager property.",
            address_line="456 Ocean Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        # ========================================================
        # UNITS
        # ========================================================

        self.unit = Unit.objects.create(
            property=self.property,
            unit_number="101",
            monthly_rent="15000.00",
            status=UnitStatus.OCCUPIED,
        )

        self.other_unit = Unit.objects.create(
            property=self.other_property,
            unit_number="201",
            monthly_rent="15000.00",
            status=UnitStatus.OCCUPIED,
        )

        # ========================================================
        # TENANCIES
        # ========================================================

        self.tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent="15000.00",
            security_deposit="15000.00",
            status=TenancyStatus.ACTIVE,
        )

        self.other_tenancy = Tenancy.objects.create(
            tenant=self.other_tenant,
            unit=self.other_unit,
            start_date=date(2026, 8, 1),
            monthly_rent="15000.00",
            security_deposit="15000.00",
            status=TenancyStatus.ACTIVE,
        )

        # ========================================================
        # PAYMENTS
        # ========================================================

        self.payment = Payment.objects.create(
            tenancy=self.tenancy,
            tenant=self.tenant,
            amount="15000.00",
            payment_method=PaymentMethod.GCASH,
            status=PaymentStatus.PENDING,
            reference_number="GCASH-001",
            notes="August rental payment.",
        )

        self.other_payment = Payment.objects.create(
            tenancy=self.other_tenancy,
            tenant=self.other_tenant,
            amount="18000.00",
            payment_method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            reference_number="BANK-001",
            notes="Other tenant payment.",
        )

        # ========================================================
        # URLS
        # ========================================================

        self.list_url = "/api/payments/"

        self.detail_url = (
            f"/api/payments/{self.payment.id}/"
        )

        self.mark_paid_url = (
            f"/api/payments/{self.payment.id}/mark-paid/"
        )

        self.mark_failed_url = (
            f"/api/payments/{self.payment.id}/mark-failed/"
        )

        self.refund_url = (
            f"/api/payments/{self.payment.id}/refund/"
        )

        self.cancel_url = (
            f"/api/payments/{self.payment.id}/cancel/"
        )

    # ============================================================
    # HELPERS
    # ============================================================

    def authenticate_as(self, user):
        self.client.force_authenticate(
            user=user,
        )

    def refresh_payment(self):
        self.payment.refresh_from_db()

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    def test_list_requires_authentication(self):
        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_create_requires_authentication(self):
        response = self.client.post(
            self.list_url,
            {
                "tenancy": self.tenancy.id,
                "tenant": self.tenant.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.GCASH,
                "reference_number": "GCASH-NEW",
                "notes": "New payment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ============================================================
    # LIST
    # ============================================================

    def test_property_manager_can_list_managed_payments(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            self.payment.id,
        )

    def test_tenant_can_list_own_payments(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            self.payment.id,
        )

    def test_property_manager_cannot_see_other_manager_payments(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        payment_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.payment.id,
            payment_ids,
        )

        self.assertNotIn(
            self.other_payment.id,
            payment_ids,
        )

    def test_tenant_cannot_see_other_tenant_payments(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        payment_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(
            self.payment.id,
            payment_ids,
        )

        self.assertNotIn(
            self.other_payment.id,
            payment_ids,
        )

    # ============================================================
    # CREATE
    # ============================================================

    def test_property_manager_can_create_payment(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.list_url,
            {
                "tenancy": self.tenancy.id,
                "tenant": self.tenant.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.GCASH,
                "reference_number": "GCASH-NEW",
                "notes": "August payment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Payment.objects.filter(
                tenancy=self.tenancy,
                tenant=self.tenant,
                reference_number="GCASH-NEW",
            ).exists()
        )

    def test_tenant_cannot_create_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.list_url,
            {
                "tenancy": self.tenancy.id,
                "tenant": self.tenant.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.GCASH,
                "reference_number": "GCASH-TENANT",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_create_payment_requires_tenancy(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.list_url,
            {
                "tenant": self.tenant.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "tenancy",
            response.data,
        )

    def test_create_payment_requires_tenant(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.list_url,
            {
                "tenancy": self.tenancy.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "tenant",
            response.data,
        )

    def test_create_payment_rejects_wrong_tenant_for_tenancy(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.list_url,
            {
                "tenancy": self.tenancy.id,
                "tenant": self.other_tenant.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.CASH,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "tenant",
            response.data,
        )

    def test_electronic_payment_requires_reference_number(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.list_url,
            {
                "tenancy": self.tenancy.id,
                "tenant": self.tenant.id,
                "amount": "15000.00",
                "payment_method": PaymentMethod.GCASH,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "reference_number",
            response.data,
        )

    # ============================================================
    # DETAIL
    # ============================================================

    def test_property_manager_can_retrieve_payment(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.get(
            self.detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.payment.id,
        )

        self.assertEqual(
            response.data["amount"],
            "15000.00",
        )

    def test_tenant_can_retrieve_own_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.get(
            self.detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.payment.id,
        )

    def test_other_manager_cannot_retrieve_payment(self):
        self.authenticate_as(
            self.other_manager,
        )

        response = self.client.get(
            self.detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_other_tenant_cannot_retrieve_payment(self):
        self.authenticate_as(
            self.other_tenant,
        )

        response = self.client.get(
            self.detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ============================================================
    # UPDATE
    # ============================================================

    def test_property_manager_can_update_payment_notes(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "notes": "Updated payment note.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.notes,
            "Updated payment note.",
        )

    def test_tenant_cannot_update_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "notes": "Tenant attempted update.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_status_cannot_be_changed_through_patch(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "status": PaymentStatus.PAID,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.PENDING,
        )

    def test_tenant_cannot_be_changed_through_patch(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "tenant": self.other_tenant.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.tenant_id,
            self.tenant.id,
        )

    def test_tenancy_cannot_be_changed_through_patch(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "tenancy": self.other_tenancy.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.tenancy_id,
            self.tenancy.id,
        )

    # ============================================================
    # MARK PAID
    # ============================================================

    def test_property_manager_can_mark_payment_paid(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.mark_paid_url,
            {
                "payment_date": "2026-08-15",
                "reference_number": "GCASH-PAID-001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.PAID,
        )

        self.assertEqual(
            self.payment.payment_date,
            date(2026, 8, 15),
        )

        self.assertEqual(
            self.payment.reference_number,
            "GCASH-PAID-001",
        )

    def test_tenant_cannot_mark_payment_paid(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.mark_paid_url,
            {
                "payment_date": "2026-08-15",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_mark_paid_rejects_invalid_date(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.mark_paid_url,
            {
                "payment_date": "not-a-date",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "payment_date",
            response.data,
        )

    # ============================================================
    # MARK FAILED
    # ============================================================

    def test_property_manager_can_mark_payment_failed(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.mark_failed_url,
            {
                "notes": "Payment failed at gateway.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.FAILED,
        )

        self.assertEqual(
            self.payment.notes,
            "Payment failed at gateway.",
        )

    def test_tenant_cannot_mark_payment_failed(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.mark_failed_url,
            {
                "notes": "Tenant attempt.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ============================================================
    # REFUND
    # ============================================================

    def test_property_manager_can_refund_paid_payment(self):
        self.payment.status = PaymentStatus.PAID
        self.payment.payment_date = date(2026, 8, 15)
        self.payment.save()

        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.refund_url,
            {
                "notes": "Refund processed.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.REFUNDED,
        )

        self.assertEqual(
            self.payment.notes,
            "Refund processed.",
        )

    def test_tenant_cannot_refund_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.refund_url,
            {
                "notes": "Tenant attempt.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ============================================================
    # CANCEL
    # ============================================================

    def test_property_manager_can_cancel_pending_payment(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.cancel_url,
            {
                "notes": "Payment cancelled.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.refresh_payment()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.CANCELLED,
        )

        self.assertEqual(
            self.payment.notes,
            "Payment cancelled.",
        )

    def test_tenant_cannot_cancel_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.cancel_url,
            {
                "notes": "Tenant attempt.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )