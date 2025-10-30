from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Offer
from django.core.paginator import Paginator
from .filters import OfferFilter

# Create your views here.

def home_view(request):
    offers = Offer.objects.filter(active = True, if_sold = False).select_related('car', 'seller')

    offer_filter = OfferFilter(request.GET, queryset=offers)
    filtered_count = offer_filter.qs.count()

    paginator = Paginator(offer_filter.qs, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'filter': offer_filter,
        'filtered_count': filtered_count,
        'page_obj': page_obj,
    }

    return render(request, "main/home.html", context)

