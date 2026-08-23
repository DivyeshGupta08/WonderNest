from rest_framework import serializers

from .models import Payment
from apps.orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):

    # Keep API field name as "status"
    # but connect it to model field "payment_status"
    status = serializers.CharField(
        source="payment_status",
        read_only=True
    )

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

        user = self.context["request"].user
        order = validated_data["order"]

        payment = Payment.objects.create(
            user=user,
            order=order,
            amount=order.total_amount,
            payment_method=validated_data["payment_method"],
            payment_status="PENDING",
        )

        return payment


class UpdatePaymentStatusSerializer(serializers.Serializer):

    status = serializers.ChoiceField(
        source="payment_status",
        choices=[
            ("PENDING", "Pending"),
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
        ]
    )

    def update(self, instance, validated_data):

        new_status = validated_data["payment_status"]

        instance.payment_status = new_status

        instance.save(
            update_fields=[
                "payment_status",
                "updated_at"
            ]
        )

        if new_status == "SUCCESS":

            instance.order.status = "CONFIRMED"

            instance.order.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )

        elif new_status == "FAILED":

            instance.order.status = "PENDING"

            instance.order.save(
                update_fields=[
                    "status",
                    "updated_at"
                ]
            )

        return instance