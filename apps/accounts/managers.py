from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


class CustomUserManager(BaseUserManager):
    """Менеджер пользователей для кастомной модели User.
    Обеспечивает корректное создание обычных пользователей и суперпользователей
    с валидацией электронной почты, пароля, имени и фамилии. Используется в
    связке с кастомной моделью User, где email является идентификатором для входа."""

    def validate_user(self, first_name: str, last_name: str, email: str, password: str):
        """Выполняет валидацию обязательных полей при создании пользователя."""

        if not first_name:
            raise ValidationError("Пользователи должны указать свое имя")

        if not last_name:
            raise ValidationError("Пользователи должны указать свою фамилию")

        if not email:
            raise ValidationError("Пользователь должен иметь email.")

        email = self.normalize_email(email)
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError(
                "Вы должны указать действительный адрес электронной почты"
            )

        if not password:
            raise ValidationError("У пользователя должен быть пароль")

        user = self.model(first_name=first_name, last_name=last_name, email=email)
        try:
            validate_password(password, user)
        except ValidationError as e:
            raise ValidationError(f"Пароль недопустим: {'; '.join(e.messages)}")

    def validate_superuser(self, **extra_fields):
        """Проверяет и устанавливает обязательные атрибуты для суперпользователя."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError(
                "У суперпользователей должно быть значение is_staff=True"
            )
        if extra_fields.get("is_superuser") is not True:
            raise ValidationError("Суперпользователь должен иметь is_superuser=True.")
        return extra_fields

    def create_user(
        self, first_name: str, last_name: str, email: str, password: str, **extra_fields
    ):
        """Создаёт и сохраняет обычного пользователя с указанными данными."""

        self.validate_user(first_name, last_name, email, password)
        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, first_name: str, last_name: str, email: str, password: str, **extra_fields
    ):
        """Создаёт и сохраняет суперпользователя с правами администратора.
        Автоматически устанавливает флаги `is_staff` и `is_superuser` в `True`.
        Выполняет те же проверки, что и `create_user`, плюс дополнительные
        проверки для суперпользователя."""

        extra_fields = self.validate_superuser(**extra_fields)
        user = self.create_user(first_name, last_name, email, password, **extra_fields)

        return user
