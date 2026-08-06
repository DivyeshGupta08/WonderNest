from django.urls import path

from .views import (
    WishlistListAPIView,
    WishlistCreateAPIView,
    WishlistDeleteAPIView,
)

urlpatterns = [
    path("", WishlistListAPIView.as_view()),
    path("add/", WishlistCreateAPIView.as_view()),
    path("<int:pk>/delete/", WishlistDeleteAPIView.as_view()),
]