from django.urls import path

from .views import (
    TenancyActivateView,
    TenancyDetailView,
    TenancyEndView,
    TenancyListCreateView,
)


app_name = "tenancies"


urlpatterns = [
    path(
        "",
        TenancyListCreateView.as_view(),
        name="tenancy-list-create",
    ),

    path(
        "<int:pk>/",
        TenancyDetailView.as_view(),
        name="tenancy-detail",
    ),

    path(
        "<int:pk>/activate/",
        TenancyActivateView.as_view(),
        name="tenancy-activate",
    ),

    path(
        "<int:pk>/end/",
        TenancyEndView.as_view(),
        name="tenancy-end",
    ),
]