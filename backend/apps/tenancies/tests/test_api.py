from datetime import date
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.properties.models import (
    Property,
    PropertyStatus,
    PropertyType,
    Unit,
    UnitStatus,
    UnitType,
)
from apps.tenancies.models import Tenancy, TenancyStatus


class TenancyAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            role="PROPERTY_MANAGER",
        )

        cls.other_manager = User.objects.create_user(
            email="othermanager@example.com",
            password="StrongPassword123!",
            role="PROPERTY_MANAGER",
        )

        cls.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            role="TENANT",
        )

        cls.other_tenant = User.objects.create_user(
            email="othertenant@example.com",
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

        cls.other_property = Property.objects.create(
            manager=cls.other_manager,
            name="Ocean View Apartments",
            property_type=PropertyType.APARTMENT,
            description="Another residential property.",
            address_line="456 Ocean Street",
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

        cls.other_unit = Unit.objects.create(
            property=cls.other_property,
            unit_number="201",
            unit_type=UnitType.ONE_BEDROOM,
            bedrooms=1,
            bathrooms=Decimal("1.0"),
            monthly_rent=Decimal("18000.00"),
            status=UnitStatus.AVAILABLE,
        )

    # ==========================================================
    # URL HELPERS
    # ==========================================================

    def tenancy_list_url(self):
        return reverse(
            "tenancies:tenancy-list-create",
        )

    def tenancy_detail_url(self, tenancy):
        return reverse(
            "tenancies:tenancy-detail",
            kwargs={"pk": tenancy.pk},
        )

    def tenancy_activate_url(self, tenancy):
        return reverse(
            "tenancies:tenancy-activate",
            kwargs={"pk": tenancy.pk},
        )

    def tenancy_end_url(self, tenancy):
        return reverse(
            "tenancies:tenancy-end",
            kwargs={"pk": tenancy.pk},
        )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def create_pending_tenancy(self):
        return Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.PENDING,
        )

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    def test_unauthenticated_user_cannot_list_tenancies(self):
        response = self.client.get(
            self.tenancy_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_tenant_cannot_create_tenancy(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.tenancy_list_url(),
            {
                "tenant": self.tenant.id,
                "unit": self.unit.id,
                "start_date": "2026-08-01",
                "monthly_rent": "15000.00",
                "security_deposit": "15000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def test_property_manager_can_create_tenancy(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_list_url(),
            {
                "tenant": self.tenant.id,
                "unit": self.unit.id,
                "start_date": "2026-08-01",
                "monthly_rent": "15000.00",
                "security_deposit": "15000.00",
                "notes": "Initial tenancy.",
            },
            format="json",
        )

        print(
            "CREATE TENANCY STATUS:",
            response.status_code,
        )

        print(
            "CREATE TENANCY DATA:",
            response.data,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Tenancy.objects.filter(
                tenant=self.tenant,
                unit=self.unit,
            ).exists()
        )

    def test_manager_cannot_create_tenancy_for_another_manager_unit(
        self,
    ):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_list_url(),
            {
                "tenant": self.tenant.id,
                "unit": self.other_unit.id,
                "start_date": "2026-08-01",
                "monthly_rent": "18000.00",
                "security_deposit": "18000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_create_tenancy_requires_unit(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_list_url(),
            {
                "tenant": self.tenant.id,
                "start_date": "2026-08-01",
                "monthly_rent": "15000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "unit",
            response.data,
        )

    def test_create_tenancy_requires_tenant(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_list_url(),
            {
                "unit": self.unit.id,
                "start_date": "2026-08-01",
                "monthly_rent": "15000.00",
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

    # ==========================================================
    # LIST
    # ==========================================================

    def test_property_manager_can_list_own_tenancies(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.tenancy_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            tenancy.id,
            returned_ids,
        )

    def test_tenant_can_list_own_tenancies(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.tenancy_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        returned_ids = [
            item["id"]
            for item in response.data
        ]

        self.assertIn(
            tenancy.id,
            returned_ids,
        )

    # ==========================================================
    # DETAIL
    # ==========================================================

    def test_property_manager_can_retrieve_own_tenancy(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.tenancy_detail_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            tenancy.id,
        )

    def test_tenant_can_retrieve_own_tenancy(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.tenancy_detail_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    # ==========================================================
    # UPDATE
    # ==========================================================

    def test_property_manager_can_update_tenancy(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.tenancy_detail_url(tenancy),
            {
                "monthly_rent": "16000.00",
                "notes": "Rent updated.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        tenancy.refresh_from_db()

        self.assertEqual(
            tenancy.monthly_rent,
            Decimal("16000.00"),
        )

        self.assertEqual(
            tenancy.notes,
            "Rent updated.",
        )

    def test_tenant_cannot_update_tenancy(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.patch(
            self.tenancy_detail_url(tenancy),
            {
                "monthly_rent": "16000.00",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # STATUS WORKFLOW
    # ==========================================================

    def test_property_manager_can_activate_tenancy(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_activate_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        tenancy.refresh_from_db()
        self.unit.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ACTIVE,
        )

        self.assertEqual(
            self.unit.status,
            UnitStatus.OCCUPIED,
        )

    def test_duplicate_active_tenancy_is_rejected(self):
        first = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.unit.status = UnitStatus.OCCUPIED
        self.unit.save(
            update_fields=["status", "updated_at"],
        )

        second = Tenancy.objects.create(
            tenant=self.other_tenant,
            unit=self.unit,
            start_date=date(2026, 9, 1),
            monthly_rent=Decimal("15500.00"),
            security_deposit=Decimal("15500.00"),
            status=TenancyStatus.PENDING,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_activate_url(second),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        second.refresh_from_db()

        self.assertEqual(
            second.status,
            TenancyStatus.PENDING,
        )

        self.assertEqual(
            first.status,
            TenancyStatus.ACTIVE,
        )

    def test_property_manager_can_end_active_tenancy(self):
        tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.unit.status = UnitStatus.OCCUPIED
        self.unit.save(
            update_fields=["status", "updated_at"],
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_end_url(tenancy),
            {
                "end_date": "2026-08-31",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        tenancy.refresh_from_db()
        self.unit.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ENDED,
        )

        self.assertEqual(
            tenancy.end_date,
            date(2026, 8, 31),
        )

        self.assertEqual(
            self.unit.status,
            UnitStatus.AVAILABLE,
        )

    def test_end_tenancy_requires_end_date(self):
        tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_end_url(tenancy),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
            response.data,
        )

    def test_invalid_end_date_is_rejected(self):
        tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_end_url(tenancy),
            {
                "end_date": "not-a-date",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "end_date",
            response.data,
        )

    # ==========================================================
    # STATUS PROTECTION
    # ==========================================================

    def test_status_cannot_be_changed_through_patch(self):
        tenancy = self.create_pending_tenancy()

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.tenancy_detail_url(tenancy),
            {
                "status": TenancyStatus.ACTIVE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        tenancy.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.PENDING,
        )