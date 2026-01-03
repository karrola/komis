from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("offer/<slug:slug>/", views.offer_details_view, name="offer-details"),
    path("add-offer/car/", views.add_offer_car_view, name="add-offer-car"),
    path("add-offer/price/", views.add_offer_price_view, name="add-offer-price"),
    path("my-offers/", views.my_offers_view, name="my-offers"),
    path("end-offer/<slug:slug>/", views.end_offer_view, name="end-offer"),
] 
