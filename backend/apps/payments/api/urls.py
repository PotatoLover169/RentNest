from django.urls import path

from apps.payments.api.views import (
    PaymentCancelView,
    PaymentDetailView,
    PaymentListCreateView,
    PaymentMarkFailedView,
    PaymentMarkPaidView,
    PaymentRefundView,
)


app_name = "payments"


urlpatterns = [
    # ========================================================
    # PAYMENT LIST / CREATE
    # ========================================================

    path(
        "",
        PaymentListCreateView.as_view(),
        name="payment-list-create",
    ),

    # ========================================================
    # PAYMENT DETAIL
    # ========================================================

    path(
        "<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),

    # ========================================================
    # PAYMENT WORKFLOWS
    # ========================================================

    path(
        "<int:pk>/mark-paid/",
        PaymentMarkPaidView.as_view(),
        name="payment-mark-paid",
    ),

    path(
        "<int:pk>/mark-failed/",
        PaymentMarkFailedView.as_view(),
        name="payment-mark-failed",
    ),

    path(
        "<int:pk>/refund/",
        PaymentRefundView.as_view(),
        name="payment-refund",
    ),

    path(
        "<int:pk>/cancel/",
        PaymentCancelView.as_view(),
        name="payment-cancel",
    ),
]