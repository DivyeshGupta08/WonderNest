from django.urls import path
from .views import CartSummaryAPIView

from .views import (
    AddToCartView,
    CartListView,
    UpdateCartView,
    DeleteCartView,
)


urlpatterns = [

    path(
        "add/",
        AddToCartView.as_view(),
        name="cart-add"
    ),

    path(
        "",
        CartListView.as_view(),
        name="cart-list"
    ),

    path(
        "update/<int:pk>/",
        UpdateCartView.as_view(),
        name="cart-update"
    ),

    path(
        "delete/<int:pk>/",
        DeleteCartView.as_view(),
        name="cart-delete"
    ),
    
    path(
        "summary/",
        CartSummaryAPIView.as_view(),
        name="cart-summary"
    ),
]