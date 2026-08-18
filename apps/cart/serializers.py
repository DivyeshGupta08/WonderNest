from rest_framework import serializers
from .models import Cart


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    product_price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "added_at",
        ]

        read_only_fields = [
            "id",
            "added_at",
            "product_name",
            "product_price",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Quantity must be at least 1."
            )

        return value
    
class CartSummarySerializer(serializers.Serializer):
    total_items = serializers.IntegerField()
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    discount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )