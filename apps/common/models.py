import uuid
from django.db import models
from django.utils import timezone

from apps.common.managers import GetOrNoneManager, IsDeletedManager


class BaseModel(models.Model):
    """Абстрактная модель, предоставляющая базовые поля для всех моделей приложения."""

    id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        verbose_name="Идентификатор",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    objects = GetOrNoneManager()

    class Meta:
        """Мета-класс для настройки модели."""

        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
        ]


class IsDeletedModel(BaseModel):
    """Абстрактная модель, добавляющая функциональность мягкого удаления к дочерним моделям."""

    is_deleted = models.BooleanField(
        default=False, db_index=True, verbose_name="Помечен как удалённый"
    )
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата удаления"
    )

    objects = IsDeletedManager()

    class Meta:
        """Мета-класс для настройки модели."""

        abstract = True

    def delete(self, *args, **kwargs):
        """Помечает объект как удалённый, устанавливая флаг is_deleted и время удаления."""

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def hard_delete(self, *args, **kwargs):
        """Выполняет полное (жёсткое) удаление объекта из базы данных."""

        super().delete(*args, **kwargs)

    def restore(self):
        """Восстанавливает объект, снимая метку удаления."""

        if self.is_deleted:
            self.is_deleted = False
            self.deleted_at = None
            self.save(update_fields=["is_deleted", "deleted_at"])
