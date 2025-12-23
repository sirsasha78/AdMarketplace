from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import CreateUserSerializer, MyTokenObtainPairSerializer


class RegisterAPIView(generics.CreateAPIView):
    """Эндпоинт для регистрации нового пользователя.
    Позволяет анонимным пользователям создать учётную запись
    с помощью электронной почты и пароля. При успешной регистрации
    возвращает данные нового пользователя (без пароля)."""

    serializer_class = CreateUserSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    """Представление для получения пары JWT-токенов (access и refresh) при аутентификации пользователя.
    Этот класс расширяет стандартное представление `TokenObtainPairView` из библиотеки `djangorestframework-simplejwt`
    и использует кастомный сериализатор `MyTokenObtainPairSerializer` для добавления дополнительных данных в токен,
    таких как роль пользователя, идентификатор или другие необходимые атрибуты."""

    serializer_class = MyTokenObtainPairSerializer
