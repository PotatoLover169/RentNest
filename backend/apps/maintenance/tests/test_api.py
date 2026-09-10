from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import User
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


class MaintenanceAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            role="PROPERTY_MANAGER",
        )

        cls.other_manager = User.objects.create_user(
            email="other-manager@example.com",
            password="StrongPassword123!",
            role="PROPERTY_MANAGER",
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            role="TENANT",
        )

        cls.other_tenant = User.objects.create_user(
            email="other-tenant@example.com",
            password="StrongPassword123!",
            role="TENANT",
        )

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

    def setUp(self):
        self.client = APIClient()

    # ==========================================================
    # HELPERS
    # ==========================================================

    def create_active_tenancy(
        self,
        tenant=None,
    ):
        tenant = tenant or self.tenant

        return TenancyService.create_tenancy(
            tenant=tenant,
            unit=self.unit,
            start_date="2026-08-01",
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

    def create_request(
        self,
        tenant=None,
    ):
        tenant = tenant or self.tenant

        self.create_active_tenancy(
            tenant=tenant,
        )

        return MaintenanceRequest.objects.create(
            tenant=tenant,
            property=self.property,
            unit=self.unit,
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
    # AUTHENTICATION
    # ==========================================================

    def test_unauthenticated_user_cannot_list_requests(self):
        response = self.client.get(
            self.list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def test_tenant_can_create_request(self):
        self.create_active_tenancy()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.list_url(),
            {
                "unit": self.unit.id,
                "title": "Broken faucet",
                "description": "Kitchen faucet is leaking.",
                "priority": "HIGH",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        self.assertTrue(
            MaintenanceRequest.objects.filter(
                tenant=self.tenant,
                property=self.property,
                unit=self.unit,
                title="Broken faucet",
            ).exists()
        )

        request = MaintenanceRequest.objects.get(
            tenant=self.tenant,
            title="Broken faucet",
        )

        self.assertEqual(
            request.status,
            MaintenanceStatus.PENDING,
        )

        self.assertEqual(
            request.priority,
            "HIGH",
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
            status.HTTP_400_BAD_REQUEST,
        )

    def test_tenant_without_active_tenancy_cannot_create_request(
        self,
    ):
        self.client.force_authenticate(
            user=self.other_tenant,
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
            status.HTTP_400_BAD_REQUEST,
        )

    # ==========================================================
    # LIST ACCESS
    # ==========================================================

    def test_tenant_can_list_own_requests(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.list_url()
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
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            request.id,
        )

    def test_property_manager_can_list_managed_requests(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.list_url()
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
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            request.id,
        )
    
    # ==========================================================
    # START
    # ==========================================================

    def test_manager_can_start_request(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
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

    # ==========================================================
    # COMPLETE
    # ==========================================================

    def test_manager_can_complete_request(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        start_response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            start_response.status_code,
            status.HTTP_200_OK,
            start_response.data,
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
            response.data,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.COMPLETED,
        )

        self.assertEqual(
            request.actual_cost,
            Decimal("1500.00"),
        )

        self.assertIsNotNone(
            request.completed_at,
        )

    # ==========================================================
    # CANCEL
    # ==========================================================

    def test_tenant_can_cancel_pending_request(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.cancel_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            response.data,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.CANCELLED,
        )

    # ==========================================================
    # WORKFLOW PROTECTION
    # ==========================================================

    def test_manager_cannot_complete_pending_request_directly(
        self,
    ):
        request = self.create_request()

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
            status.HTTP_400_BAD_REQUEST,
        )

    def test_status_cannot_be_changed_through_patch(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.detail_url(request.id),
            {
                "status": "COMPLETED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        request.refresh_from_db()

        self.assertEqual(
            request.status,
            MaintenanceStatus.PENDING,
        )

    def test_other_manager_cannot_start_request(self):
        request = self.create_request()

        self.client.force_authenticate(
            user=self.other_manager,
        )

        response = self.client.post(
            self.start_url(request.id),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )