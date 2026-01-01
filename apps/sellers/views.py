from django.http import HttpRequest
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from apps.sellers.models import Seller
from apps.sellers.serializers import SellerSerializer
from apps.accounts.models import User


tags = ["Sellers"]


class SellersView(generics.CreateAPIView):
    """Создаёт профиль продавца для текущего пользователя.
    Позволяет пользователю стать продавцом, заполнив информацию о компании.
    Если профиль уже существует — обновляется.
    Тип аккаунта автоматически меняется на 'SELLER'."""

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
