import django_filters

from apps.announcements.models import Announcement


class AnnouncementFilter(django_filters.FilterSet):
    """Фильтр для модели Announcement, позволяющий фильтровать объявления по диапазону цен.
    Используется в представлениях на основе DRF, где требуется фильтрация по числовым диапазонам.
    Позволяет выполнять запросы вида:
        /api/announcements/?min_price=100&max_price=500"""

    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Минимальная цена",
        help_text="Объявления с ценой больше или равной указанной.",
        required=False,
    )
    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Максимальная цена",
        help_text="Объявления с ценой меньше или равной указанной.",
        required=False,
    )

    class Meta:
        """Метакласс, определяющий настройки фильтра."""

        model = Announcement
        fields = ["min_price", "max_price"]
