from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from apps.announcements.serializers import CategorySerializer
from apps.announcements.models import Category


tags = ["Announcements"]


class CategoriesView(generics.ListCreateAPIView):
    """Представление для работы со списком категорий объявлений.
    Поддерживает:
    - Получение списка всех категорий (GET-запрос).
    - Создание новой категории (POST-запрос)."""

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
