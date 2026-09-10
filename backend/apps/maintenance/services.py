from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

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
        - The maintenance request belongs to the unit's property.
        - New requests start with PENDING status.
        """

        if tenant.role != UserRole.TENANT:
            raise ValidationError(
                "Only tenants can submit maintenance requests."
            )

        unit = (
            Unit.objects
            .select_for_update()
            .select_related("property")
            .get(
                pk=unit.pk,
            )
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
            tenant=tenant,
            property=unit.property,
            unit=unit,
            title=title,
            description=description,
            priority=priority,
            status=MaintenanceStatus.PENDING,
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
        Move a PENDING request to IN_PROGRESS.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
            .select_related(
                "property",
                "unit",
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
            MaintenanceStatus.PENDING
        ):
            raise ValidationError(
                "Only a pending maintenance request "
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
    # COMPLETE REQUEST
    # ============================================================

    @staticmethod
    @transaction.atomic
    def complete_request(
        *,
        request_instance,
        manager,
        actual_cost=None,
    ):
        """
        Move an IN_PROGRESS request to COMPLETED.

        Optionally records the actual maintenance cost.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
            .select_related(
                "property",
                "unit",
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
                "can be completed."
            )

        if (
            actual_cost is not None
            and actual_cost < 0
        ):
            raise ValidationError(
                "Actual cost cannot be negative."
            )

        maintenance_request.status = (
            MaintenanceStatus.COMPLETED
        )

        maintenance_request.completed_at = timezone.now()

        if actual_cost is not None:
            maintenance_request.actual_cost = actual_cost

        update_fields = [
            "status",
            "completed_at",
            "updated_at",
        ]

        if actual_cost is not None:
            update_fields.append(
                "actual_cost",
            )

        maintenance_request.save(
            update_fields=update_fields,
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
        Cancel a PENDING maintenance request.

        Only the tenant who created the request can cancel it.
        """

        maintenance_request = (
            MaintenanceRequest.objects
            .select_for_update()
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
            MaintenanceStatus.PENDING
        ):
            raise ValidationError(
                "Only a pending maintenance request "
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
        """
        Ensure that the property manager owns the property
        associated with the maintenance request.
        """

        if manager.role != UserRole.PROPERTY_MANAGER:
            raise ValidationError(
                "Only property managers can manage "
                "maintenance requests."
            )

        if (
            maintenance_request.property.manager_id
            != manager.id
        ):
            raise ValidationError(
                "You do not manage the property "
                "for this maintenance request."
            )