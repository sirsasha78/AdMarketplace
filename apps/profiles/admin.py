from django.contrib import admin

from apps.profiles.models import ShippingAddress


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    """Админ-панель для модели ShippingAddress."""

    list_display = (
        "user",
        "full_name",
        "email",
        "phone",
        "address",
        "city",
        "country",
        "zipcode",
    )
    list_filter = ("city", "country", "user")
    search_fields = ("city", "address")
    raw_id_fields = ("user",)
