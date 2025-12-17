from phonenumber_field.modelfields import PhoneNumberField
from autoslug import AutoSlugField
from django.db import models
from django.conf import settings

from apps.common.models import BaseModel


class Seller(BaseModel):
    """Модель продавца на маркетплейсе.
    Описывает профиль пользователя, зарегистрированного как продавец.
    Может представлять как компанию, так и физическое лицо.
    Связана с пользователем системы через отношение один-к-одному.
    Содержит информацию о продавце, контактные данные, статус проверки
    и техническое поле slug для формирования URL-адресов."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller",
        verbose_name="Пользователь",
    )
    company_name = models.CharField(
        max_length=255, blank=True, verbose_name="Название компании"
    )
    name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ФИО продавца"
    )

    def company_name_or_name(self) -> str:
        """Возвращает название компании или ФИО продавца."""

        return self.company_name or self.name or f"продавец_{self.user.id}"

    slug = AutoSlugField(
        populate_from="company_name_or_name",
        always_update=True,
        unique=True,
        verbose_name="URL",
    )
    website_url = models.URLField(blank=True, null=True, verbose_name="Сайт")
    phone_number = PhoneNumberField(verbose_name="Телефон")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание продавца"
    )
    is_approved = models.BooleanField(default=False, verbose_name="Проверен")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта продавца."""

        display_name = self.company_name or self.name or self.user.email
        if self.is_approved:
            return f"Продавец: {display_name} подтвержден"
        return f"Продавец: {display_name} не подтвержден"

    class Meta:
        """Мета-класс для настройки модели."""

        verbose_name = "Продавец"
        verbose_name_plural = "Продавцы"
