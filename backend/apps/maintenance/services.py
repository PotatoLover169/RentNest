from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import UserRole
from apps.properties.models import Unit

from .models import (
    MaintenancePriority,
    MaintenanceRequest,
    MaintenanceStatus,
)


class MaintenanceService:

    # ============================================================
    # CREATE REQUEST
    # ============================================================

    @staticmethod
    @transaction.atomic
    def create_request(
        *,
        tenant,
        unit,
        title,
        description,
        priority=MaintenancePriority.MEDIUM,
    ):
        """
        Create a maintenance request.

        Rules:
        - Only tenants can submit requests.
        - Tenant must have an ACTIVE tenancy for the unit.
        - Unit must belong to the tenant's active tenancy.
        """

        if tenant.role != UserRole.TENANT:
            raise ValidationError(
                "Only tenants can submit maintenance requests."
            )

        has_active_tenancy = tenant.tenancies.filter(
            unit=unit,
            status="ACTIVE",
        ).exists()

        if not has_active_tenancy:
            raise ValidationError(
                "The tenant does not have an active tenancy "
                "for this unit."
            )

        return MaintenanceRequest.objects.create(
            unit=unit,
            tenant=tenant,
            title=title,
            description=description,
            priority=priority,
            status=MaintenanceStatus.OPEN,
        )

    # ============================================================
    # START WORK
    # ============================================================

    @staticmethod
    @transaction.atomic
    def start_request(
        *,
        request_instance,
        manager,
    ):
        """
        Move an OPEN request to IN_PROGRESS.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
            .select_related(
                "unit",
                "unit__property",
            )
            .get(
                pk=request_instance.pk,
            )
        )

        MaintenanceService._ensure_manager_owns_request(
            maintenance_request=maintenance_request,
            manager=manager,
        )

        if maintenance_request.status != MaintenanceStatus.OPEN:
            raise ValidationError(
                "Only an open maintenance request "
                "can be started."
            )

        maintenance_request.status = (
            MaintenanceStatus.IN_PROGRESS
        )

        maintenance_request.assigned_to = manager

        maintenance_request.save(
            update_fields=[
                "status",
                "assigned_to",
                "updated_at",
            ]
        )

        return maintenance_request

    # ============================================================
    # RESOLVE REQUEST
    # ============================================================

    @staticmethod
    @transaction.atomic
    def resolve_request(
        *,
        request_instance,
        manager,
        resolution_notes,
    ):
        """
        Move an IN_PROGRESS request to RESOLVED.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
            .select_related(
                "unit",
                "unit__property",
            )
            .get(
                pk=request_instance.pk,
            )
        )

        MaintenanceService._ensure_manager_owns_request(
            maintenance_request=maintenance_request,
            manager=manager,
        )

        if maintenance_request.status != (
            MaintenanceStatus.IN_PROGRESS
        ):
            raise ValidationError(
                "Only an in-progress maintenance request "
                "can be resolved."
            )

        if not resolution_notes:
            raise ValidationError(
                "Resolution notes are required."
            )

        maintenance_request.status = (
            MaintenanceStatus.RESOLVED
        )

        maintenance_request.resolution_notes = (
            resolution_notes
        )

        maintenance_request.save(
            update_fields=[
                "status",
                "resolution_notes",
                "updated_at",
            ]
        )

        return maintenance_request

    # ============================================================
    # CLOSE REQUEST
    # ============================================================

    @staticmethod
    @transaction.atomic
    def close_request(
        *,
        request_instance,
        manager,
    ):
        """
        Move a RESOLVED request to CLOSED.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
            .select_related(
                "unit",
                "unit__property",
            )
            .get(
                pk=request_instance.pk,
            )
        )

        MaintenanceService._ensure_manager_owns_request(
            maintenance_request=maintenance_request,
            manager=manager,
        )

        if maintenance_request.status != (
            MaintenanceStatus.RESOLVED
        ):
            raise ValidationError(
                "Only a resolved maintenance request "
                "can be closed."
            )

        maintenance_request.status = (
            MaintenanceStatus.CLOSED
        )

        maintenance_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return maintenance_request

    # ============================================================
    # CANCEL REQUEST
    # ============================================================

    @staticmethod
    @transaction.atomic
    def cancel_request(
        *,
        request_instance,
        tenant,
    ):
        """
        Cancel an OPEN maintenance request.

        Only the tenant who created the request can cancel it.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
            .select_related(
                "unit",
            )
            .get(
                pk=request_instance.pk,
            )
        )

        if maintenance_request.tenant_id != tenant.id:
            raise ValidationError(
                "You do not have permission to cancel "
                "this maintenance request."
            )

        if maintenance_request.status != (
            MaintenanceStatus.OPEN
        ):
            raise ValidationError(
                "Only an open maintenance request "
                "can be cancelled."
            )

        maintenance_request.status = (
            MaintenanceStatus.CANCELLED
        )

        maintenance_request.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return maintenance_request

    # ============================================================
    # PRIVATE VALIDATION
    # ============================================================

    @staticmethod
    def _ensure_manager_owns_request(
        *,
        maintenance_request,
        manager,
    ):
        if manager.role != UserRole.PROPERTY_MANAGER:
            raise ValidationError(
                "Only property managers can manage "
                "maintenance requests."
            )

        if (
            maintenance_request.unit.property.manager_id
            != manager.id
        ):
            raise ValidationError(
                "You do not manage the property "
                "for this maintenance request."
            )