from django.contrib import admin

from apps.sellers.models import Seller, SellerReview


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    """Админ-панель для модели Seller"""

    list_display = (
        "id",
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


@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    """Админ-панель для модели SellerReview.
    Предоставляет интерфейс для управления отзывами на продавцов
    в административной панели Django. Позволяет просматривать,
    фильтровать и редактировать отзывы.
    """

    list_display = ("id", "user", "seller", "rating", "text")
