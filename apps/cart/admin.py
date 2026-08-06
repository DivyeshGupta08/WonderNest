from django.contrib import admin
from .models import Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "product",
        "quantity",
        "total_price",
        "added_at",
    )

    list_filter = (
        "added_at",
    )

    search_fields = (
        "user__username",
        "product__name",
    )

    readonly_fields = (
        "added_at",
    )

    ordering = (
        "-added_at",
    )