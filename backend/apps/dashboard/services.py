from collections import (
    Counter,
    defaultdict,
)
from decimal import Decimal

from django.db.models import Q
from django.utils import timezone

from apps.approvals.models import (
    EditRequestStatus,
    TimeEntryEditRequest,
)
from apps.clients.models import Client
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.tracker.models import (
    TimeEntry,
    TimeEntryStatus,
)


def get_completed_entries(user):
    """
    Returns all completed time entries for the user.
    """
    return TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.COMPLETED,
    )


def get_running_timer(user):
    return TimeEntry.objects.filter(
        owner=user,
        status=TimeEntryStatus.RUNNING,
    ).exists()


def get_current_timer(user):
    """
    Return the currently running timer.
    """

    timer = (
        TimeEntry.objects
        .filter(
            owner=user,
            status=TimeEntryStatus.RUNNING,
        )
        .select_related(
            "project",
            "task",
        )
        .first()
    )

    if not timer:
        return None

    elapsed = timezone.now() - timer.start_time

    return {
        "id": timer.id,
        "project": timer.project,
        "task": timer.task,
        "description": timer.description,
        "start_time": timer.start_time,
        "elapsed_seconds": int(
            elapsed.total_seconds()
        ),
    }


def build_productivity_summary(entries):
    """
    Build a productivity summary from a queryset of completed entries.
    """

    total_seconds = 0
    billable_seconds = 0
    earnings = Decimal("0.00")

    for entry in entries:

        if entry.duration:

            seconds = entry.duration.total_seconds()

            total_seconds += seconds

            if entry.billable:
                billable_seconds += seconds

        earnings += entry.earnings

    return {
        "hours": round(
            total_seconds / 3600,
            2,
        ),

        "billable_hours": round(
            billable_seconds / 3600,
            2,
        ),

        "earnings": earnings,

        "entries": entries.count(),

        "completed_tasks": entries.exclude(
            task=None,
        ).count(),
    }


def get_today_summary(user):
    """
    Return today's productivity summary.
    """

    today = timezone.localdate()

    entries = get_completed_entries(user).filter(
        start_time__date=today,
    )

    return build_productivity_summary(
        entries,
    )


def get_week_summary(user):
    """
    Return this week's productivity summary.
    """

    today = timezone.localdate()

    week_start = today - timezone.timedelta(
        days=today.weekday(),
    )

    entries = get_completed_entries(user).filter(
        start_time__date__gte=week_start,
    )

    return build_productivity_summary(
        entries,
    )


def get_month_summary(user):
    """
    Return this month's productivity summary.
    """

    today = timezone.localdate()

    entries = get_completed_entries(user).filter(
        start_time__year=today.year,
        start_time__month=today.month,
    )

    return build_productivity_summary(
        entries,
    )


def get_today_hours(user):
    today = timezone.localdate()

    total_seconds = 0

    entries = get_completed_entries(user).filter(
        start_time__date=today,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_this_week_hours(user):
    today = timezone.localdate()

    week_start = today - timezone.timedelta(
        days=today.weekday()
    )

    total_seconds = 0

    entries = get_completed_entries(user).filter(
        start_time__date__gte=week_start,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_this_month_hours(user):
    today = timezone.localdate()

    total_seconds = 0

    entries = get_completed_entries(user).filter(
        start_time__year=today.year,
        start_time__month=today.month,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_billable_hours(user):
    total_seconds = 0

    entries = get_completed_entries(user).filter(
        billable=True,
    )

    for entry in entries:
        if entry.duration:
            total_seconds += entry.duration.total_seconds()

    return round(total_seconds / 3600, 2)


def get_estimated_earnings(user):
    total = Decimal("0.00")

    for entry in get_completed_entries(user):
        total += entry.earnings

    return total


def get_active_projects(user):
    """
    Return the number of active projects visible to the user.

    Managers and admins can view all active projects.

    Employees can view active projects that they either own
    or belong to as a project member.
    """

    active_projects = Project.objects.filter(
        status="in_progress",
    )

    is_manager_or_admin = (
        user.is_superuser
        or user.groups.filter(
            name__in=["Manager", "Admin"],
        ).exists()
    )

    if is_manager_or_admin:
        return active_projects.count()

    return active_projects.filter(
        Q(owner=user) | Q(members=user),
    ).distinct().count()


def get_completed_projects(user):
    return Project.objects.filter(
        owner=user,
        status="completed",
    ).count()


def get_total_clients(user):
    return Client.objects.filter(
        owner=user,
    ).count()


def get_pending_approvals():
    return TimeEntryEditRequest.objects.filter(
        status=EditRequestStatus.PENDING,
    ).count()


def get_recent_entries(
    user,
    limit=5,
):
    """
    Return the most recent completed time entries.
    """

    return (
        get_completed_entries(user)
        .select_related(
            "project",
            "task",
        )
        .order_by("-start_time")[:limit]
    )


def get_recent_projects(
    user,
    limit=5,
):
    """
    Return the user's most recently updated projects.
    """

    return (
        Project.objects.filter(
            owner=user,
        )
        .select_related(
            "client",
        )
        .order_by(
            "-updated_at",
        )[:limit]
    )


def get_upcoming_tasks(
    user,
    limit=5,
):
    """
    Return upcoming tasks ordered by due date.
    """

    today = timezone.localdate()

    return (
        Task.objects.filter(
            owner=user,
            due_date__isnull=False,
            due_date__gte=today,
        )
        .exclude(
            status="completed",
        )
        .select_related(
            "project",
        )
        .order_by(
            "due_date",
        )[:limit]
    )


def get_overdue_tasks(
    user,
    limit=5,
):
    """
    Return overdue tasks.
    """

    today = timezone.localdate()

    return (
        Task.objects.filter(
            owner=user,
            completed=False,
            due_date__lt=today,
        )
        .select_related(
            "project",
        )
        .order_by(
            "due_date",
        )[:limit]
    )


def get_active_timer(
    user,
):
    """
    Return the currently running timer.
    """

    return (
        TimeEntry.objects.filter(
            owner=user,
            status=TimeEntryStatus.RUNNING,
        )
        .select_related(
            "project",
            "task",
        )
        .first()
    )


def get_top_projects(
    user,
    limit=5,
):
    """
    Return the projects with the highest tracked hours.
    """

    project_data = defaultdict(
        lambda: {
            "project": None,
            "hours": 0,
            "earnings": Decimal("0.00"),
        }
    )

    entries = get_completed_entries(user).select_related(
        "project",
    )

    for entry in entries:
        project = entry.project

        item = project_data[project.id]

        item["project"] = project

        if entry.duration:
            item["hours"] += (
                entry.duration.total_seconds() / 3600
            )

        item["earnings"] += entry.earnings

    projects = sorted(
        project_data.values(),
        key=lambda x: x["hours"],
        reverse=True,
    )

    return projects[:limit]


def get_hours_per_day(
    user,
    days=7,
):
    """
    Return tracked hours for each of the last N days.
    """

    today = timezone.localdate()

    results = []

    for i in range(days - 1, -1, -1):
        current_day = today - timezone.timedelta(
            days=i,
        )

        total_seconds = 0

        entries = (
            get_completed_entries(user)
            .filter(
                start_time__date=current_day,
            )
        )

        for entry in entries:
            if entry.duration:
                total_seconds += (
                    entry.duration.total_seconds()
                )

        results.append(
            {
                "date": current_day.isoformat(),
                "hours": round(
                    total_seconds / 3600,
                    2,
                ),
            }
        )

    return results


def get_billable_breakdown(
    user,
):
    """
    Return billable and non-billable tracked hours.
    """

    billable_seconds = 0
    non_billable_seconds = 0

    entries = get_completed_entries(user)

    for entry in entries:
        if not entry.duration:
            continue

        seconds = entry.duration.total_seconds()

        if entry.billable:
            billable_seconds += seconds
        else:
            non_billable_seconds += seconds

    return {
        "billable_hours": round(
            billable_seconds / 3600,
            2,
        ),
        "non_billable_hours": round(
            non_billable_seconds / 3600,
            2,
        ),
    }


def get_project_status_breakdown(
    user,
):
    """
    Return the number of projects grouped by status.
    """

    statuses = (
        Project.objects.filter(
            owner=user,
        ).values_list(
            "status",
            flat=True,
        )
    )

    counter = Counter(statuses)

    return {
        "planning": counter.get(
            "planning",
            0,
        ),
        "in_progress": counter.get(
            "in_progress",
            0,
        ),
        "on_hold": counter.get(
            "on_hold",
            0,
        ),
        "completed": counter.get(
            "completed",
            0,
        ),
        "cancelled": counter.get(
            "cancelled",
            0,
        ),
    }


def get_chart_data(user):
    """
    Return chart-ready dashboard data.
    """

    hours = get_hours_per_day(user)
    billable = get_billable_breakdown(user)
    project_status = get_project_status_breakdown(user)

    return {
        "hours_per_day": [
            {
                "label": item["date"],
                "value": item["hours"],
            }
            for item in hours
        ],

        "billable": [
            {
                "label": "Billable",
                "value": billable["billable_hours"],
            },
            {
                "label": "Non-Billable",
                "value": billable["non_billable_hours"],
            },
        ],

        "project_status": [
            {
                "label": "Planning",
                "value": project_status["planning"],
            },
            {
                "label": "In Progress",
                "value": project_status["in_progress"],
            },
            {
                "label": "On Hold",
                "value": project_status["on_hold"],
            },
            {
                "label": "Completed",
                "value": project_status["completed"],
            },
            {
                "label": "Cancelled",
                "value": project_status["cancelled"],
            },
        ],
    }


def get_quick_stats(
    user,
):
    """
    Return lightweight dashboard statistics.
    """

    return {
        "today_hours": get_today_hours(user),
        "this_week_hours": get_this_week_hours(user),
        "this_month_hours": get_this_month_hours(user),
        "active_projects": get_active_projects(user),
        "completed_projects": get_completed_projects(user),
        "total_clients": get_total_clients(user),
        "billable_hours": get_billable_hours(user),
        "estimated_earnings": get_estimated_earnings(user),
        "pending_approvals": get_pending_approvals(),
    }


def get_dashboard_feed(
    user,
    limit=20,
):
    """
    Return a unified dashboard activity feed.
    """

    activities = []

    #
    # Recent Time Entries
    #
    entries = (
        get_completed_entries(user)
        .select_related(
            "project",
            "task",
        )
        .order_by(
            "-updated_at",
        )[:limit]
    )

    for entry in entries:

        activities.append(
            {
                "type": "time_entry",
                "title": "Time Entry Logged",
                "description": entry.description,
                "timestamp": entry.updated_at,
            }
        )

    #
    # Recent Projects
    #
    projects = (
        Project.objects.filter(
            owner=user,
        )
        .order_by(
            "-updated_at",
        )[:limit]
    )

    for project in projects:

        activities.append(
            {
                "type": "project",
                "title": "Project Updated",
                "description": project.name,
                "timestamp": project.updated_at,
            }
        )

    #
    # Recent Tasks
    #
    tasks = (
        Task.objects.filter(
            owner=user,
        )
        .order_by(
            "-updated_at",
        )[:limit]
    )

    for task in tasks:

        activities.append(
            {
                "type": "task",
                "title": "Task Updated",
                "description": task.title,
                "timestamp": task.updated_at,
            }
        )

    activities.sort(
        key=lambda item: item["timestamp"],
        reverse=True,
    )

    return activities[:limit]


def get_dashboard_data(user):
    """
    Return dashboard statistics.
    """

    return {
        "summary": {
            "running_timer": get_running_timer(user),
            "current_timer": get_current_timer(user),
            "today": get_today_summary(user),
            "week": get_week_summary(user),
            "month": get_month_summary(user),
            "today_hours": get_today_hours(user),
            "this_week_hours": get_this_week_hours(user),
            "this_month_hours": get_this_month_hours(user),
            "active_projects": get_active_projects(user),
            "completed_projects": get_completed_projects(user),
            "total_clients": get_total_clients(user),
            "billable_hours": get_billable_hours(user),
            "estimated_earnings": get_estimated_earnings(user),
            "pending_approvals": get_pending_approvals(),
        },

        "recent_entries": get_recent_entries(user),

        "top_projects": get_top_projects(user),

        "hours_per_day": get_hours_per_day(user),

        "billable_breakdown": get_billable_breakdown(user),

        "project_status_breakdown": get_project_status_breakdown(user),

        "charts": get_chart_data(user),
    }