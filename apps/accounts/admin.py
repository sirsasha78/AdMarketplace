from django.contrib import admin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель для модели User."""

    list_display = ("username", "phone_number", "email", "account_type")
