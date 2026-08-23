from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for displaying payment information.

    API uses the field name 'status',
    while the database model uses 'payment_status'.
    """

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
    """
    Serializer used when creating a payment.
    """

    class Meta:
        model = Payment

        fields = [
            "order",
            "payment_method",
        ]

    def validate_order(self, order):
        """
        Make sure the logged-in user owns the order
        and the order has not been cancelled.
        """

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
        """
        Create a payment using the order's total amount.
        """

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
        choices=[
            ("PENDING", "Pending"),
            ("SUCCESS", "Success"),
            ("FAILED", "Failed"),
            ("REFUNDED", "Refunded"),
        ]
    )

    def update(self, instance, validated_data):

        new_status = validated_data["status"]

        # Payment model field is payment_status
        instance.payment_status = new_status

        instance.save(
            update_fields=[
                "payment_status",
                "updated_at",
            ]
        )

        # SUCCESS → Order becomes CONFIRMED
        if new_status == "SUCCESS":

            instance.order.status = "CONFIRMED"

            instance.order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        # FAILED → Order remains PENDING
        elif new_status == "FAILED":

            instance.order.status = "PENDING"

            instance.order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        # REFUNDED → Order becomes CANCELLED
        elif new_status == "REFUNDED":

            instance.order.status = "CANCELLED"

            instance.order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return {
            "id": instance.id,
            "status": instance.payment_status,
            "order": instance.order.id,
        }