from django.urls import path

from .views import (
    PropertyDeactivateView,
    PropertyDetailView,
    PropertyListCreateView,
)


app_name = "properties"


urlpatterns = [
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
]