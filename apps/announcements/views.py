from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from django.db.models import QuerySet

from apps.announcements.serializers import CategorySerializer, AnnouncementSerializer
from apps.announcements.models import Category, Announcement
from apps.sellers.models import Seller
from apps.common.permissions import IsAdminOrReadOnly


tags = ["Announcements"]


class CategoriesView(generics.ListCreateAPIView):
    """Представление для работы со списком категорий объявлений.
    Поддерживает:
    - Получение списка всех категорий (GET-запрос).
    - Создание новой категории (POST-запрос)."""

    permission_classes = [IsAdminOrReadOnly]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    @extend_schema(
        summary="Получение списка категорий",
        description="Возвращает полный список всех категорий.",
        responses=CategorySerializer(many=True),
        tags=tags,
        operation_id="list_categories",
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения списка всех категорий."""

        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Создание новой категории",
        description="Позволяет создать новую категорию.",
        request=CategorySerializer,
        responses=CategorySerializer,
        tags=tags,
        operation_id="create_category",
    )
    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает POST-запрос для создания новой категории."""

        return super().post(request, *args, **kwargs)


class AnnouncementsByCategoryView(generics.ListAPIView):
    """Представление для получения списка объявлений по категории.
    Предоставляет API-эндпоинт для получения всех объявлений,
    относящихся к определённой категории, указанной по её slug."""

    permission_classes = [AllowAny]
    serializer_class = AnnouncementSerializer

    def get_object(self) -> Category:
        """Возвращает объект категории по slug из URL-параметров.
        Если категория с указанным slug не найдена, выбрасывается исключение NotFound.
        """

        category = Category.objects.get_or_none(slug=self.kwargs["slug"])
        if not category:
            raise NotFound({"message": "Категория не существует!"})
        return category

    def get_queryset(self) -> QuerySet[Announcement]:
        """Возвращает набор объявлений, относящихся к указанной категории."""

        category = self.get_object()
        return Announcement.objects.filter(category=category).select_related(
            "category", "seller", "seller__user"
        )

    @extend_schema(
        summary="Выбор объявлений по категории",
        description="Получить объявления из определенной категории.",
        operation_id="category_announcements",
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает HTTP GET-запрос для получения списка объявлений категории."""

        return super().get(request, *args, **kwargs)


class AnnouncementsView(generics.ListAPIView):
    """Представление для получения списка всех объявлений.
    Предоставляет API-эндпоинт, возвращающий полный список объявлений,
    доступных в системе. Поддерживает оптимизированный запрос к базе данных
    с предзагрузкой связанных объектов: категории, продавца и пользователя продавца."""

    permission_classes = [AllowAny]
    serializer_class = AnnouncementSerializer

    def get_queryset(self) -> QuerySet[Announcement]:
        """Возвращает QuerySet всех объявлений с предзагруженными связанными данными."""

        return Announcement.objects.all().select_related(
            "category", "seller", "seller__user"
        )

    @extend_schema(
        summary="Все объявления",
        description="Выводит все объявления",
        operation_id="all_announcements",
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает GET-запрос для получения списка всех объявлений."""

        return super().get(request, *args, **kwargs)


class AnnouncementsBySellerView(generics.ListAPIView):
    """Представление для получения списка объявлений определённого продавца.
    Предоставляет API-эндпоинт, возвращающий все объявления,
    принадлежащие продавцу, идентифицируемому по его slug.
    Доступен для всех пользователей (публичный)."""

    permission_classes = [AllowAny]
    serializer_class = AnnouncementSerializer

    def get_object(self) -> Seller:
        """Возвращает объект продавца по slug из URL-параметров.
        Метод пытается найти продавца с указанным slug. Если продавец не найден,
        выбрасывается исключение NotFound с понятным сообщением."""

        seller = Seller.objects.get_or_none(slug=self.kwargs["slug"])
        if not seller:
            raise NotFound({"message": "Продавца не существует!"})
        return seller

    def get_queryset(self) -> QuerySet[Announcement]:
        """Возвращает QuerySet объявлений, принадлежащих указанному продавцу."""

        seller = self.get_object()
        return Announcement.objects.filter(seller=seller).select_related(
            "category", "seller", "seller__user"
        )

    @extend_schema(
        summary="Объявления продавца",
        description="Выводит все объявления определенного продавца.",
        operation_id="seller_announcements",
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает HTTP GET-запрос для получения списка объявлений продавца."""

        return super().get(request, *args, **kwargs)


class AnnouncementDetailView(generics.RetrieveAPIView):
    """Представление для получения детальной информации об объявлении.
    Предоставляет API-эндпоинт, возвращающий полные сведения об объявлении
    по его уникальному идентификатору в виде slug. Доступен для всех пользователей.
    Если объявление с указанным slug не найдено, возвращается ошибка 404."""

    permission_classes = [AllowAny]
    serializer_class = AnnouncementSerializer

    def get_object(self) -> Announcement:
        """Возвращает объект объявления по его slug из URL-параметров.
        Пытается найти объявление с указанным slug. Если объект не найден,
        выбрасывается исключение `NotFound` с понятным сообщением об ошибке."""

        announcement = Announcement.objects.select_related(
            "category", "seller", "seller__user"
        ).get_or_none(slug=self.kwargs["slug"])

        if not announcement:
            raise NotFound({"message": "Объявления не существует!"})
        return announcement

    @extend_schema(
        summary="Информация об объявлении",
        description="Возвращает сведения об объявлении с помощью slug.",
        operation_id="announcement_detail",
        tags=tags,
    )
    def get(self, request: HttpRequest, *args, **kwargs) -> Response:
        """Обрабатывает HTTP GET-запрос для получения детальной информации об объявлении."""

        return super().get(request, *args, **kwargs)
