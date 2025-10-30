import django_filters
from .models import Offer, Feature
from django import forms

class OfferFilter(django_filters.FilterSet):
    # marka
    brand = django_filters.MultipleChoiceFilter(
        method='filter_by_brand', 
        label='Marka',
        widget=forms.CheckboxSelectMultiple)
    
    # cechy
    features = django_filters.ModelMultipleChoiceFilter(
        queryset=Feature.objects.all(),
        method='filter_by_features',
        label='Cechy',
        conjoined=True,
        widget=forms.CheckboxSelectMultiple)
    
    # rok produkcji
    production_year__gte = django_filters.NumberFilter(
        field_name='car__production_year',
        lookup_expr='gte',
        label='Rok produkcji od'
    )
    production_year__lte = django_filters.NumberFilter(
        field_name='car__production_year',
        lookup_expr='lte',
        label='Rok produkcji do'
    )

    # przebieg
    mileage_km__gte = django_filters.NumberFilter(
        field_name='car__mileage_km',
        lookup_expr='gte',
        label='Przebieg od'
    )
    mileage_km__lte = django_filters.NumberFilter(
        field_name='car__mileage_km',
        lookup_expr='lte',
        label='Przebieg do'
    )

    # cena
    price__gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Cena od'
    )
    price__lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Cena do'
    )
    
    # paliwo 
    fuel = django_filters.MultipleChoiceFilter(
    method='filter_by_fuel', 
    label='Rodzaj paliwa',
    widget=forms.CheckboxSelectMultiple)

    drive = django_filters.MultipleChoiceFilter(method='filter_by_drive', label='Napęd', widget=forms.CheckboxSelectMultiple)
    transmission = django_filters.MultipleChoiceFilter(method='filter_by_transmission', label='Skrzynia biegów', widget=forms.CheckboxSelectMultiple)
    type = django_filters.MultipleChoiceFilter(method='filter_by_type', label='Typ nadwozia', widget=forms.CheckboxSelectMultiple)
    colour = django_filters.MultipleChoiceFilter(method='filter_by_colour', label='Kolor', widget=forms.CheckboxSelectMultiple)
    condition = django_filters.MultipleChoiceFilter(method='filter_by_condition', label='Stan', widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Offer
        fields = ['price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        brands = Offer.objects.values_list('car__vehicle_brand', flat=True).distinct().order_by('car__vehicle_brand')
        choices = [(b, b) for b in brands if b]
        choices_with_empty = [("", "Wszystkie")] + choices
        self.filters['brand'].extra['choices'] = choices_with_empty

        fuels = Offer.objects.values_list('car__fuel_type', flat=True).distinct().order_by('car__fuel_type')
        fuel_choices = [(f, f) for f in fuels if f]
        self.filters['fuel'].extra['choices'] = [("", "Wszystkie")] + fuel_choices

            # --- Napęd ---
        drives = Offer.objects.values_list('car__drive', flat=True).distinct().order_by('car__drive')
        drive_choices = [(d, d) for d in drives if d]
        drive_choices_with_empty = [("", "Wszystkie")] + drive_choices
        self.filters['drive'].extra['choices'] = drive_choices_with_empty

        # --- Skrzynia biegów ---
        transmissions = Offer.objects.values_list('car__transmission', flat=True).distinct().order_by('car__transmission')
        transmission_choices = [(t, t) for t in transmissions if t]
        transmission_choices_with_empty = [("", "Wszystkie")] + transmission_choices
        self.filters['transmission'].extra['choices'] = transmission_choices_with_empty

        # --- Typ nadwozia ---
        types = Offer.objects.values_list('car__type', flat=True).distinct().order_by('car__type')
        type_choices = [(ty, ty) for ty in types if ty]
        type_choices_with_empty = [("", "Wszystkie")] + type_choices
        self.filters['type'].extra['choices'] = type_choices_with_empty

        # --- Kolor ---
        colours = Offer.objects.values_list('car__colour', flat=True).distinct().order_by('car__colour')
        colour_choices = [(c, c) for c in colours if c]
        colour_choices_with_empty = [("", "Wszystkie")] + colour_choices
        self.filters['colour'].extra['choices'] = colour_choices_with_empty

        # --- Stan ---
        conditions = Offer.objects.values_list('car__condition', flat=True).distinct().order_by('car__condition')
        condition_choices = [(co, co) for co in conditions if co]
        condition_choices_with_empty = [("", "Wszystkie")] + condition_choices
        self.filters['condition'].extra['choices'] = condition_choices_with_empty


    def filter_by_brand(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__vehicle_brand__in=value)
    
    def filter_by_fuel(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__fuel_type__in=value)
    
    def filter_by_drive(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__drive__in=value)

    def filter_by_transmission(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__transmission__in=value)

    def filter_by_type(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__type__in=value)

    def filter_by_colour(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__colour__in=value)

    def filter_by_condition(self, queryset, name, value):
        if not value or value == [""]:
            return queryset
        return queryset.filter(car__condition__in=value)
    
    def filter_by_features(self, queryset, name, values):
        if not values:
            return queryset
        
        for feature in values:
            queryset = queryset.filter(car__features=feature)
        return queryset.distinct()