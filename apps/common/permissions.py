from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.views import View
from rest_framework.request import Request

from typing import Any
from apps.accounts.models import User


class IsOwner(permissions.BasePermission):
    """Пользовательское разрешение, позволяющее доступ только владельцам объекта или персоналу.
    Разрешение проверяет права доступа на двух уровнях:
    - На уровне запроса (has_permission): пользователь должен быть аутентифицирован.
    - На уровне объекта (has_object_permission): пользователь может взаимодействовать
      только с объектами, принадлежащими ему, либо быть сотрудником (staff).
    Используется для защиты представлений, где доступ к данным должен быть ограничен
    их владельцем. Администраторы (с атрибутом is_staff) имеют полный доступ."""

    def has_permission(self, request: HttpRequest, view: View) -> bool:
        """Проверяет, имеет ли пользователь право на выполнение запроса."""

        return request.user.is_authenticated

    def has_object_permission(self, request: HttpRequest, view: View, obj: Any) -> bool:
        """Проверяет, имеет ли пользователь право на взаимодействие с конкретным объектом."""

        if obj.user == request.user or request.user.is_staff:
            return True
        self.message = "У вас нет прав на доступ к этому объекту."
        return False


class IsSeller(permissions.BasePermission):
    """Пользовательское разрешение, позволяющее доступ только подтверждённым продавцам или персоналу.
    Разрешение проверяет права доступа на двух уровнях:
    - На уровне запроса (has_permission): пользователь должен быть аутентифицирован,
      иметь тип аккаунта "SELLER" и подтверждённый профиль продавца, либо быть сотрудником (is_staff).
    - На уровне объекта (has_object_permission): пользователь может взаимодействовать
      только с объектами, принадлежащими его профилю продавца, либо быть сотрудником (is_staff).
    Используется для защиты представлений, связанных с функционалом продавца,
    таких как управление товарами, объявлениями, заказами и статистикой.
    Администраторы (с атрибутом is_staff) имеют полный доступ ко всем объектам."""

    def has_permission(self, request: HttpRequest, view: View) -> bool:
        """Проверяет, имеет ли пользователь право на выполнение запроса."""

        if (
            request.user.is_authenticated
            and request.user.account_type == User.ACCOUNT_TYPE_SELLER
            and request.user.seller.is_approved
        ) or request.user.is_staff:
            return True
        return False

    def has_object_permission(self, request: HttpRequest, view: View, obj: Any) -> bool:
        """Проверяет, имеет ли пользователь право на взаимодействие с конкретным объектом."""

        if obj == request.user.seller or request.user.is_staff:
            return True
        self.message = "У вас нет прав на доступ к этому объекту."
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Пользовательское разрешение, разрешающее чтение всем, но запись — только администраторам.
    Разрешает выполнение безопасных HTTP-методов (GET, HEAD, OPTIONS) любым пользователям,
    включая неаутентифицированных.
    Для небезопасных методов (POST, PUT, PATCH, DELETE) требует, чтобы пользователь был
    аутентифицирован и являлся сотрудником (атрибут is_staff=True).
    Применяется для представлений, где данные должны быть доступны для просмотра всем,
    но защищены от изменений."""

    def has_permission(self, request: HttpRequest, view: View) -> bool:
        """Проверяет, имеет ли пользователь право на выполнение запроса."""

        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Пользовательское разрешение, позволяющее редактировать или удалять объект только его владельцу.
    Разрешает чтение (GET, HEAD, OPTIONS) всем пользователям.
    Запись (PUT, PATCH, DELETE) разрешена только владельцу объекта или персоналу (staff).
    Используется в представлениях, где важна защита данных от изменения посторонними пользователями.
    """

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """Проверяет, имеет ли пользователь право на выполнение операции над объектом."""

        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff
