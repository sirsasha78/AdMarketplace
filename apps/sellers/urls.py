from django.urls import path

from apps.sellers.views import (
    SellersView,
    SellerAnnouncementsView,
    SellerAnnouncementView,
)


urlpatterns = [
    path("", SellersView.as_view(), name="seller"),
    path("announcements/", SellerAnnouncementsView.as_view(), name="announcements"),
    path(
        "announcements/<slug:slug>/",
        SellerAnnouncementView.as_view(),
        name="announcement_detail",
    ),
]
