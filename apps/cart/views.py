from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Cart
from .serializers import CartSerializer
from .serializers import CartSummarySerializer
from apps.products.models import Product
from decimal import Decimal


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"error": "Product ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {"error": "Quantity must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not product.available:
            return Response(
                {"error": "This product is currently unavailable."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > product.stock:
            return Response(
                {
                    "error": f"Only {product.stock} item(s) available in stock."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:

            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock:
                return Response(
                    {
                        "error": (
                            f"Only {product.stock} item(s) "
                            "available in stock."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity = new_quantity
            cart_item.save()

        serializer = CartSerializer(cart_item)

        return Response(
            {
                "message": (
                    "Product added to cart."
                    if created
                    else "Cart quantity updated."
                ),
                "cart": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class CartListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        cart_items = Cart.objects.filter(
            user=request.user
        ).select_related("product")

        serializer = CartSerializer(
            cart_items,
            many=True
        )

        return Response(
            {
                "count": cart_items.count(),
                "cart": serializer.data
            },
            status=status.HTTP_200_OK
        )


class UpdateCartView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):

        try:
            cart_item = Cart.objects.select_related(
                "product"
            ).get(
                id=pk,
                user=request.user
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get("quantity")

        if quantity is None:
            return Response(
                {"error": "Quantity is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response(
                {"error": "Quantity must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {"error": "Quantity must be at least 1."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart_item.product.available:
            return Response(
                {"error": "This product is currently unavailable."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > cart_item.product.stock:
            return Response(
                {
                    "error": (
                        f"Only {cart_item.product.stock} "
                        "item(s) available in stock."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart_item)

        return Response(
            {
                "message": "Cart quantity updated successfully.",
                "cart": serializer.data
            },
            status=status.HTTP_200_OK
        )


class DeleteCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        try:
            cart_item = Cart.objects.get(
                id=pk,
                user=request.user
            )
        except Cart.DoesNotExist:
            return Response(
                {"error": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()

        return Response(
            {
                "message": "Product removed from cart successfully."
            },
            status=status.HTTP_200_OK
        )
        
class CartSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        total_items = 0
        subtotal = Decimal("0.00")
        total = Decimal("0.00")

        for item in cart_items:
            total_items += item.quantity

            product_price = item.product.price
            item_total = product_price * item.quantity

            subtotal += item_total
            total += item.total_price

        discount = subtotal - total

        serializer = CartSummarySerializer({
            "total_items": total_items,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
        })

        return Response(serializer.data)