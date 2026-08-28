from django.core.exceptions import ValidationError
from django.db import transaction

from apps.properties.models import Unit, UnitStatus

from .models import Tenancy, TenancyStatus


class TenancyService:

    @staticmethod
    @transaction.atomic
    def create_tenancy(
        *,
        tenant,
        unit,
        start_date,
        monthly_rent,
        security_deposit=0,
        end_date=None,
        status=TenancyStatus.PENDING,
        notes="",
    ):
        """
        Create a tenancy.

        If the tenancy is created as ACTIVE:
        - The unit must not already have another ACTIVE tenancy.
        - The unit must be AVAILABLE.
        - The unit becomes OCCUPIED.
        """

        if status == TenancyStatus.ACTIVE:
            TenancyService._ensure_unit_can_be_activated(
                unit=unit,
            )

        tenancy = Tenancy.objects.create(
            tenant=tenant,
            unit=unit,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=monthly_rent,
            security_deposit=security_deposit,
            status=status,
            notes=notes,
        )

        if status == TenancyStatus.ACTIVE:
            unit.status = UnitStatus.OCCUPIED
            unit.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return tenancy

    @staticmethod
    @transaction.atomic
    def activate_tenancy(
        *,
        tenancy_instance,
    ):
        """
        Activate a pending tenancy.

        Rules:
        - Tenancy must not already be active.
        - An ended tenancy cannot be activated.
        - The unit must not already have another ACTIVE tenancy.
        - The unit must be AVAILABLE.
        - The unit becomes OCCUPIED.
        """

        tenancy = (
            Tenancy.objects
            .select_for_update()
            .select_related("unit")
            .get(pk=tenancy_instance.pk)
        )

        if tenancy.status == TenancyStatus.ACTIVE:
            raise ValidationError(
                "This tenancy is already active."
            )

        if tenancy.status == TenancyStatus.ENDED:
            raise ValidationError(
                "An ended tenancy cannot be activated."
            )

        unit = Unit.objects.select_for_update().get(
            pk=tenancy.unit_id,
        )

        TenancyService._ensure_unit_can_be_activated(
            unit=unit,
            exclude_tenancy=tenancy,
        )

        tenancy.status = TenancyStatus.ACTIVE

        tenancy.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        unit.status = UnitStatus.OCCUPIED

        unit.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return tenancy

    @staticmethod
    @transaction.atomic
    def end_tenancy(
        *,
        tenancy_instance,
        end_date,
    ):
        """
        End an active tenancy.

        The tenancy becomes ENDED and the unit becomes AVAILABLE.
        """

        tenancy = (
            Tenancy.objects
            .select_for_update()
            .select_related("unit")
            .get(pk=tenancy_instance.pk)
        )

        if tenancy.status != TenancyStatus.ACTIVE:
            raise ValidationError(
                "Only an active tenancy can be ended."
            )

        if end_date < tenancy.start_date:
            raise ValidationError(
                "End date cannot be before the tenancy start date."
            )

        unit = Unit.objects.select_for_update().get(
            pk=tenancy.unit_id,
        )

        tenancy.status = TenancyStatus.ENDED
        tenancy.end_date = end_date

        tenancy.save(
            update_fields=[
                "status",
                "end_date",
                "updated_at",
            ]
        )

        unit.status = UnitStatus.AVAILABLE

        unit.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return tenancy

    @staticmethod
    def _ensure_unit_can_be_activated(
        *,
        unit,
        exclude_tenancy=None,
    ):
        """
        Validate that a unit can receive an ACTIVE tenancy.

        This is a domain-level rule rather than a database
        constraint because MySQL does not support the
        conditional unique constraint used by the model.
        """

        active_tenancies = Tenancy.objects.filter(
            unit=unit,
            status=TenancyStatus.ACTIVE,
        )

        if exclude_tenancy is not None:
            active_tenancies = active_tenancies.exclude(
                pk=exclude_tenancy.pk,
            )

        if active_tenancies.exists():
            raise ValidationError(
                "This unit already has an active tenancy."
            )

        if unit.status != UnitStatus.AVAILABLE:
            raise ValidationError(
                "Only an available unit can have an active tenancy."
            )