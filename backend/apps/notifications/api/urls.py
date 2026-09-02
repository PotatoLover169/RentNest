from django.urls import path

from .views import (
    NotificationDeleteView,
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationMarkUnreadView,
)


app_name = "notifications"


urlpatterns = [
    path(
        "",
        NotificationListView.as_view(),
        name="notification-list",
    ),

    path(
        "<int:pk>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),

    path(
        "<int:pk>/mark-read/",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),

    path(
        "<int:pk>/mark-unread/",
        NotificationMarkUnreadView.as_view(),
        name="notification-mark-unread",
    ),

    path(
        "mark-all-read/",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),

    path(
        "<int:pk>/delete/",
        NotificationDeleteView.as_view(),
        name="notification-delete",
    ),
]