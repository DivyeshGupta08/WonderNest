from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.filter(available=True)

    serializer_class = ProductSerializer

    search_fields = [
        "name",
        "description",
        "brand",
    ]

    filterset_fields = [
        "category",
        "featured",
    ]

    ordering_fields = [
        "price",
        "created_at",
        "name",
    ]
    
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(available=True)

    serializer_class = ProductSerializer

    lookup_field = "slug"