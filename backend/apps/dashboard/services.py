from apps.accounts.models import User, UserRole
from apps.maintenance.models import MaintenanceRequest, MaintenanceStatus
from apps.notifications.models import Notification
from apps.payments.models import Payment, PaymentStatus
from apps.properties.models import Property, Unit
from apps.tenancies.models import Tenancy, TenancyStatus


OPEN_MAINTENANCE_STATUSES = (
    MaintenanceStatus.PENDING,
    MaintenanceStatus.IN_PROGRESS,
)


def get_dashboard_summary(user):
    """
    Return database-backed dashboard statistics for the signed-in user.

    ADMIN:
        Platform-wide counts.

    PROPERTY_MANAGER:
        Counts restricted to properties managed by this user and their
        related rental activity.

    TENANT:
        Counts restricted to this tenant's own rental activity.
    """
    properties = Property.objects.all()
    units = Unit.objects.all()
    tenancies = Tenancy.objects.all()
    payments = Payment.objects.all()
    maintenance_requests = MaintenanceRequest.objects.all()

    if user.role == UserRole.PROPERTY_MANAGER:
        properties = properties.filter(manager=user)
        units = units.filter(property__manager=user)
        tenancies = tenancies.filter(unit__property__manager=user)
        payments = payments.filter(
            tenancy__unit__property__manager=user
        )
        maintenance_requests = maintenance_requests.filter(
            property__manager=user
        )

    elif user.role == UserRole.TENANT:
        # A tenant only sees records belonging to their own account.
        tenancies = tenancies.filter(tenant=user)
        payments = payments.filter(tenant=user)
        maintenance_requests = maintenance_requests.filter(tenant=user)

    summary = {
        "active_tenancies": tenancies.filter(
            status=TenancyStatus.ACTIVE
        ).count(),
        "pending_payments": payments.filter(
            status=PaymentStatus.PENDING
        ).count(),
        "open_maintenance_requests": maintenance_requests.filter(
            status__in=OPEN_MAINTENANCE_STATUSES
        ).count(),
        "unread_notifications": Notification.objects.filter(
            recipient=user,
            is_read=False,
        ).count(),
    }

    if user.role in (UserRole.ADMIN, UserRole.PROPERTY_MANAGER):
        summary.update(
            {
                "properties": properties.count(),
                "units": units.count(),
            }
        )

    if user.role == UserRole.ADMIN:
        summary.update(
            {
                "total_users": User.objects.count(),
                "total_tenancies": tenancies.count(),
                "total_payments": payments.count(),
                "total_maintenance_requests": (
                    maintenance_requests.count()
                ),
            }
        )

    return summary
