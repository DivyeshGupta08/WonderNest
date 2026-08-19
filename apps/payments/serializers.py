from rest_framework import serializers

from .models import Payment
from apps.orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "amount",
            "status",
            "transaction_id",
            "created_at",
            "updated_at",
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = [
            "order",
            "payment_method",
        ]

    def validate_order(self, order):

        user = self.context["request"].user

        if order.user != user:
            raise serializers.ValidationError(
                "You cannot make payment for this order."
            )

        if order.status == "CANCELLED":
            raise serializers.ValidationError(
                "Payment cannot be made for a cancelled order."
            )

        return order

    def create(self, validated_data):

        order = validated_data["order"]

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            payment_method=validated_data["payment_method"],
            status="PENDING",
        )

        return payment