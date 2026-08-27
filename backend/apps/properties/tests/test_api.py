from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserRole
from apps.properties.models import (
    Property,
    PropertyStatus,
    PropertyType,
)


class PropertyAPITests(APITestCase):
    """
    API tests for the RentNest properties domain.

    Covers:
    - authentication
    - role-based access
    - property ownership
    - property visibility
    - property updates
    - safe property deactivation
    """

    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role=UserRole.PROPERTY_MANAGER,
        )

        self.other_manager = User.objects.create_user(
            email="othermanager@example.com",
            password="StrongPassword123!",
            first_name="Other",
            last_name="Manager",
            role=UserRole.PROPERTY_MANAGER,
        )

        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Tenant",
            role=UserRole.TENANT,
        )

        self.property = Property.objects.create(
            manager=self.manager,
            name="Sunrise Apartments",
            property_type=PropertyType.APARTMENT,
            description="A modern residential property.",
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        self.other_property = Property.objects.create(
            manager=self.other_manager,
            name="Harbor View Residences",
            property_type=PropertyType.CONDOMINIUM,
            description="A residential property near the city.",
            address_line="456 Harbor Road",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.ACTIVE,
        )

        self.inactive_property = Property.objects.create(
            manager=self.manager,
            name="Old Property",
            property_type=PropertyType.HOUSE,
            description="An inactive property.",
            address_line="789 Old Road",
            city="Cebu City",
            province="Cebu",
            postal_code="6000",
            status=PropertyStatus.INACTIVE,
        )

    # ==========================================================
    # URL HELPERS
    # ==========================================================

    def property_list_url(self):
        return reverse(
            "properties:property-list-create",
        )

    def property_detail_url(self, property_id):
        return reverse(
            "properties:property-detail",
            kwargs={"pk": property_id},
        )

    def property_deactivate_url(self, property_id):
        return reverse(
            "properties:property-deactivate",
            kwargs={"pk": property_id},
        )

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    def test_unauthenticated_user_cannot_list_properties(self):
        response = self.client.get(
            self.property_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # ==========================================================
    # PROPERTY CREATION
    # ==========================================================

    def test_property_manager_can_create_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.property_list_url(),
            {
                "name": "New Rental Property",
                "property_type": PropertyType.APARTMENT,
                "description": "A newly managed rental property.",
                "address_line": "10 New Street",
                "city": "Cebu City",
                "province": "Cebu",
                "postal_code": "6000",
                "status": PropertyStatus.ACTIVE,
            },
            format="json",
        )

        print("CREATE PROPERTY STATUS:", response.status_code)
        print("CREATE PROPERTY DATA:", response.data)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Property.objects.filter(
                name="New Rental Property",
                manager=self.manager,
            ).exists()
        )

    def test_tenant_cannot_create_property(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.post(
            self.property_list_url(),
            {
                "name": "Tenant Property",
                "property_type": PropertyType.APARTMENT,
                "description": "This should not be created.",
                "address_line": "10 Tenant Street",
                "city": "Cebu City",
                "province": "Cebu",
                "postal_code": "6000",
                "status": PropertyStatus.ACTIVE,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ==========================================================
    # PROPERTY LIST / OWNERSHIP
    # ==========================================================

    def test_manager_only_sees_owned_properties(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.property_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        property_ids = {
            item["id"]
            for item in response.data
        }

        self.assertIn(
            self.property.id,
            property_ids,
        )

        self.assertNotIn(
            self.other_property.id,
            property_ids,
        )

    def test_tenant_can_list_active_properties(self):
        self.client.force_authenticate(
            user=self.tenant,
        )

        response = self.client.get(
            self.property_list_url(),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        property_ids = {
            item["id"]
            for item in response.data
        }

        self.assertIn(
            self.property.id,
            property_ids,
        )

        self.assertNotIn(
            self.inactive_property.id,
            property_ids,
        )

    # ==========================================================
    # PROPERTY RETRIEVAL
    # ==========================================================

    def test_manager_can_retrieve_owned_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.property_detail_url(
                self.property.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            self.property.id,
        )

    def test_manager_cannot_retrieve_another_managers_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.get(
            self.property_detail_url(
                self.other_property.id,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # PROPERTY UPDATE
    # ==========================================================

    def test_manager_can_update_owned_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.property_detail_url(
                self.property.id,
            ),
            {
                "name": "Updated Sunrise Apartments",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.property.refresh_from_db()

        self.assertEqual(
            self.property.name,
            "Updated Sunrise Apartments",
        )

    def test_manager_cannot_update_another_managers_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.patch(
            self.property_detail_url(
                self.other_property.id,
            ),
            {
                "name": "Unauthorized Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # ==========================================================
    # PROPERTY DEACTIVATION
    # ==========================================================

    def test_manager_can_deactivate_owned_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.property_deactivate_url(
                self.property.id,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.property.refresh_from_db()

        self.assertEqual(
            self.property.status,
            PropertyStatus.INACTIVE,
        )

    def test_deactivation_does_not_delete_property(self):
        self.client.force_authenticate(
            user=self.manager,
        )

        response = self.client.post(
            self.property_deactivate_url(
                self.property.id,
            ),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            Property.objects.filter(
                id=self.property.id,
            ).exists()
        )