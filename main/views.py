from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Offer, Car
from django.core.paginator import Paginator
from .filters import OfferFilter
from .forms import CarForm, PriceForm, EndOfferForm
from django.utils import timezone
from .ml.predictor import predict_price

# Create your views here.

def home_view(request):
    offers = Offer.objects.filter(active = True, if_sold = False).select_related('car', 'seller')
    user = request.user
    user_offers = []
    favourites = []

    if user.is_authenticated:
        user_offers = user.offers.filter(active=True, if_sold=False)
        favourites = user.favourites.all()

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
        'user_offers': user_offers,
        'favourites': favourites,
    }

    return render(request, "main/home.html", context)

def offer_details_view(request, slug):
    offer = get_object_or_404(Offer, slug=slug)
    is_my_offer = (
        request.user.is_authenticated
        and offer.seller_id == request.user.id
    )
    if request.user.is_authenticated: favourites = request.user.favourites.all()
    else: favourites = None

    return render(request, "main/offer_details.html", {"offer": offer, "is_my_offer": is_my_offer, "favourites": favourites})

@login_required
def add_offer_car_view(request):
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car_data = form.cleaned_data.copy()
            # ManyToManyField -> lista ID (JSON-safe)
            car_data['features'] = list(
                car_data['features'].values_list('id', flat=True)
            )

            request.session['car_data'] = car_data
            predicted_price = predict_price(car_data)
            request.session['predicted_price'] = predicted_price

            return redirect('add-offer-price')
    else:
        form = CarForm()

    return render(request, 'main/add_offer_car.html', {'form': form})

@login_required
def add_offer_price_view(request):
    car_data = request.session.get('car_data')
    predicted_price = request.session.get('predicted_price')

    if not car_data or predicted_price is None:
        return redirect('add-offer-car')

    if request.method == 'POST':
        form = PriceForm(request.POST, request.FILES)
        if form.is_valid():
            # wyciągamy features z danych auta
            features_ids = car_data.pop('features')

            # zapis auta (bez M2M)
            car = Car.objects.create(**car_data)

            # zapis relacji ManyToMany
            car.features.set(features_ids)

            # zapis oferty
            offer = form.save(commit=False)
            offer.car = car
            offer.seller = request.user
            offer.save()

            # czyszczenie sesji
            request.session.pop('car_data', None)
            request.session.pop('predicted_price', None)

            return redirect('offer-details', slug=offer.slug)
    else:
        form = PriceForm(initial={'price': predicted_price})

    return render(request, 'main/add_offer_price.html', {
        'form': form,
        'car_data': car_data,
        'predicted_price': predicted_price,
    })

@login_required
def my_offers_view(request):
    user = request.user

    active = user.offers.filter(active=True, if_sold=False)
    sold = user.offers.filter(active=False, if_sold=True)
    not_sold = user.offers.filter(active=False, if_sold=False)
    favourites = user.favourites.all()

    context = {
        "active": active,
        "sold": sold,
        "not_sold": not_sold,
        "favourites": favourites,
        "categories": [
            ("Polubione oferty", favourites),
            ("Aktywne oferty", active),
            ("Sprzedane oferty", sold),
            ("Zakończone, niesprzedane oferty", not_sold),
        ],
    }

    return render(request, "main/my_offers.html", context)

@login_required
def end_offer_view(request, slug):
    offer = get_object_or_404(
        Offer,
        slug=slug,
        seller=request.user 
    )

    if request.method == "POST":
        form = EndOfferForm(request.POST, instance=offer)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.active = False
            offer.offer_end_date = timezone.localtime()
            offer.save()
            return redirect("my-offers")
    else:
        form = EndOfferForm(instance=offer)

    return render(request, "main/end_offer.html", {"form": form, "offer": offer})

@login_required
def favourites_view(request, slug):
    user = request.user
    offer = get_object_or_404(Offer, slug=slug)

    if offer in user.favourites.all():
        user.favourites.remove(offer)
    else:
        user.favourites.add(offer)

    return redirect(request.META.get('HTTP_REFERER', 'home'))