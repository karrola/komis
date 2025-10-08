from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Car

# Create your views here.

def home_view(request):
    cars = Car.objects.all()
    return render(request, "main/home.html", {'cars': cars})

