from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Offer
from django.core.paginator import Paginator
from .filters import OfferFilter
from .forms import CarForm, PriceForm

# Create your views here.

def home_view(request):
    offers = Offer.objects.filter(active = True, if_sold = False).select_related('car', 'seller')

    offer_filter = OfferFilter(request.GET, queryset=offers)
    filtered_count = offer_filter.qs.count()

    paginator = Paginator(offer_filter.qs, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    query_params.pop('page', None)  # usuwa page jeśli istnieje

    context = {
        'filter': offer_filter,
        'filtered_count': filtered_count,
        'page_obj': page_obj,
        'query_params': query_params.urlencode(),
    }

    return render(request, "main/home.html", context)

def offer_details_view(request, slug):
    offer = get_object_or_404(Offer, slug=slug)
    return render(request, 'main/offer_details.html', {'offer': offer})

def add_offer_car_view(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        if form.is_valid():
            print("valid")
            form = CarForm()
        else:
            print("no valid")
            print(form.errors)
    else:
        form = CarForm()

    return render(request, 'main/add_offer_car.html', {'form': form})

def add_offer_price_view(request):
    if request.method == "POST":
        form = PriceForm(request.POST)
        if form.is_valid():
            print("valid")
            form = PriceForm()
        else:
            print("no valid")
            print(form.errors)
    else:
        form = PriceForm()

    return render(request, 'main/add_offer_price.html', {'form': form})