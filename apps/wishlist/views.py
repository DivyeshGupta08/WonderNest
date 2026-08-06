from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status

from .models import Wishlist
from .serializers import WishlistSerializer
from apps.products.models import Product


class WishlistListAPIView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class WishlistCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product")

        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            product=product,
        )

        if not created:
            return Response(
                {"message": "Product already in wishlist"},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Added to wishlist"},
            status=status.HTTP_201_CREATED,
        )


class WishlistDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            item = Wishlist.objects.get(
                id=pk,
                user=request.user,
            )
            item.delete()

            return Response(
                {"message": "Removed from wishlist"},
                status=status.HTTP_200_OK,
            )

        except Wishlist.DoesNotExist:
            return Response(
                {"error": "Wishlist item not found"},
                status=status.HTTP_404_NOT_FOUND,
            )