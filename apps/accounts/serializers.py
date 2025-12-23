from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

from apps.accounts.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя.
    Поддерживает:
    - Валидацию пароля через стандартные валидаторы Django
    - Подтверждение пароля
    - Выбор типа аккаунта (покупатель/продавец)
    Пароль и подтверждение доступны только для записи."""

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        """Метаданные сериализатора."""

        model = get_user_model()
        fields = ("email", "password", "confirm_password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value: str) -> str:
        """Валидирует пароль с использованием стандартных валидаторов Django."""

        validate_password(value)
        return value

    def validate(self, attrs: dict) -> dict:
        """Проверяет совпадение пароля и подтверждения пароля."""

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data: dict) -> User:
        """Создаёт нового пользователя с захешированным паролем."""

        validated_data.pop("confirm_password")
        user = User(email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для получения пары JWT-токенов (access и refresh).
    Добавляет в токен дополнительные данные пользователя:
    - Группу (admin/user)
    - Роль (тип аккаунта: BUYER, SELLER и т.д.)
    - Издателя токена (iss)
    Используется при аутентификации пользователя для расширения стандартного набора claims.
    """

    @classmethod
    def get_token(cls, user: User):
        """Создаёт и возвращает JWT-токен с дополнительными данными пользователя."""

        token = super().get_token(user)

        if user.is_staff:
            token["group"] = "admin"
        else:
            token["group"] = "user"
            token["role"] = user.account_type
        token["iss"] = "http://127.0.0.1:8001"
        return token
