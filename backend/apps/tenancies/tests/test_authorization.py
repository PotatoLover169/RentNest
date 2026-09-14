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


class TenancyAuthorizationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="StrongPassword123!",
            role="ADMIN",
            is_staff=False,
        )

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

    def create_tenancy(self):
        return Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.PENDING,
        )

    # ==========================================================
    # ADMIN
    # ==========================================================

    def test_admin_can_list_all_tenancies(self):
        tenancy = self.create_tenancy()

        self.client.force_authenticate(
            user=self.admin,
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
            for item in response.data["results"]
        ]

        self.assertIn(
            tenancy.id,
            returned_ids,
        )

    def test_admin_can_create_tenancy_for_any_property(self):
        self.client.force_authenticate(
            user=self.admin,
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
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Tenancy.objects.filter(
                tenant=self.tenant,
                unit=self.other_unit,
            ).exists()
        )

    def test_admin_can_update_any_tenancy(self):
        tenancy = self.create_tenancy()

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.patch(
            self.tenancy_detail_url(tenancy),
            {
                "monthly_rent": "16000.00",
                "notes": "Updated by administrator.",
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

    def test_admin_can_activate_any_tenancy(self):
        tenancy = self.create_tenancy()

        self.client.force_authenticate(
            user=self.admin,
        )

        response = self.client.post(
            self.tenancy_activate_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        tenancy.refresh_from_db()

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ACTIVE,
        )

    def test_admin_can_end_any_tenancy(self):
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
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_authenticate(
            user=self.admin,
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

        self.assertEqual(
            tenancy.status,
            TenancyStatus.ENDED,
        )

    # ==========================================================
    # PROPERTY MANAGER SCOPE
    # ==========================================================

    def test_manager_cannot_retrieve_other_manager_tenancy(self):
        tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.other_unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("18000.00"),
            security_deposit=Decimal("18000.00"),
            status=TenancyStatus.PENDING,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.tenancy_detail_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_manager_cannot_activate_other_manager_tenancy(self):
        tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.other_unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("18000.00"),
            security_deposit=Decimal("18000.00"),
            status=TenancyStatus.PENDING,
        )

        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.tenancy_activate_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # TENANT PROTECTION
    # ==========================================================

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

    def test_tenant_cannot_update_tenancy(self):
        tenancy = self.create_tenancy()

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

    def test_tenant_cannot_activate_tenancy(self):
        tenancy = self.create_tenancy()

        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.tenancy_activate_url(tenancy),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_tenant_cannot_end_tenancy(self):
        tenancy = Tenancy.objects.create(
            tenant=self.tenant,
            unit=self.unit,
            start_date=date(2026, 8, 1),
            monthly_rent=Decimal("15000.00"),
            security_deposit=Decimal("15000.00"),
            status=TenancyStatus.ACTIVE,
        )

        self.client.force_authenticate(
            user=self.tenant,
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
            status.HTTP_403_FORBIDDEN,
        )