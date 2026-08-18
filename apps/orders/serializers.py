import uuid

from django.db import transaction
from rest_framework import serializers

from .models import Order, OrderItem
from apps.cart.models import Cart


class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price",
            "total_price",
        ]

        read_only_fields = [
            "id",
            "product_name",
            "price",
            "total_price",
        ]


class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
            "items",
        ]

        read_only_fields = [
            "id",
            "order_number",
            "user",
            "total_amount",
            "status",
            "created_at",
            "updated_at",
            "items",
        ]


class CreateOrderSerializer(serializers.Serializer):

    def create(self, validated_data):

        user = self.context["request"].user

        cart_items = (
            Cart.objects
            .filter(user=user)
            .select_related("product")
        )

        if not cart_items.exists():
            raise serializers.ValidationError(
                "Your cart is empty."
            )

        with transaction.atomic():

            order = Order.objects.create(
                user=user,
                order_number=self.generate_order_number(),
                total_amount=0
            )

            total_amount = 0

            for cart_item in cart_items:

                product = cart_item.product

                if product is None:
                    continue

                price = (
                    product.discount_price
                    if product.discount_price is not None
                    else product.price
                )

                item_total = price * cart_item.quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=price,
                    total_price=item_total
                )

                total_amount += item_total

            if total_amount == 0:
                raise serializers.ValidationError(
                    "Unable to create order because your cart contains no valid products."
                )

            order.total_amount = total_amount

            order.save(
                update_fields=["total_amount", "updated_at"]
            )

            cart_items.delete()

        return order

    def generate_order_number(self):

        while True:

            order_number = (
                f"WN-{uuid.uuid4().hex[:10].upper()}"
            )

            if not Order.objects.filter(
                order_number=order_number
            ).exists():

                return order_number

    def to_representation(self, instance):
        return OrderSerializer(
            instance,
            context=self.context
        ).data