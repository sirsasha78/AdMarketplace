from django.urls import path

from apps.profiles.views import (
    ProfileView,
    ShippingAddressesView,
    ShippingAddressViewID,
)


urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path(
        "shipping_addresses/",
        ShippingAddressesView.as_view(),
        name="shipping_addresses",
    ),
    path(
        "shipping_addresses/detail/<str:id>/",
        ShippingAddressViewID.as_view(),
        name="shipping_addresses_detail",
    ),
]
