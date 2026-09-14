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
    UnitType,
)
from apps.tenancies.models import (
    Tenancy,
    TenancyStatus,
)


User = get_user_model()


class PaymentAuthorizationTests(TestCase):
    """
    Authorization and role-isolation tests for the Payments module.

    Access policy:

    ADMIN
        - Full payment access.
        - Can list, retrieve, create, update, and use
          payment workflow endpoints.
        - Authorization is based on UserRole.ADMIN,
          not is_staff.

    PROPERTY_MANAGER
        - Can access payments belonging to tenancies
          under properties they manage.
        - Can create and update payments within their scope.
        - Can use payment workflow endpoints within their scope.
        - Cannot access another manager's payments.

    TENANT
        - Can view their own payments.
        - Cannot create, update, or manipulate payment status.
        - Cannot access another tenant's payments.
    """

    @classmethod
    def setUpTestData(cls):
        # ============================================================
        # USERS
        # ============================================================

        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            first_name="System",
            last_name="Admin",
        )

        cls.admin.role = UserRole.ADMIN
        cls.admin.is_staff = False
        cls.admin.is_superuser = False
        cls.admin.save(
            update_fields=[
                "role",
                "is_staff",
                "is_superuser",
            ]
        )

        cls.property_manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
        )

        cls.property_manager.role = UserRole.PROPERTY_MANAGER
        cls.property_manager.save(
            update_fields=["role"]
        )

        cls.other_manager = User.objects.create_user(
            email="othermanager@example.com",
            password="StrongPassword123!",
            first_name="Other",
            last_name="Manager",
        )

        cls.other_manager.role = UserRole.PROPERTY_MANAGER
        cls.other_manager.save(
            update_fields=["role"]
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Doe",
        )

        cls.tenant.role = UserRole.TENANT
        cls.tenant.save(
            update_fields=["role"]
        )

        cls.other_tenant = User.objects.create_user(
            email="othertenant@example.com",
            password="StrongPassword123!",
            first_name="Jane",
            last_name="Smith",
        )

        cls.other_tenant.role = UserRole.TENANT
        cls.other_tenant.save(
            update_fields=["role"]
        )

        # ============================================================
        # PROPERTIES
        # ============================================================

        cls.property = Property.objects.create(
            manager=cls.property_manager,
            name="Sunrise Apartments",
            property_type=PropertyType.APARTMENT,
            description="Main rental property.",
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        cls.other_property = Property.objects.create(
            manager=cls.other_manager,
            name="Ocean View Apartments",
            property_type=PropertyType.APARTMENT,
            description="Other manager property.",
            address_line="456 Ocean Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        # ============================================================
        # UNITS
        # ============================================================

        cls.unit = Unit.objects.create(
            property=cls.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms="1.0",
            monthly_rent="15000.00",
            status=UnitStatus.OCCUPIED,
        )

        cls.other_unit = Unit.objects.create(
            property=cls.other_property,
            unit_number="201",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms="1.0",
            monthly_rent="18000.00",
            status=UnitStatus.OCCUPIED,
        )

        # ============================================================
        # TENANCIES
        # ============================================================

        cls.tenancy = Tenancy.objects.create(
            tenant=cls.tenant,
            unit=cls.unit,
            start_date="2026-08-01",
            monthly_rent="15000.00",
            security_deposit="15000.00",
            status=TenancyStatus.ACTIVE,
        )

        cls.other_tenancy = Tenancy.objects.create(
            tenant=cls.other_tenant,
            unit=cls.other_unit,
            start_date="2026-08-01",
            monthly_rent="18000.00",
            security_deposit="18000.00",
            status=TenancyStatus.ACTIVE,
        )

        # ============================================================
        # PAYMENTS
        # ============================================================

        cls.payment = Payment.objects.create(
            tenancy=cls.tenancy,
            tenant=cls.tenant,
            amount="15000.00",
            payment_method=PaymentMethod.GCASH,
            status=PaymentStatus.PENDING,
            reference_number="GCASH-001",
            notes="August rental payment.",
        )

        cls.other_payment = Payment.objects.create(
            tenancy=cls.other_tenancy,
            tenant=cls.other_tenant,
            amount="18000.00",
            payment_method=PaymentMethod.BANK_TRANSFER,
            status=PaymentStatus.PENDING,
            reference_number="BANK-001",
            notes="Other tenant payment.",
        )

        # ============================================================
        # URLS
        # ============================================================

        cls.list_url = "/api/payments/"

        cls.detail_url = (
            f"/api/payments/{cls.payment.id}/"
        )

        cls.other_detail_url = (
            f"/api/payments/{cls.other_payment.id}/"
        )

        cls.mark_paid_url = (
            f"/api/payments/{cls.payment.id}/mark-paid/"
        )

        cls.mark_failed_url = (
            f"/api/payments/{cls.payment.id}/mark-failed/"
        )

        cls.refund_url = (
            f"/api/payments/{cls.payment.id}/refund/"
        )

        cls.cancel_url = (
            f"/api/payments/{cls.payment.id}/cancel/"
        )

    def setUp(self):
        self.client = APIClient()

    # ============================================================
    # HELPERS
    # ============================================================

    def authenticate_as(self, user):
        self.client.force_authenticate(
            user=user,
        )

    # ============================================================
    # ADMIN AUTHORIZATION
    # ============================================================

    def test_admin_can_list_all_payments(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

    def test_admin_can_retrieve_any_payment(self):
        self.authenticate_as(self.admin)

        response = self.client.get(
            self.other_detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.other_payment.id,
        )

    def test_admin_can_update_payment(self):
        self.authenticate_as(self.admin)

        response = self.client.patch(
            self.detail_url,
            {
                "notes": "Updated by administrator.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.notes,
            "Updated by administrator.",
        )

    def test_admin_can_mark_payment_paid(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.mark_paid_url,
            {
                "payment_date": "2026-08-15",
                "reference_number": "ADMIN-PAID-001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.PAID,
        )

    def test_admin_can_mark_payment_failed(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.mark_failed_url,
            {
                "notes": "Marked failed by administrator.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.FAILED,
        )

    def test_admin_can_cancel_payment(self):
        self.authenticate_as(self.admin)

        response = self.client.post(
            self.cancel_url,
            {
                "notes": "Cancelled by administrator.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.CANCELLED,
        )

    def test_admin_access_uses_role_not_is_staff(self):
        self.assertFalse(
            self.admin.is_staff,
        )

        self.assertEqual(
            self.admin.role,
            UserRole.ADMIN,
        )

        self.authenticate_as(self.admin)

        response = self.client.get(
            self.list_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ============================================================
    # PROPERTY MANAGER AUTHORIZATION
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

    def test_property_manager_cannot_retrieve_other_manager_payment(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.get(
            self.other_detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_property_manager_cannot_update_other_manager_payment(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.patch(
            self.other_detail_url,
            {
                "notes": "Unauthorized update.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_property_manager_can_mark_managed_payment_paid(self):
        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            self.mark_paid_url,
            {
                "payment_date": "2026-08-15",
                "reference_number": "MANAGER-PAID-001",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.payment.refresh_from_db()

        self.assertEqual(
            self.payment.status,
            PaymentStatus.PAID,
        )

    def test_property_manager_cannot_mark_other_manager_payment_paid(self):
        other_mark_paid_url = (
            f"/api/payments/"
            f"{self.other_payment.id}/"
            f"mark-paid/"
        )

        self.authenticate_as(
            self.property_manager,
        )

        response = self.client.post(
            other_mark_paid_url,
            {
                "payment_date": "2026-08-15",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ============================================================
    # TENANT READ-ONLY AUTHORIZATION
    # ============================================================

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

    def test_tenant_cannot_retrieve_other_tenant_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.get(
            self.other_detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
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
                "reference_number": "TENANT-001",
                "notes": "Unauthorized tenant payment.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_cannot_update_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "notes": "Unauthorized tenant update.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
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

    def test_tenant_cannot_mark_payment_failed(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.mark_failed_url,
            {
                "notes": "Unauthorized tenant attempt.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_cannot_refund_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.refund_url,
            {
                "notes": "Unauthorized tenant refund.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_cannot_cancel_payment(self):
        self.authenticate_as(
            self.tenant,
        )

        response = self.client.post(
            self.cancel_url,
            {
                "notes": "Unauthorized tenant cancellation.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )