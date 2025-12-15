from django.db import models
from django.utils import timezone


class GetOrNoneQuerySet(models.QuerySet):
    """Расширение стандартного QuerySet Django с добавлением метода get_or_none.
    Данный класс предоставляет удобный способ получения объекта из базы данных
    по заданным критериям, возвращая None вместо выброса исключения,
    если объект не найден."""

    def get_or_none(self, **kwargs) -> models.Model | None:
        """Возвращает объект, соответствующий заданным параметрам, или None, если объект не найден."""

        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class GetOrNoneManager(models.Manager):
    """Кастомный менеджер модели, расширяющий функциональность стандартного Manager,
    чтобы добавить метод `get_or_none`, возвращающий объект или None, если объект не найден.
    """

    def get_queryset(self) -> GetOrNoneQuerySet:
        """Возвращает кастомный QuerySet, предоставляющий дополнительные методы,
        такие как `get_or_none`."""

        return GetOrNoneQuerySet(self.model)

    def get_or_none(self, **kwargs) -> models.Model | None:
        """Возвращает объект, соответствующий заданным параметрам, или None, если объект не найден."""

        return self.get_queryset().get_or_none()


class IsDeletedQuerySet(GetOrNoneQuerySet):
    """Расширение QuerySet для поддержки мягкого удаления объектов.
    Данный класс добавляет возможность мягкого удаления (пометка как удалённого)
    вместо физического удаления записей из базы данных. При мягком удалении
    устанавливается флаг `is_deleted` и время `deleted_at`, тогда как при
    жёстком удалении записи удаляются стандартным способом через родительский класс."""

    def delete(self, hard_delete=False) -> tuple[int, dict[str, int]]:
        """Выполняет удаление объектов в queryset."""

        if hard_delete:
            return super().delete()
        else:
            return self.update(is_deleted=True, deleted_at=timezone.now())

    def restore(self) -> int:
        """Восстанавливает все удалённые объекты в QuerySet, снимая флаг is_deleted
        и обнуляя deleted_at. Операция выполняется на уровне БД (массовое обновление).
        Возвращает количество затронутых объектов."""

        return self.update(is_deleted=False, deleted_at=None)


class IsDeletedManager(GetOrNoneManager):
    """Менеджер модели, фильтрующий объекты по флагу `is_deleted`.
    Этот менеджер используется для работы с моделями, поддерживающими мягкое удаление
    (логическое удаление через поле `is_deleted`). По умолчанию возвращает только
    неудалённые объекты. Предоставляет методы для доступа ко всем объектам, включая удалённые,
    а также для выполнения физического удаления."""

    def get_queryset(self) -> IsDeletedQuerySet:
        """Возвращает QuerySet, содержащий только неудалённые объекты."""

        return IsDeletedQuerySet(self.model).filter(is_deleted=False)

    def unfiltered(self) -> IsDeletedQuerySet:
        """Возвращает QuerySet со всеми объектами модели, включая удалённые."""

        return IsDeletedQuerySet(self.model)

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        """Выполняет полное (жёсткое) удаление всех объектов в QuerySet, включая удалённые."""

        return self.unfiltered().delete(hard_delete=True)
