from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.properties.models import Property, PropertyType
from apps.properties.permissions import (
    IsPropertyManager,
    IsPropertyManagerOrReadOnly,
    IsPropertyManagerOwner,
)


User = get_user_model()


class PropertyPermissionTests(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123!",
            first_name="Property",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

        self.other_manager = User.objects.create_user(
            email="other@example.com",
            password="StrongPassword123!",
            first_name="Other",
            last_name="Manager",
            role="PROPERTY_MANAGER",
        )

        self.tenant = User.objects.create_user(
            email="tenant@example.com",
            password="StrongPassword123!",
            first_name="John",
            last_name="Tenant",
            role="TENANT",
        )

        self.property = Property.objects.create(
            manager=self.manager,
            name="Sunrise Residences",
            property_type=PropertyType.APARTMENT,
            address_line="123 Main Street",
            city="Cebu City",
            province="Cebu",
        )

    def test_property_manager_has_manager_permission(self):
        request = self.factory.get("/")

        request.user = self.manager

        permission = IsPropertyManager()

        self.assertTrue(
            permission.has_permission(request, None)
        )

    def test_tenant_does_not_have_manager_permission(self):
        request = self.factory.get("/")

        request.user = self.tenant

        permission = IsPropertyManager()

        self.assertFalse(
            permission.has_permission(request, None)
        )

    def test_manager_can_access_owned_property(self):
        request = self.factory.get("/")

        request.user = self.manager

        permission = IsPropertyManagerOwner()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )

    def test_manager_cannot_access_other_manager_property(self):
        request = self.factory.get("/")

        request.user = self.other_manager

        permission = IsPropertyManagerOwner()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )

    def test_tenant_cannot_access_property_as_manager(self):
        request = self.factory.get("/")

        request.user = self.tenant

        permission = IsPropertyManagerOwner()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )

    def test_manager_can_modify_owned_property(self):
        request = self.factory.patch("/")

        request.user = self.manager

        permission = IsPropertyManagerOrReadOnly()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )

    def test_other_manager_cannot_modify_property(self):
        request = self.factory.patch("/")

        request.user = self.other_manager

        permission = IsPropertyManagerOrReadOnly()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )

    def test_tenant_cannot_modify_property(self):
        request = self.factory.patch("/")

        request.user = self.tenant

        permission = IsPropertyManagerOrReadOnly()

        self.assertFalse(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )

    def test_authenticated_user_can_read_property(self):
        request = self.factory.get("/")

        request.user = self.tenant

        permission = IsPropertyManagerOrReadOnly()

        self.assertTrue(
            permission.has_object_permission(
                request,
                None,
                self.property,
            )
        )