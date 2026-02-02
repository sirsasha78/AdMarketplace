from django.urls import path

from apps.sellers.views import (
    SellersView,
    SellerAnnouncementsView,
    SellerAnnouncementView,
    SellerReviewsView,
    ReviewCreateView,
    ReviewDetailView,
)


urlpatterns = [
    path("", SellersView.as_view(), name="seller"),
    path("announcements/", SellerAnnouncementsView.as_view(), name="announcements"),
    path(
        "announcements/<slug:slug>/",
        SellerAnnouncementView.as_view(),
        name="announcement_detail",
    ),
    path("reviews/", ReviewCreateView.as_view(), name="create-review"),
    path("reviews/<slug:slug>/", SellerReviewsView.as_view(), name="reviews"),
    path("reviews-detail/<str:pk>/", ReviewDetailView.as_view(), name="review-detail"),
]
