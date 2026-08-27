from django.urls import path

from .views import (
    PropertyDeactivateView,
    PropertyDetailView,
    PropertyListCreateView,
    UnitDeactivateView,
    UnitDetailView,
    UnitListCreateView,
    UnitStatusView,
)


app_name = "properties"


urlpatterns = [
    # ========================================================
    # PROPERTY ROUTES
    # ========================================================

    path(
        "",
        PropertyListCreateView.as_view(),
        name="property-list-create",
    ),

    path(
        "<int:pk>/",
        PropertyDetailView.as_view(),
        name="property-detail",
    ),

    path(
        "<int:pk>/deactivate/",
        PropertyDeactivateView.as_view(),
        name="property-deactivate",
    ),

    # ========================================================
    # UNIT ROUTES
    # ========================================================

    path(
        "units/",
        UnitListCreateView.as_view(),
        name="unit-list-create",
    ),

    path(
        "units/<int:pk>/",
        UnitDetailView.as_view(),
        name="unit-detail",
    ),

    path(
        "units/<int:pk>/status/",
        UnitStatusView.as_view(),
        name="unit-status",
    ),

    path(
        "units/<int:pk>/deactivate/",
        UnitDeactivateView.as_view(),
        name="unit-deactivate",
    ),
]