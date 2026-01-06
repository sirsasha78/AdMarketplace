from rest_framework import serializers
from apps.announcements.models import Category, Announcement


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category.
    Преобразует данные модели категории в формат JSON и обратно.
    Используется для представления и валидации информации о категориях
    в API. Поддерживает только чтение поля slug — оно генерируется автоматически
    и не может быть изменено через API."""

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации."""

        model = Category
        fields = ("name", "slug", "image")
        extra_kwargs = {
            "slug": {"read_only": True},
        }


class SellerAnnouncementSerializer(serializers.Serializer):
    """Сериализатор для представления данных продавца в контексте объявления.
    Преобразует данные модели Seller в упрощённый формат, содержащий только
    необходимую информацию о продавце, такую как название компании, слаг и аватар.
    Используется для включения информации о продавце в ответы API, связанные с объявлениями.
    """

    name = serializers.CharField(source="company_name")
    slug = serializers.SlugField()
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        """Возвращает URL аватара продавца."""

        return obj.user.avatar.url if obj.user.avatar else None


class AnnouncementSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Announcement (Объявление).
    Преобразует данные модели объявления в формат JSON и обратно.
    Используется для представления и валидации информации об объявлении
    в API. Включает вложенные данные о продавце и категории."""

    seller = SellerAnnouncementSerializer()
    category = CategorySerializer()

    class Meta:
        """Метакласс сериализатора, определяющий модель и правила сериализации."""

        model = Announcement
        fields = (
            "title",
            "slug",
            "description",
            "price",
            "condition",
            "image",
            "seller",
            "category",
        )
        extra_kwargs = {
            "slug": {"read_only": True},
        }


class CreateAnnouncementSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объявления.
    Преобразует данные из формата JSON в объект модели Announcement и обратно.
    Используется в представлениях для валидации и сохранения новых объявлений.
    Поле 'category_slug' является write-only и используется для указания категории
    объявления по её slug. При валидации проверяется существование категории.
    После валидации объект категории устанавливается в поле 'category' модели Announcement.
    """

    category_slug = serializers.SlugField(write_only=True)

    class Meta:
        """Метакласс, определяющий модель и поля сериализатора."""

        model = Announcement
        fields = (
            "title",
            "category_slug",
            "description",
            "price",
            "condition",
            "image",
        )

    def validate_category_slug(self, value: str) -> str:
        """Валидирует slug категории."""

        if not Category.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Категория с таким slug не найдена.")
        return value
