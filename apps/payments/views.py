from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import (
    PaymentSerializer,
    CreatePaymentSerializer,
    UpdatePaymentStatusSerializer,
)


class CreatePaymentView(generics.CreateAPIView):

    serializer_class = CreatePaymentSerializer
    permission_classes = [IsAuthenticated]


class PaymentListView(generics.ListAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            Payment.objects
            .filter(order__user=self.request.user)
            .select_related("order")
        )


class PaymentDetailView(generics.RetrieveAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            Payment.objects
            .filter(order__user=self.request.user)
            .select_related("order")
        )


class VerifyPaymentView(generics.UpdateAPIView):

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Payment.objects.filter(
            order__user=self.request.user
        )

    def update(self, request, *args, **kwargs):

        payment = self.get_object()

        payment.payment_status = "SUCCESS"

        payment.save(
            update_fields=[
                "payment_status",
                "updated_at"
            ]
        )

        order = payment.order

        order.status = "CONFIRMED"

        order.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        serializer = self.get_serializer(payment)

        return Response(
            {
                "message": "Payment verified successfully.",
                "payment": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdatePaymentStatusView(generics.UpdateAPIView):

    serializer_class = UpdatePaymentStatusSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["patch"]

    def get_queryset(self):

        return (
            Payment.objects
            .filter(order__user=self.request.user)
            .select_related("order")
        )