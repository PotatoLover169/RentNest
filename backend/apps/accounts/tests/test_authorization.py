from decimal import Decimal

from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.maintenance.models import (
    MaintenanceRequest,
    MaintenanceStatus,
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


class MaintenanceAuthorizationTests(TestCase):
    """
    Authorization and role-isolation tests for Maintenance.

    ADMIN
        - Full maintenance management access.
        - Access is based on UserRole.ADMIN, not is_staff.

    PROPERTY_MANAGER
        - Can access requests for properties they manage.
        - Cannot access another manager's requests.

    TENANT
        - Can access their own requests.
        - Can create requests for actively tenanted units.
        - Can cancel their own pending requests.
        - Cannot manage maintenance workflow.
    """

    @classmethod
    def setUpTestData(cls):
        # =====================================================
        # USERS
        # =====================================================

        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            role=UserRole.ADMIN,
        )
        cls.admin.is_staff = False
        cls.admin.is_superuser = False
        cls.admin.save(
            update_fields=[
                "is_staff",
                "is_superuser",
            ]
        )

        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            role=UserRole.PROPERTY_MANAGER,
        )

        cls.other_manager = User.objects.create_user(
            email="other-manager@example.com",
            password="StrongPassword123!",
            role=UserRole.PROPERTY_MANAGER,
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            role=UserRole.TENANT,
        )

        cls.other_tenant = User.objects.create_user(
            email="other-tenant@example.com",
            password="StrongPassword123!",
            role=UserRole.TENANT,
        )

        # =====================================================
        # PROPERTIES
        # =====================================================

        cls.property = Property.objects.create(
            manager=cls.manager,
            name="Sunrise Apartments",
            property_type=PropertyType.APARTMENT,
            description="Manager property.",
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

        # =====================================================
        # UNITS
        # =====================================================

        cls.unit = Unit.objects.create(
            property=cls.property,
            unit_number="101",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("15000.00"),
            status=UnitStatus.OCCUPIED,
        )

        cls.other_unit = Unit.objects.create(
            property=cls.other_property,
            unit_number="201",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("18000.00"),
            status=UnitStatus.OCCUPIED,
        )

        # =====================================================
        # TENANCIES
        # =====================================================

        cls.tenancy = Tenancy.objects.create(
            tenant=cls.tenant,
            unit=cls.unit,
            start_date="2026-08-01",
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        cls.other_tenancy = Tenancy.objects.create(
            tenant=cls.other_tenant,
            unit=cls.other_unit,
            start_date="2026-08-01",
            monthly_rent=Decimal("18000.00"),
            security_deposit=Decimal("18000.00"),
            status=TenancyStatus.ACTIVE,
        )

        # =====================================================
        # MAINTENANCE REQUESTS
        # =====================================================

        cls.request = MaintenanceRequest.objects.create(
            tenant=cls.tenant,
            property=cls.property,
            unit=cls.unit,
            title="Leaking Faucet",
            description="Kitchen faucet is leaking.",
            status=MaintenanceStatus.PENDING,
        )

        cls.other_request = MaintenanceRequest.objects.create(
            tenant=cls.other_tenant,
            property=cls.other_property,
            unit=cls.other_unit,
            title="Broken Window",
            description="Bedroom window is broken.",
            status=MaintenanceStatus.PENDING,
        )

        # =====================================================
        # URLS
        # =====================================================

        cls.list_url = "/api/maintenance/"
        cls.detail_url = (
            f"/api/maintenance/{cls.request.id}/"
        )
        cls.other_detail_url = (
            f"/api/maintenance/{cls.other_request.id}/"
        )
        cls.start_url = (
            f"/api/maintenance/{cls.request.id}/start/"
        )
        cls.other_start_url = (
            f"/api/maintenance/{cls.other_request.id}/start/"
        )
        cls.complete_url = (
            f"/api/maintenance/{cls.request.id}/complete/"
        )
        cls.cancel_url = (
            f"/api/maintenance/{cls.request.id}/cancel/"
        )
        cls.other_cancel_url = (
            f"/api/maintenance/{cls.other_request.id}/cancel/"
        )

    def setUp(self):
        self.client = APIClient()

    # ========================================================
    # ADMIN
    # ========================================================

    def test_admin_can_list_all_requests(self):
        self.client.force_authenticate(
            user=self.admin,
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
            2,
        )

    def test_admin_can_retrieve_any_request(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            self.other_detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.other_request.id,
        )

    def test_admin_access_uses_role_not_is_staff(self):
        self.admin.is_staff = False
        self.admin.save(
            update_fields=["is_staff"],
        )

        self.client.force_authenticate(
            user=self.admin,
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
            2,
        )

    def test_admin_can_start_any_request(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.other_start_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.other_request.refresh_from_db()

        self.assertEqual(
            self.other_request.status,
            MaintenanceStatus.IN_PROGRESS,
        )

        self.assertEqual(
            self.other_request.assigned_to,
            self.other_manager,
        )

    def test_admin_can_complete_any_request(self):
        self.other_request.status = (
            MaintenanceStatus.IN_PROGRESS
        )
        self.other_request.assigned_to = (
            self.other_manager
        )
        self.other_request.save(
            update_fields=[
                "status",
                "assigned_to",
            ]
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.other_start_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        response = self.client.post(
            (
                f"/api/maintenance/"
                f"{self.other_request.id}/complete/"
            ),
            {
                "actual_cost": "2500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.other_request.refresh_from_db()

        self.assertEqual(
            self.other_request.status,
            MaintenanceStatus.COMPLETED,
        )

    # ========================================================
    # PROPERTY MANAGER
    # ========================================================

    def test_manager_can_list_managed_requests(self):
        self.client.force_authenticate(
            user=self.manager,
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
            self.request.id,
        )

    def test_manager_cannot_retrieve_other_manager_request(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.other_detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_cannot_start_other_manager_request(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.other_start_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_cannot_complete_other_manager_request(self):
        self.other_request.status = (
            MaintenanceStatus.IN_PROGRESS
        )
        self.other_request.assigned_to = (
            self.other_manager
        )
        self.other_request.save(
            update_fields=[
                "status",
                "assigned_to",
            ]
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            (
                f"/api/maintenance/"
                f"{self.other_request.id}/complete/"
            ),
            {
                "actual_cost": "2000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.other_request.refresh_from_db()

        self.assertEqual(
            self.other_request.status,
            MaintenanceStatus.IN_PROGRESS,
        )

    # ========================================================
    # TENANT
    # ========================================================

    def test_tenant_can_list_own_requests(self):
        self.client.force_authenticate(
            user=self.tenant,
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
            self.request.id,
        )

    def test_tenant_cannot_retrieve_other_tenant_request(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.other_detail_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_tenant_cannot_update_request(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.patch(
            self.detail_url,
            {
                "title": "Updated title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_cannot_start_request(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.start_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_cannot_complete_request(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.complete_url,
            {
                "actual_cost": "1000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_can_cancel_own_request(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.cancel_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        self.request.refresh_from_db()

        self.assertEqual(
            self.request.status,
            MaintenanceStatus.CANCELLED,
        )

    def test_tenant_cannot_cancel_other_tenant_request(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.other_cancel_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.other_request.refresh_from_db()

        self.assertEqual(
            self.other_request.status,
            MaintenanceStatus.PENDING,
        )

    # ========================================================
    # CREATE AUTHORIZATION
    # ========================================================

    def test_property_manager_cannot_create_request(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.list_url,
            {
                "unit": self.unit.id,
                "title": "Manager request",
                "description": "Should not be allowed.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_cannot_create_request(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.list_url,
            {
                "unit": self.unit.id,
                "title": "Admin request",
                "description": "Should not be allowed.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_without_active_tenancy_cannot_create_request(
        self,
    ):
        self.client.force_authenticate(
            user=self.other_tenant,
        )

        response = self.client.post(
            self.list_url,
            {
                "unit": self.unit.id,
                "title": "Unauthorized request",
                "description": "No active tenancy.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )