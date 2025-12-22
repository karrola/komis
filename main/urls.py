from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("offer/<slug:slug>/", views.offer_details_view, name="offer-details"),
] 
