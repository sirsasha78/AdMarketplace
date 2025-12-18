from autoslug import AutoSlugField
from django.db import models

from apps.common.models import BaseModel, IsDeletedModel
from apps.common.services.validators import IMAGE_VALIDATORS
from apps.sellers.models import Seller


CONDITION_TYPE_CHOICES = (
    ("NEW", "Новый"),
    ("USED", "Подержанный"),
)


class Category(BaseModel):
    """Модель категории для классификации объявлений на маркетплейсе.
    Описывает категорию, к которой может быть отнесено объявление.
    Каждая категория имеет уникальное название и slug для формирования URL.
    Также может иметь изображение, отображаемое в интерфейсе."""

    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")
    slug = AutoSlugField(
        populate_from="name", unique=True, always_update=True, verbose_name="URL"
    )
    image = models.ImageField(
        upload_to="category_images/", validators=IMAGE_VALIDATORS, verbose_name="Фото"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление объекта категории."""

        return self.name

    class Meta:
        """Мета-класс для настройки поведения модели."""

        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Announcement(IsDeletedModel):
    """Модель объявления для платформы объявлений.
    Хранит информацию о товаре или услуге, выставленной на продажу.
    Поддерживает возможность привязки к категории и продавцу,
    а также хранит основные атрибуты: название, описание, цену, состояние и изображение.
    Поле `slug` генерируется автоматически на основе заголовка для использования в URL.
    При удалении продавца поле `seller` становится NULL, но объявление сохраняется."""

    title = models.CharField(max_length=255, verbose_name="Название")
    slug = AutoSlugField(
        populate_from="title", unique=True, db_index=True, verbose_name="URL"
    )
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name="Категория",
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="announcements",
        verbose_name="Продавец",
    )
    condition = models.CharField(
        max_length=11,
        choices=CONDITION_TYPE_CHOICES,
        db_index=True,
        verbose_name="Состояние",
    )
    image = models.ImageField(
        upload_to="announcement_images/",
        validators=IMAGE_VALIDATORS,
        verbose_name="Изображение",
    )

    def __str__(self) -> str:
        """Возвращает строковое представление объекта объявления."""

        return self.title

    class Meta:
        """Метакласс для настройки модели."""

        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
