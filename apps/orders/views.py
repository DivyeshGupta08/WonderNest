from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Order
from .serializers import (
    OrderSerializer,
    CreateOrderSerializer,
)


class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__product")
        )
        
class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["patch"]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("items__product")

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()

        new_status = request.data.get("status")

        allowed_statuses = [
            "PENDING",
            "CONFIRMED",
            "SHIPPED",
            "DELIVERED",
            "CANCELLED",
        ]

        if new_status not in allowed_statuses:
            return Response(
                {
                    "error": "Invalid order status.",
                    "allowed_statuses": allowed_statuses,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save(update_fields=["status", "updated_at"])

        return Response(
            OrderSerializer(
                order,
                context=self.get_serializer_context()
            ).data,
            status=status.HTTP_200_OK,
        )
        
class CancelOrderView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ["patch"]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("items__product")

    def partial_update(self, request, *args, **kwargs):
        from django.db import transaction

        order = self.get_object()

        if order.status != "PENDING":
            return Response(
                {
                    "error": "Only pending orders can be cancelled.",
                    "current_status": order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():

            for item in order.items.select_related("product"):

                if item.product:
                    item.product.stock += item.quantity

                    item.product.save(
                        update_fields=["stock"]
                    )

            order.status = "CANCELLED"

            order.save(
                update_fields=["status", "updated_at"]
            )

        return Response(
            OrderSerializer(
                order,
                context=self.get_serializer_context()
            ).data,
            status=status.HTTP_200_OK,
        )