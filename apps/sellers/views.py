from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request

from apps.sellers.models import Seller, SellerReview
from apps.sellers.serializers import (
    SellerSerializer,
    SellerReviewSerializer,
    ReviewUpdateSerializer,
)
from apps.accounts.models import User
from apps.announcements.models import Category, Announcement
from apps.announcements.serializers import (
    AnnouncementSerializer,
    CreateAnnouncementSerializer,
)
from apps.common.services.utils import set_dict_attr
from apps.common.permissions import IsSeller, IsOwnerOrReadOnly, IsAdminOrReadOnly
from apps.common.paginations import CustomPagination


tags = ["Sellers"]


class SellersView(generics.ListCreateAPIView):
    """Представление для получения списка всех продавцов и создания/обновления профиля продавца.
    Данный класс реализует API-эндпоинт, который позволяет:
    - Получать список всех продавцов с поддержкой пагинации.
    - Создавать или обновлять профиль продавца для текущего пользователя.

    При создании профиля автоматически изменяется тип аккаунта пользователя на 'SELLER'.
    Если профиль продавца уже существует, он обновляется.
    Атрибуты:
        queryset (QuerySet): Набор объектов модели Seller для отображения.
        permission_classes (list): Список классов разрешений. Доступ к созданию
            отзыва имеют только аутентифицированные пользователи.
        serializer_class (Serializer): Сериализатор для преобразования данных о продавце.
        pagination_class (Pagination): Класс пагинации для постраничного вывода."""

    queryset = Seller.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SellerSerializer
    pagination_class = CustomPagination

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
        summary="Все продавцы",
        description="Этот эндопоинт возвращает всех продавцов.",
        operation_id="all_sellers",
        tags=tags,
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения списка всех продавцов."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создать профиль продавца",
        description="Позволяет пользователю создать или обновить профиль продавца.",
        request=SellerSerializer,
        responses=SellerSerializer,
        operation_id="create_or_update_seller_profile",
        tags=tags,
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос для создания/обновления профиля продавца."""

        return super().post(request, *args, **kwargs)


class SellerAnnouncementsView(generics.ListCreateAPIView):
    """Представление для управления объявлениями продавца.
    Данный эндпоинт позволяет:
    - Получить список всех объявлений текущего продавца (GET-запрос).
    - Создать новое объявление от имени продавца (POST-запрос).
    Поддерживает:
    - Пагинацию (?page=2&page_size=50)"""

    permission_classes = [IsSeller]
    pagination_class = CustomPagination

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
    def get(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения списка объявлений продавца."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создать объявление",
        description="Этот эндопоинт позволяет продавцу создавать объявления",
        request=CreateAnnouncementSerializer,
        responses=AnnouncementSerializer,
        tags=tags,
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
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
    def put(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает HTTP PUT-запрос для полного обновления объявления."""

        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Частичное обновление объявления",
        request=CreateAnnouncementSerializer,
        responses=CreateAnnouncementSerializer,
        tags=tags,
    )
    def patch(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает HTTP PATCH-запрос для частичного обновления объявления.
        Использует стандартную логику UpdateModelMixin."""

        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Удалить объявление",
        description="Удаляет объявление продавца.",
        tags=tags,
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает HTTP DELETE-запрос для удаления объявления."""

        return super().delete(request, *args, **kwargs)


class SellerReviewsView(generics.ListAPIView):
    """Представление для получения списка отзывов на продавца.
    Предоставляет API-эндпоинт, возвращающий все активные отзывы,
    оставленные покупателями на конкретного продавца. Поддерживает
    постраничный вывод данных с использованием кастомной пагинации.
    Атрибуты:
        serializer_class (Serializer): Сериализатор для преобразования
            объектов отзывов в формат JSON.
        permission_classes (list): Разрешения доступа — доступ разрешён всем.
        pagination_class (Pagination): Класс пагинации с возможностью
            управления количеством элементов на странице через параметр
            `page_size` в запросе."""

    serializer_class = SellerReviewSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_object(self) -> Seller:
        """Возвращает объект продавца по его slug из URL.
        Получает продавца из базы данных по значению параметра `slug`.
        Если продавец не найден, вызывает исключение NotFound."""

        seller = Seller.objects.get_or_none(slug=self.kwargs["slug"])
        if not seller:
            raise NotFound({"message": "Продавец не существует"})
        return seller

    def get_queryset(self) -> QuerySet[SellerReview]:
        """Возвращает QuerySet всех активных отзывов на продавца.
        Формирует список отзывов, связанных с продавцом, полученном
        через метод get_object. Исключает удалённые отзывы (is_deleted=True)."""

        seller = self.get_object()
        reviews = SellerReview.objects.filter(seller=seller, is_deleted=False).order_by(
            "-created_at"
        )
        return reviews

    @extend_schema(
        summary="Получение отзывов",
        description="Этот эндопоинт возвращает все отзывы на конкретного продавца",
        tags=tags,
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает HTTP GET-запрос для получения списка отзывов."""

        return super().get(request, *args, **kwargs)


class ReviewCreateView(generics.CreateAPIView):
    """Представление для создания отзыва на продавца.
    Предоставляет API-эндпоинт, позволяющий авторизованным пользователям
    оставлять отзывы на продавцов. Использует сериализатор для валидации
    входных данных и автоматически связывает отзыв с текущим пользователем
    как покупателем (buyer). Поддерживает документацию через drf-spectacular.
    Атрибуты:
        serializer_class (Serializer): Сериализатор, используемый для валидации
            и сохранения данных отзыва. Ожидается, что он обрабатывает поля
            отзыва и корректно устанавливает связь с покупателем.
        permission_classes (list): Список классов разрешений. Доступ к созданию
            отзыва имеют только аутентифицированные пользователи."""

    serializer_class = SellerReviewSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создание отзыва",
        description="Эндопоинт для создание отзывов",
        request=SellerReviewSerializer,
        responses=SellerReviewSerializer,
        tags=tags,
    )
    def post(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает HTTP POST-запрос для создания нового отзыва."""

        return super().post(request, *args, **kwargs)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для просмотра, изменения и удаления отзыва продавца.
    Предоставляет эндпоинты для получения, полного обновления и удаления
    конкретного отзыва о продавце. Использует мягкое удаление — отзыв
    помечается как удалённый (is_deleted=True), но не удаляется из базы данных.
    Атрибуты:
        queryset (QuerySet): Набор объектов SellerReview, исключая удалённые.
        serializer_class (Serializer): Сериализатор для валидации и
            преобразования данных при обновлении отзыва.
        permission_classes (list): Классы разрешений, определяющие,
            кто может выполнять действия. Владелец отзыва может
            редактировать и удалять, остальные — только читать."""

    queryset = SellerReview.objects.filter(is_deleted=False)
    serializer_class = ReviewUpdateSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @extend_schema(
        summary="Получение отзыва",
        description="Возвращает данные одного отзыва.",
        tags=tags,
    )
    def get(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения данных одного отзыва.
        Возвращает сериализованные данные отзыва, если он существует
        и не помечен как удалённый. Доступно всем пользователям."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Изменение отзыва",
        description="Позволяет владельцу изменить текст или рейтинг отзыва.",
        tags=tags,
    )
    def put(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает PUT-запрос для полного обновления отзыва.
        Обновляет все поля отзыва новыми значениями. Доступно только
        владельцу отзыва. При успешном обновлении возвращает обновлённые данные."""

        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Удаление отзыва",
        description="Помечает отзыв как удалённый (мягкое удаление).",
        tags=tags,
    )
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """Обрабатывает DELETE-запрос для удаления отзыва.
        Помечает отзыв как удалённый (устанавливает is_deleted=True),
        фактически не удаляя его из базы данных. Доступно только владельцу."""

        return super().delete(request, *args, **kwargs)
