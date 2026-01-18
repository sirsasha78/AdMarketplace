from django.http import HttpRequest
from rest_framework import permissions
from rest_framework.views import View

from typing import Any


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
