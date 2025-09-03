from django.urls import path
from . import views

urlpatterns = [
    path("", views.auth_page_view, name="auth_page"),
    path("sign_up/", views.sign_up_view, name="sign_up"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
