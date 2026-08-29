from django.urls import path

from .views import (
    MaintenanceCancelView,
    MaintenanceCloseView,
    MaintenanceDetailView,
    MaintenanceListCreateView,
    MaintenanceResolveView,
    MaintenanceStartView,
)


app_name = "maintenance"


urlpatterns = [
    path(
        "",
        MaintenanceListCreateView.as_view(),
        name="maintenance-list-create",
    ),

    path(
        "<int:pk>/",
        MaintenanceDetailView.as_view(),
        name="maintenance-detail",
    ),

    path(
        "<int:pk>/start/",
        MaintenanceStartView.as_view(),
        name="maintenance-start",
    ),

    path(
        "<int:pk>/resolve/",
        MaintenanceResolveView.as_view(),
        name="maintenance-resolve",
    ),

    path(
        "<int:pk>/close/",
        MaintenanceCloseView.as_view(),
        name="maintenance-close",
    ),

    path(
        "<int:pk>/cancel/",
        MaintenanceCancelView.as_view(),
        name="maintenance-cancel",
    ),
]