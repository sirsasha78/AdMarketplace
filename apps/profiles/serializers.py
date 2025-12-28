from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.profiles.models import ShippingAddress


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для представления и обновления профиля пользователя.
    Преобразует модель пользователя в JSON-формат и обратно,
    включая основные персональные данные и информацию о типе аккаунта.
    Поле электронной почты и тип аккаунта доступны только для чтения,
    аватар — необязательное поле."""

    class Meta:
        """Метакласс сериализатора, определяющий модель и поля для сериализации."""

        model = get_user_model()
        fields = ("first_name", "last_name", "email", "avatar", "account_type")
        extra_kwargs = {
            "email": {"read_only": True},
            "avatar": {"required": False},
            "account_type": {"read_only": True},
        }


class ShippingAddressSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShippingAddress.
    Преобразует данные модели адреса доставки в JSON-формат и обратно.
    Используется при создании, чтении и обновлении адресов доставки.
    Обеспечивает валидацию полей и настраивает права доступа к данным."""

    class Meta:
        """Метакласс сериализатора."""

        model = ShippingAddress
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "zipcode",
        )
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def validate(self, attrs: dict) -> dict:
        """Проверяет, что у пользователя не существует адреса доставки с такими же данными.
        Осуществляет дополнительную валидацию на уровне сериализатора, предотвращая
        создание дублирующихся адресов доставки для одного и того же пользователя."""

        user = self.context["request"].user
        if ShippingAddress.objects.filter(user=user, **attrs).exists():
            raise serializers.ValidationError("Такой адрес доставки уже существует.")
        return attrs
