from django.urls import path

from .views import (
    CreatePaymentView,
    PaymentListView,
    PaymentDetailView,
    VerifyPaymentView,
)

urlpatterns = [
    path(
        "create/",
        CreatePaymentView.as_view(),
        name="create-payment",
    ),

    path(
        "",
        PaymentListView.as_view(),
        name="payment-list",
    ),

    path(
        "<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment-detail",
    ),

    path(
        "<int:pk>/verify/",
        VerifyPaymentView.as_view(),
        name="verify-payment",
    ),
]