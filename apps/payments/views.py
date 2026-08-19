from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.orders.models import Order

from .models import Payment
from .serializers import PaymentSerializer


class CreatePaymentView(generics.CreateAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        order_id = request.data.get("order")

        if not order_id:
            raise ValidationError(
                {"order": "Order ID is required."}
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            raise ValidationError(
                {"order": "Order not found or does not belong to you."}
            )

        if hasattr(order, "payment"):
            raise ValidationError(
                {"order": "Payment already exists for this order."}
            )

        if order.status == "CANCELLED":
            raise ValidationError(
                {"order": "Cannot create payment for a cancelled order."}
            )

        payment = Payment.objects.create(
            user=request.user,
            order=order,
            payment_method=request.data.get("payment_method"),
            amount=order.total_amount,
            payment_status="PENDING"
        )

        serializer = self.get_serializer(payment)

        return Response(
            serializer.data,
            status=201
        )