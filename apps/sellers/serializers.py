from rest_framework import serializers

from apps.sellers.models import Seller


class SellerSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Seller (Продавец).
    Преобразует данные модели продавца в формат JSON и обратно.
    Используется для представления и обновления информации о продавце
    в API. Обеспечивает валидацию полей и настраивает права доступа к данным."""

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации."""

        model = Seller
        fields = (
            "company_name",
            "name",
            "slug",
            "website_url",
            "phone_number",
            "description",
            "is_approved",
        )
        extra_kwargs = {
            "slug": {"read_only": True},
            "website_url": {"required": False, "allow_null": True},
            "is_approved": {"read_only": True},
        }
