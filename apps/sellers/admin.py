from django.contrib import admin

from apps.sellers.models import Seller


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Админ-панель для модели Seller"""

    list_display = (
        "user",
        "company_name",
        "name",
        "website_url",
        "phone_number",
        "description",
        "is_approved",
    )
    list_filter = ("company_name", "is_approved")
    search_fields = ("company_name", "description")
    raw_id_fields = ("user",)
