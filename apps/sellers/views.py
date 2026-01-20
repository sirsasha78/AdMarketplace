from django.db.models import QuerySet
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from apps.sellers.models import Seller
from apps.sellers.serializers import SellerSerializer
from apps.accounts.models import User
from apps.announcements.models import Category, Announcement
from apps.announcements.serializers import (
    AnnouncementSerializer,
    CreateAnnouncementSerializer,
)
from apps.common.services.utils import set_dict_attr
from apps.common.permissions import IsSeller


tags = ["Sellers"]


class SellersView(generics.CreateAPIView):
    """Создаёт профиль продавца для текущего пользователя.
    Позволяет пользователю стать продавцом, заполнив информацию о компании.
    Если профиль уже существует — обновляется.
    Тип аккаунта автоматически меняется на 'SELLER'."""

    permission_classes = [IsAuthenticated]
    serializer_class = SellerSerializer

    def perform_create(self, serializer: SellerSerializer) -> Seller:
        """Создаёт или обновляет профиль продавца для пользователя.
        Автоматически устанавливает account_type = 'SELLER'."""

        user = self.request.user
        seller, _ = Seller.objects.update_or_create(
            user=user, defaults=serializer.validated_data
        )

        if user.account_type != User.ACCOUNT_TYPE_SELLER:
            user.account_type = User.ACCOUNT_TYPE_SELLER
            user.save(update_fields=["account_type"])
        return seller

    @extend_schema(
        summary="Создать профиль продавца",
        description="Позволяет пользователю создать или обновить профиль продавца.",
        request=SellerSerializer,
        responses=SellerSerializer,
        operation_id="create_or_update_seller_profile",
        tags=tags,
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос для создания/обновления профиля продавца."""

        return super().post(request, *args, **kwargs)


class SellerAnnouncementsView(generics.ListCreateAPIView):
    """Представление для управления объявлениями продавца.
    Данный эндпоинт позволяет:
    - Получить список всех объявлений текущего продавца (GET-запрос).
    - Создать новое объявление от имени продавца (POST-запрос)."""

    permission_classes = [IsSeller]

    def get_object(self) -> Seller:
        """Возвращает профиль продавца текущего пользователя."""

        obj = Seller.objects.get_or_none(user=self.request.user, is_approved=True)
        if not obj:
            raise NotFound({"message": "Профиль продавца не найден."})
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self) -> QuerySet[Announcement]:
        """Возвращает queryset объявлений, принадлежащих текущему продавцу."""

        seller = self.get_object()
        return Announcement.objects.filter(seller=seller).select_related(
            "category", "seller__user"
        )

    def get_serializer_class(self):
        """Определяет класс сериализатора в зависимости от HTTP-метода запроса."""

        if self.request.method == "POST":
            return CreateAnnouncementSerializer
        return AnnouncementSerializer

    def perform_create(self, serializer: CreateAnnouncementSerializer):
        """Выполняет создание нового объявления.
        Извлекает валидированные данные из сериализатора, определяет категорию
        по её slug и устанавливает продавца. Затем создаёт объект объявления."""

        data = serializer.validated_data
        category_slug = data.pop("category_slug")
        category = Category.objects.get(slug=category_slug)
        seller = self.get_object()
        data["category"] = category
        data["seller"] = seller
        Announcement.objects.create(**data)

    @extend_schema(
        summary="Получить объявления продавца",
        description="Этот эндопоинт возвращает все объявления продавца.",
        responses=AnnouncementSerializer(many=True),
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения списка объявлений продавца."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создать объявление",
        description="Этот эндопоинт позволяет продавцу создавать объявления",
        request=CreateAnnouncementSerializer,
        responses=AnnouncementSerializer,
        tags=tags,
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос для создания нового объявления."""

        return super().post(request, *args, **kwargs)


class SellerAnnouncementView(
    mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    """Представление для обновления и удаления объявления продавца.
    Поддерживает:
    - PUT/PATCH — полное/частичное обновление объявления,
    - DELETE — удаление объявления.
    Доступ только владельцу."""

    permission_classes = [IsSeller]
    serializer_class = CreateAnnouncementSerializer

    def get_object(self):
        """Возвращает объект объявления по его slug, если он существует и принадлежит текущему продавцу.
        Проверяет:
        - Существование объявления с указанным slug.
        - Принадлежность объявления текущему пользователю (через связь с продавцом)."""

        obj = Announcement.objects.get_or_none(slug=self.kwargs["slug"])
        if not obj:
            raise NotFound({"message": "Объявления не существует!"})
        elif obj.seller != self.request.user.seller:
            raise NotFound({"message": "Объявления не существует!"})
        return obj

    def perform_update(self, serializer: CreateAnnouncementSerializer):
        """Выполняет обновление объекта объявления после валидации данных.
        Извлекает валидированные данные из сериализатора, определяет категорию
        по её slug, обновляет поля объекта объявления и сохраняет изменения в базу данных.
        Использует вспомогательную функцию set_dict_attr для массового присвоения полей.
        """

        announcement = self.get_object()
        data = serializer.validated_data
        category_slug = data.pop("category_slug")
        category = Category.objects.get(slug=category_slug)
        data["category"] = category
        set_dict_attr(announcement, data)
        announcement.save()

    @extend_schema(
        summary="Полное обновление объявления",
        description="Заменяет все поля объявления.",
        request=CreateAnnouncementSerializer,
        responses=CreateAnnouncementSerializer,
        tags=tags,
    )
    def put(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает HTTP PUT-запрос для полного обновления объявления."""

        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление объявления",
        request=CreateAnnouncementSerializer,
        responses=CreateAnnouncementSerializer,
        tags=tags,
    )
    def patch(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает HTTP PATCH-запрос для частичного обновления объявления.
        Использует стандартную логику UpdateModelMixin."""

        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить объявление",
        description="Удаляет объявление продавца.",
        tags=tags,
    )
    def delete(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает HTTP DELETE-запрос для удаления объявления."""

        return super().delete(request, *args, **kwargs)
