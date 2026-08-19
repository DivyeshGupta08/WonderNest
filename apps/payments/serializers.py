from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):

    order_number = serializers.CharField(
        source="order.order_number",
        read_only=True
    )

    class Meta:
        model = Payment

        fields = [
            "id",
            "order",
            "order_number",
            "user",
            "payment_method",
            "payment_status",
            "transaction_id",
            "amount",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "payment_status",
            "transaction_id",
            "amount",
            "created_at",
            "updated_at",
            "order_number",
        ]