from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class PropertyType(models.TextChoices):
    APARTMENT = "APARTMENT", "Apartment"
    CONDOMINIUM = "CONDOMINIUM", "Condominium"
    HOUSE = "HOUSE", "House"
    BOARDING_HOUSE = "BOARDING_HOUSE", "Boarding House"
    DORMITORY = "DORMITORY", "Dormitory"
    COMMERCIAL = "COMMERCIAL", "Commercial"
    OTHER = "OTHER", "Other"


class PropertyStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"


class UnitType(models.TextChoices):
    STUDIO = "STUDIO", "Studio"
    ONE_BEDROOM = "ONE_BEDROOM", "One Bedroom"
    TWO_BEDROOM = "TWO_BEDROOM", "Two Bedroom"
    THREE_BEDROOM = "THREE_BEDROOM", "Three Bedroom"
    FOUR_PLUS_BEDROOM = "FOUR_PLUS_BEDROOM", "Four Plus Bedroom"
    COMMERCIAL = "COMMERCIAL", "Commercial"
    OTHER = "OTHER", "Other"


class UnitStatus(models.TextChoices):
    AVAILABLE = "AVAILABLE", "Available"
    OCCUPIED = "OCCUPIED", "Occupied"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    INACTIVE = "INACTIVE", "Inactive"


class Property(models.Model):
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="managed_properties",
        limit_choices_to={"role": "PROPERTY_MANAGER"},
    )

    name = models.CharField(
        max_length=150,
    )

    property_type = models.CharField(
        max_length=30,
        choices=PropertyType.choices,
        db_index=True,
    )

    description = models.TextField(
        blank=True,
    )

    address_line = models.CharField(
        max_length=255,
    )

    city = models.CharField(
        max_length=100,
        db_index=True,
    )

    province = models.CharField(
        max_length=100,
        db_index=True,
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=PropertyStatus.choices,
        default=PropertyStatus.ACTIVE,
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["manager", "status"],
                name="property_manager_status_idx",
            ),
            models.Index(
                fields=["city", "province"],
                name="property_location_idx",
            ),
        ]

    def __str__(self):
        return self.name


class Unit(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="units",
    )

    unit_number = models.CharField(
        max_length=50,
    )

    unit_type = models.CharField(
        max_length=30,
        choices=UnitType.choices,
    )

    bedrooms = models.PositiveSmallIntegerField(
        default=0,
    )

    bathrooms = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1,
        validators=[
            MinValueValidator(0),
        ],
    )

    monthly_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=UnitStatus.choices,
        default=UnitStatus.AVAILABLE,
        db_index=True,
    )

    description = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["property", "unit_number"]

        constraints = [
            models.UniqueConstraint(
                fields=["property", "unit_number"],
                name="unique_unit_number_per_property",
            ),
        ]

        indexes = [
            models.Index(
                fields=["property", "status"],
                name="unit_property_status_idx",
            ),
            models.Index(
                fields=["status", "monthly_rent"],
                name="unit_status_rent_idx",
            ),
        ]

    def __str__(self):
        return f"{self.property.name} - Unit {self.unit_number}"