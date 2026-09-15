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
    PropertyType,
    Unit,
    UnitType,
)
from apps.tenancies.models import TenancyStatus
from apps.tenancies.services import TenancyService


class MaintenanceAuthorizationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            role=UserRole.ADMIN,
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

        # ------------------------------------------------------
        # PROPERTY MANAGER 1
        # ------------------------------------------------------

        cls.property = Property.objects.create(
            manager=cls.manager,
            name="Sunrise Apartments",
            property_type=PropertyType.APARTMENT,
            description="Residential property.",
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

        # ------------------------------------------------------
        # PROPERTY MANAGER 2
        # ------------------------------------------------------

        cls.other_property = Property.objects.create(
            manager=cls.other_manager,
            name="Ocean View Residences",
            property_type=PropertyType.APARTMENT,
            description="Another residential property.",
            address_line="456 Ocean Avenue",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
        )

        cls.other_unit = Unit.objects.create(
            property=cls.other_property,
            unit_number="201",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("18000.00"),
        )

    def setUp(self):
        self.client = APIClient()

    # ==========================================================
    # HELPERS
    # ==========================================================

    def create_active_tenancy(
        self,
        tenant,
        unit,
    ):
        return TenancyService.create_tenancy(
            tenant=tenant,
            unit=unit,
            start_date="2026-08-01",
            monthly_rent=unit.monthly_rent,
            security_deposit=unit.monthly_rent,
            status=TenancyStatus.ACTIVE,
        )

    def create_request(
        self,
        tenant,
        unit,
        property,
    ):
        self.create_active_tenancy(
            tenant=tenant,
            unit=unit,
        )

        return MaintenanceRequest.objects.create(
            tenant=tenant,
            property=property,
            unit=unit,
            title="Leaking faucet",
            description="Kitchen faucet is leaking.",
            status=MaintenanceStatus.PENDING,
        )

    def list_url(self):
        return "/api/maintenance/"

    def detail_url(self, pk):
        return f"/api/maintenance/{pk}/"

    def start_url(self, pk):
        return f"/api/maintenance/{pk}/start/"

    def complete_url(self, pk):
        return f"/api/maintenance/{pk}/complete/"

    def cancel_url(self, pk):
        return f"/api/maintenance/{pk}/cancel/"

    # ==========================================================
    # LIST AUTHORIZATION
    # ==========================================================

    def test_admin_can_list_all_requests(self):
        manager_request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        other_request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            self.list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        returned_ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            manager_request.id,
            returned_ids,
        )

        self.assertIn(
            other_request.id,
            returned_ids,
        )

    def test_property_manager_can_only_list_managed_requests(self):
        managed_request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        other_request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.list_url(),
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
            managed_request.id,
        )

        self.assertNotEqual(
            response.data["results"][0]["id"],
            other_request.id,
        )

    def test_tenant_can_only_list_own_requests(self):
        own_request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        other_request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.list_url(),
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
            own_request.id,
        )

        self.assertNotEqual(
            response.data["results"][0]["id"],
            other_request.id,
        )

    # ==========================================================
    # DETAIL RETRIEVE AUTHORIZATION
    # ==========================================================

    def test_admin_can_retrieve_any_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            request.id,
        )

    def test_property_manager_can_retrieve_managed_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_property_manager_cannot_retrieve_other_manager_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_tenant_can_retrieve_own_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_tenant_cannot_retrieve_other_tenant_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # CREATE AUTHORIZATION
    # ==========================================================

    def test_admin_cannot_create_request(self):
        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.list_url(),
            {
                "unit": self.unit.id,
                "title": "Broken faucet",
                "description": "Kitchen faucet is leaking.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_property_manager_cannot_create_request(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.list_url(),
            {
                "unit": self.unit.id,
                "title": "Broken faucet",
                "description": "Kitchen faucet is leaking.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # UPDATE AUTHORIZATION
    # ==========================================================

    def test_admin_can_update_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.patch(
            self.detail_url(request.id),
            {
                "title": "Updated maintenance title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Updated maintenance title",
        )

    def test_property_manager_can_update_managed_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.detail_url(request.id),
            {
                "title": "Manager updated title",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.title,
            "Manager updated title",
        )

    def test_property_manager_cannot_update_other_manager_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.detail_url(request.id),
            {
                "title": "Unauthorized update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_tenant_cannot_update_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.patch(
            self.detail_url(request.id),
            {
                "title": "Unauthorized tenant update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # START AUTHORIZATION
    # ==========================================================

    def test_admin_can_start_any_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.IN_PROGRESS,
        )

        self.assertEqual(
            request.assigned_to,
            self.other_manager,
        )

    def test_property_manager_can_start_managed_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.IN_PROGRESS,
        )

        self.assertEqual(
            request.assigned_to,
            self.manager,
        )

    def test_property_manager_cannot_start_other_manager_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_tenant_cannot_start_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # COMPLETE AUTHORIZATION
    # ==========================================================

    def test_admin_can_complete_any_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        request.status = MaintenanceStatus.IN_PROGRESS
        request.save(update_fields=["status"])

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.complete_url(request.id),
            {
                "actual_cost": "2500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.COMPLETED,
        )

        self.assertEqual(
            request.actual_cost,
            Decimal("2500.00"),
        )

    def test_property_manager_can_complete_managed_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        request.status = MaintenanceStatus.IN_PROGRESS
        request.save(update_fields=["status"])

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.complete_url(request.id),
            {
                "actual_cost": "1500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.COMPLETED,
        )

    def test_property_manager_cannot_complete_other_manager_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        request.status = MaintenanceStatus.IN_PROGRESS
        request.save(update_fields=["status"])

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.complete_url(request.id),
            {
                "actual_cost": "1500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_tenant_cannot_complete_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        request.status = MaintenanceStatus.IN_PROGRESS
        request.save(update_fields=["status"])

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.complete_url(request.id),
            {
                "actual_cost": "1500.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # CANCEL AUTHORIZATION
    # ==========================================================

    def test_admin_cannot_cancel_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.cancel_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_property_manager_cannot_cancel_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.cancel_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_can_cancel_own_pending_request(self):
        request = self.create_request(
            tenant=self.tenant,
            unit=self.unit,
            property=self.property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.cancel_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.CANCELLED,
        )

    def test_tenant_cannot_cancel_other_tenant_request(self):
        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.cancel_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # ROLE SECURITY
    # ==========================================================

    def test_staff_property_manager_does_not_get_admin_access(self):
        staff_manager = User.objects.create_user(
            email="staff-manager@example.com",
            password="StrongPassword123!",
            role=UserRole.PROPERTY_MANAGER,
            is_staff=True,
        )

        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=staff_manager,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_staff_tenant_does_not_get_admin_access(self):
        staff_tenant = User.objects.create_user(
            email="staff-tenant@example.com",
            password="StrongPassword123!",
            role=UserRole.TENANT,
            is_staff=True,
        )

        request = self.create_request(
            tenant=self.other_tenant,
            unit=self.other_unit,
            property=self.other_property,
        )

        self.client.force_authenticate(
            user=staff_tenant,
        )

        response = self.client.get(
            self.detail_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
