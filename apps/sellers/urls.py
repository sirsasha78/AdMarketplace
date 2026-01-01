from django.urls import path

from apps.sellers.views import SellersView


urlpatterns = [
    path("", SellersView.as_view(), name="seller"),
]
