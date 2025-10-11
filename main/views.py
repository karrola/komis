from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Car, Offer

# Create your views here.

def home_view(request):
    offers = Offer.objects.filter(active = True, if_sold = False).all()
    return render(request, "main/home.html", {'offers': offers})

