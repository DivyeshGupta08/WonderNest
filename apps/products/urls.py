from django.urls import path
from .views import CategoryListAPIView, ProductListAPIView

urlpatterns = [
    path("categories/", CategoryListAPIView.as_view()),
    path("", ProductListAPIView.as_view()),
]