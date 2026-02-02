from rest_framework import serializers

from apps.sellers.models import Seller, SellerReview


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


class SellerReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и валидации отзыва пользователя на продавца.
    Предоставляет функциональность для:
    - Валидации данных при создании отзыва,
    - Проверки уникальности отзыва (один активный отзыв от пользователя на одного продавца),
    - Валидации рейтинга в допустимом диапазоне (от 1 до 5),
    - Поддержки мягкого удаления: позволяет оставить новый отзыв,
      если предыдущий был помечен как удалённый (is_deleted=True).
    Используется в представлениях для обработки входящих данных
    при создании нового отзыва на продавца."""

    seller = serializers.SlugRelatedField(
        slug_field="slug", queryset=Seller.objects.all()
    )

    class Meta:
        """Метакласс сериализатора."""

        model = SellerReview
        fields = ("id", "seller", "rating", "text")
        extra_kwargs = {
            "text": {"allow_blank": True, "required": False},
        }

    def create(self, validated_data: dict) -> SellerReview:
        """Создаёт новый отзыв на продавца после проверки уникальности.
        Проверяет, существует ли уже неудалённый отзыв от текущего пользователя
        на указанного продавца. Если такой отзыв найден, вызывается ошибка валидации.
        В противном случае создаётся новый отзыв, привязанный к текущему пользователю.
        """

        user = self.context["request"].user
        seller = validated_data["seller"]

        review = SellerReview.objects.filter(
            user=user, seller=seller, is_deleted=False
        ).exists()
        if review:
            raise serializers.ValidationError(
                {"non_field_errors": "Вы уже оставили отзыв на этого продавца."}
            )
        return SellerReview.objects.create(user=user, **validated_data)

    def validate_rating(self, value: int) -> int:
        """Валидирует значение рейтинга отзыва.
        Проверяет, что переданное значение находится в диапазоне от 1 до 5 включительно.
        Если значение вне допустимого диапазона, вызывается ошибка валидации."""

        if not 1 <= value <= 5:
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 5.")
        return value


class ReviewUpdateSerializer(SellerReviewSerializer):
    """Сериализатор для обновления отзыва продавца.
    Наследуется от `SellerReviewSerializer` и добавляет дополнительную логику
    для безопасного обновления отзыва. Поле `seller` переопределено как только
    для чтения и возвращает слаг продавца, что предотвращает изменение связи
    с продавцом при обновлении отзыва через API.
    """

    seller = serializers.ReadOnlyField(source="seller.slug")
