from django.core.exceptions import ValidationError
from django.db import transaction

from apps.notifications.models import NotificationType
from apps.notifications.services import NotificationService
from apps.properties.models import Unit, UnitStatus

from .models import Tenancy, TenancyStatus


class TenancyService:

    # ============================================================
    # CREATE TENANCY
    # ============================================================

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

        Business rules:
        - A unit cannot have multiple ACTIVE tenancies.
        - An ACTIVE tenancy requires an AVAILABLE unit.
        - Creating an ACTIVE tenancy makes the unit OCCUPIED.
        """

        # --------------------------------------------------------
        # ACTIVE tenancy validation
        # --------------------------------------------------------

        if status == TenancyStatus.ACTIVE:
            TenancyService._ensure_unit_can_be_activated(
                unit=unit,
            )

        # --------------------------------------------------------
        # Create tenancy
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # ACTIVE tenancy occupies the unit
        # --------------------------------------------------------

        if status == TenancyStatus.ACTIVE:
            unit.status = UnitStatus.OCCUPIED

            unit.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        # --------------------------------------------------------
        # Create notification
        # --------------------------------------------------------

        NotificationService.create_notification(
            recipient=tenant,
            notification_type=NotificationType.TENANCY_CREATED,
            title="New Tenancy Created",
            message=(
                f"A new tenancy has been created for "
                f"Unit {unit.unit_number}."
            ),
        )

        return tenancy

    # ============================================================
    # ACTIVATE TENANCY
    # ============================================================

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
            .select_related(
                "unit",
                "tenant",
            )
            .get(
                pk=tenancy_instance.pk,
            )
        )

        # --------------------------------------------------------
        # Validate tenancy status
        # --------------------------------------------------------

        if tenancy.status == TenancyStatus.ACTIVE:
            raise ValidationError(
                "This tenancy is already active."
            )

        if tenancy.status == TenancyStatus.ENDED:
            raise ValidationError(
                "An ended tenancy cannot be activated."
            )

        # --------------------------------------------------------
        # Lock the unit
        # --------------------------------------------------------

        unit = Unit.objects.select_for_update().get(
            pk=tenancy.unit_id,
        )

        # --------------------------------------------------------
        # Validate unit
        # --------------------------------------------------------

        TenancyService._ensure_unit_can_be_activated(
            unit=unit,
            exclude_tenancy=tenancy,
        )

        # --------------------------------------------------------
        # Activate tenancy
        # --------------------------------------------------------

        tenancy.status = TenancyStatus.ACTIVE

        tenancy.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # --------------------------------------------------------
        # Occupy unit
        # --------------------------------------------------------

        unit.status = UnitStatus.OCCUPIED

        unit.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # --------------------------------------------------------
        # Create notification
        # --------------------------------------------------------

        NotificationService.create_notification(
            recipient=tenancy.tenant,
            notification_type=NotificationType.TENANCY_UPDATED,
            title="Tenancy Activated",
            message=(
                f"Your tenancy for Unit "
                f"{unit.unit_number} is now active."
            ),
        )

        return tenancy

    # ============================================================
    # END TENANCY
    # ============================================================

    @staticmethod
    @transaction.atomic
    def end_tenancy(
        *,
        tenancy_instance,
        end_date,
    ):
        """
        End an active tenancy.

        Rules:
        - Only ACTIVE tenancies can be ended.
        - End date cannot be before start date.
        - The tenancy becomes ENDED.
        - The unit becomes AVAILABLE.
        """

        tenancy = (
            Tenancy.objects
            .select_for_update()
            .select_related(
                "unit",
                "tenant",
            )
            .get(
                pk=tenancy_instance.pk,
            )
        )

        # --------------------------------------------------------
        # Validate tenancy status
        # --------------------------------------------------------

        if tenancy.status != TenancyStatus.ACTIVE:
            raise ValidationError(
                "Only an active tenancy can be ended."
            )

        # --------------------------------------------------------
        # Validate end date
        # --------------------------------------------------------

        if end_date < tenancy.start_date:
            raise ValidationError(
                "End date cannot be before the tenancy "
                "start date."
            )

        # --------------------------------------------------------
        # Lock unit
        # --------------------------------------------------------

        unit = Unit.objects.select_for_update().get(
            pk=tenancy.unit_id,
        )

        # --------------------------------------------------------
        # End tenancy
        # --------------------------------------------------------

        tenancy.status = TenancyStatus.ENDED
        tenancy.end_date = end_date

        tenancy.save(
            update_fields=[
                "status",
                "end_date",
                "updated_at",
            ]
        )

        # --------------------------------------------------------
        # Make unit available again
        # --------------------------------------------------------

        unit.status = UnitStatus.AVAILABLE

        unit.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # --------------------------------------------------------
        # Create notification
        # --------------------------------------------------------

        NotificationService.create_notification(
            recipient=tenancy.tenant,
            notification_type=NotificationType.TENANCY_UPDATED,
            title="Tenancy Ended",
            message=(
                f"Your tenancy for Unit "
                f"{unit.unit_number} has ended."
            ),
        )

        return tenancy

    # ============================================================
    # PRIVATE VALIDATION
    # ============================================================

    @staticmethod
    def _ensure_unit_can_be_activated(
        *,
        unit,
        exclude_tenancy=None,
    ):
        """
        Validate that a unit can receive an ACTIVE tenancy.

        This validation intentionally lives in the service layer
        because MySQL does not support the conditional unique
        constraint used to represent this business rule.
        """

        active_tenancies = Tenancy.objects.filter(
            unit=unit,
            status=TenancyStatus.ACTIVE,
        )

        # --------------------------------------------------------
        # Exclude the current tenancy when activating it
        # --------------------------------------------------------

        if exclude_tenancy is not None:
            active_tenancies = active_tenancies.exclude(
                pk=exclude_tenancy.pk,
            )

        # --------------------------------------------------------
        # Prevent multiple ACTIVE tenancies
        # --------------------------------------------------------

        if active_tenancies.exists():
            raise ValidationError(
                "This unit already has an active tenancy."
            )

        # --------------------------------------------------------
        # Unit must be available
        # --------------------------------------------------------

        if unit.status != UnitStatus.AVAILABLE:
            raise ValidationError(
                "Only an available unit can have "
                "an active tenancy."
            )