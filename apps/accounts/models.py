from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.accounts.managers import CustomUserManager
from apps.common.models import IsDeletedModel
from apps.common.services.validators import IMAGE_VALIDATORS


ACCOUNT_TYPE_CHOICES = (
    ("SELLER", "Продавец"),
    ("BUYER", "Покупатель"),
)


class User(AbstractUser, IsDeletedModel):
    """Модель пользователя системы.
    Описывает пользователей платформы, включая их контактную информацию,
    аватар, тип учетной записи и основные атрибуты. Наследуется от стандартной
    модели пользователя Django (AbstractUser) и добавляет к ней дополнительные поля."""

    username = None
    phone_number = models.CharField(max_length=15, blank=True, verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        validators=IMAGE_VALIDATORS,
        verbose_name="Аватар",
    )
    account_type = models.CharField(
        max_length=6,
        choices=ACCOUNT_TYPE_CHOICES,
        db_index=True,
        default="BUYER",
        verbose_name="Тип учетной записи",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self) -> str:
        """Возвращает строковое представление пользователя."""

        return self.get_full_name() or self.email

    class Meta:
        """Мета-класс для настройки модели."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
