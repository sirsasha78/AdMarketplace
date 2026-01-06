from django.urls import path

from apps.announcements.views import CategoriesView


urlpatterns = [
    path("categories/", CategoriesView.as_view(), name="categories"),
]
