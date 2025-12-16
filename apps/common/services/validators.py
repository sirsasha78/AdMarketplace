from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.files import File
from PIL import Image


def validate_image_size(value: File):
    """Проверяет размер изображения."""

    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("Размер изображения не может превышать 5 МБ.")


def validate_image_with_pillow(value: File):
    """Проверяет, что переданный файл является изображением."""

    try:
        img = Image.open(value)
        img.verify()
        value.seek(0)
    except Exception:
        raise ValidationError("Файл не является валидным изображением.")


IMAGE_VALIDATORS = [
    FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
    validate_image_size,
    validate_image_with_pillow,
]
