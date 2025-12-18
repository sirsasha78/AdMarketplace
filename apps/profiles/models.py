from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.conf import settings

from apps.common.models import BaseModel


class ShippingAddress(BaseModel):
    """Модель адреса доставки для пользователя.
    Хранит информацию об адресе, необходимую для доставки заказов:
    полное имя получателя, контактные данные и почтовый адрес.
    Связана с пользователем через внешний ключ. Один пользователь
    может иметь несколько адресов доставки."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shipping_addresses",
        verbose_name="Пользователь",
    )
    full_name = models.CharField(max_length=255, verbose_name="Полное имя получателя")
    email = models.EmailField(verbose_name="Электронная почта")
    phone = PhoneNumberField(verbose_name="Номер телефона")
    address = models.CharField(max_length=1000, verbose_name="Адрес")
    city = models.CharField(max_length=200, verbose_name="Город")
    country = models.CharField(max_length=200, verbose_name="Страна")
    zipcode = models.CharField(max_length=6, verbose_name="Почтовый индекс")

    def __str__(self) -> str:
        """Возвращает строковое представление объекта адреса доставки."""

        return f"Детали доставки для {self.full_name}"

    class Meta:
        """Мета-класс для настройки модели."""

        verbose_name = "Адрес доставки"
        verbose_name_plural = "Адреса доставки"
