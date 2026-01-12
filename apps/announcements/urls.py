from django.urls import path

from apps.announcements.views import (
    CategoriesView,
    AnnouncementDetailView,
    AnnouncementsView,
    AnnouncementsByCategoryView,
    AnnouncementsBySellerView,
)


urlpatterns = [
    path("categories/", CategoriesView.as_view(), name="categories"),
    path(
        "categories/<slug:slug>/",
        AnnouncementsByCategoryView.as_view(),
        name="announcements_by_category",
    ),
    path(
        "sellers/<slug:slug>/",
        AnnouncementsBySellerView.as_view(),
        name="announcements_by_seller",
    ),
    path("announcements/", AnnouncementsView.as_view(), name="announcements"),
    path(
        "announcements/<slug:slug>/",
        AnnouncementDetailView.as_view(),
        name="announcement_detail",
    ),
]
