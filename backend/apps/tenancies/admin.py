from django.contrib import admin

from .models import Tenancy


@admin.register(Tenancy)
class TenancyAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "unit",
        "start_date",
        "end_date",
        "monthly_rent",
        "status",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
    )

    search_fields = (
        "tenant__email",
        "unit__unit_number",
        "unit__property__name",
    )