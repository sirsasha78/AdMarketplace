from django.http import HttpRequest
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema

from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer
from apps.profiles.models import ShippingAddress


tags = ["Profiles"]


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для просмотра, обновления и деактивации профиля пользователя.
    Предоставляет эндпоинт для получения и редактирования данных профиля
    текущего аутентифицированного пользователя. Также позволяет деактивировать
    учётную запись (мягкое удаление через флаг `is_active`)."""

    serializer_class = ProfileSerializer

    def get_object(self):
        """Возвращает объект профиля текущего пользователя."""

        user = self.request.user
        return user

    @extend_schema(
        summary="Получить профиль",
        description="Возвращает данные профиля текущего пользователя.",
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Обновить профиль",
        description="Обновляет персональные данные пользователя.",
        tags=tags,
    )
    def put(self, request: HttpRequest, *args, **kwargs) -> Response:
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Деактивировать учетную запись",
        description="Помечает пользователя как неактивного (`is_active=False`). Физическое удаление не происходит.",
        tags=tags,
    )
    def delete(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Деактивирует учётную запись пользователя.
        Обрабатывает DELETE-запрос, устанавливая флаг `is_active` в False.
        Учётная запись не удаляется физически, а помечается как неактивная."""

        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"message": "Учетная запись пользователя деактивирована"})


class ShippingAddressesView(generics.ListCreateAPIView):
    """ "Представление для отображения и создания адресов доставки.
    Позволяет аутентифицированному пользователю:
    - Получить список всех своих адресов доставки.
    - Создать новый адрес доставки.
    Возвращает только те адреса, которые принадлежат текущему пользователю."""

    serializer_class = ShippingAddressSerializer

    def get_queryset(self) -> QuerySet[ShippingAddress]:
        """Возвращает queryset с адресами доставки, связанными с текущим пользователем."""

        user = self.request.user
        return ShippingAddress.objects.filter(user=user)

    def perform_create(self, serializer: ShippingAddressSerializer):
        """Сохраняет адрес доставки, привязывая его к текущему пользователю."""

        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Отображение адресов доставки",
        description="Возвращает все адреса доставки, связанные с пользователем.",
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения списка адресов доставки.
        Использует стандартную логику ListAPIView, но с ограниченным queryset.
        Доступно только аутентифицированным пользователям."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создает адрес доставки",
        description="Позволяет пользователю создать адрес доставки.",
        tags=tags,
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос для создания нового адреса доставки.
        Данные валидируются через ShippingAddressSerializer.
        Новый адрес автоматически связывается с текущим пользователем."""

        return super().post(request, *args, **kwargs)


class ShippingAddressViewID(generics.RetrieveUpdateDestroyAPIView):
    """Представление для получения, обновления и удаления адреса доставки по идентификатору.
    Доступ разрешён только аутентифицированным пользователям.
    Пользователь может взаимодействовать только с собственными адресами доставки."""

    serializer_class = ShippingAddressSerializer

    def get_queryset(self) -> QuerySet[ShippingAddress]:
        """Возвращает queryset с адресами доставки, принадлежащими текущему пользователю."""

        return ShippingAddress.objects.filter(user=self.request.user)

    def get_object(self):
        """Получает объект адреса доставки по ID из queryset текущего пользователя.
        Если объект не найден, возбуждается исключение NotFound с детализированным сообщением.
        """

        queryset = self.get_queryset()
        obj = queryset.get_or_none(id=self.kwargs["id"])
        if not obj:
            raise NotFound({"message": "Адреса доставки не существует!"})
        return obj

    @extend_schema(
        summary="Получение адреса доставки по ID",
        description="Возвращает адрес доставки авторизованного пользователя по ID",
        tags=tags,
    )
    def get(self, request, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения адреса доставки.
        Использует стандартную логику RetrieveModelMixin, но с предварительной проверкой
        принадлежности адреса пользователю через get_object()."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Обновление адреса доставки по ID",
        description="Эндпоинт для обновления адреса доставки авторизованного пользователя по ID",
        tags=tags,
    )
    def put(self, request, *args, **kwargs) -> Response:
        """Обрабатывает PUT-запрос для полного обновления адреса доставки.
        Валидирует входные данные и сохраняет изменения. Доступ только к своим адресам.
        """

        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление адреса доставки по ID",
        description="Эндпоинт для удаление адреса доставки авторизованного пользователя по ID",
        tags=tags,
    )
    def delete(self, request, *args, **kwargs) -> Response:
        """Обрабатывает DELETE-запрос для удаления адреса доставки.
        Физическое удаление объекта из базы данных. Доступ только к своим адресам.
        Возвращает статус 204 No Content в случае успеха."""

        return super().delete(request, *args, **kwargs)
