from django.core.exceptions import ValidationError
from django.db import transaction

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
        if status == TenancyStatus.ACTIVE:
            active_tenancy_exists = Tenancy.objects.filter(
                unit=unit,
                status=TenancyStatus.ACTIVE,
            ).exists()

            if active_tenancy_exists:
                raise ValidationError(
                    "This unit already has an active tenancy."
                )

        return Tenancy.objects.create(
            tenant=tenant,
            unit=unit,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=monthly_rent,
            security_deposit=security_deposit,
            status=status,
            notes=notes,
        )