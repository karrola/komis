from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class UserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "first_name", "last_name", "password1", "password2"]
        labels = {
            "username": "Nazwa użytkownika",  # zamiast Email
        }

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")