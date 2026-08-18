from django.urls import path

from .views import (
    CreateOrderView,
    OrderListView,
    OrderDetailView,
    OrderStatusUpdateView,
    CancelOrderView,
)


urlpatterns = [
    path(
        "create/",
        CreateOrderView.as_view(),
        name="create-order"
    ),

    path(
        "",
        OrderListView.as_view(),
        name="order-list"
    ),

    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail"
    ),
    
    path(
        "<int:pk>/status/",
        OrderStatusUpdateView.as_view(),
        name="order-status-update"
    ),
    
    path(
        "<int:pk>/cancel/",
        CancelOrderView.as_view(),
        name="order-cancel"
    ),
]