from django.contrib import admin

from apps.announcements.models import Announcement


@admin.register(Announcement)
class AdminAnnouncement(admin.ModelAdmin):
    """Админ-панель для объявлений"""

    list_display = (
        "title",
        "description",
        "price",
        "category",
        "seller",
        "condition",
        "image",
    )
    list_filter = ("category", "price", "seller")
    search_fields = ("title", "description")
    raw_id_fields = ("seller",)
