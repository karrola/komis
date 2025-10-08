from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import AuthenticationForm

# klasy które automatycznie dodają wygląd inputów bootstrapa do formularzy
class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # najpierw wywołujemy standardowy konstruktor
        for field in self.fields.values():  # iterujemy po wszystkich polach
            field.widget.attrs.setdefault('class', 'form-control')

class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

# rejestracja
class UserForm(BootstrapModelForm, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "first_name", "last_name", "password1", "password2"]

# logowanie
class EmailAuthenticationForm(BootstrapForm, AuthenticationForm):
    username = forms.EmailField(label="Email")