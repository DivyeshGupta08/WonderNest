from django.urls import path
from .views import (
    CategoryListAPIView,
    ProductListAPIView,
    ProductDetailAPIView,
    ProductCreateAPIView,
    ProductUpdateAPIView,
    ProductDeleteAPIView,
)

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view()),
    path("", ProductListAPIView.as_view()),
    path("create/", ProductCreateAPIView.as_view()),
    path("<slug:slug>/", ProductDetailAPIView.as_view()),
    path("<slug:slug>/update/", ProductUpdateAPIView.as_view()),
    path("<slug:slug>/delete/", ProductDeleteAPIView.as_view()),
]