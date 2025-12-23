import django_filters
from .models import Offer, Feature
from django import forms

class OfferFilter(django_filters.FilterSet):
    # checkboxy
    brand = django_filters.MultipleChoiceFilter(method='filter_by_brand', label='Marka', widget=forms.CheckboxSelectMultiple)
    fuel = django_filters.MultipleChoiceFilter(method='filter_by_fuel', label='Rodzaj paliwa', widget=forms.CheckboxSelectMultiple)
    drive = django_filters.MultipleChoiceFilter(method='filter_by_drive', label='Napęd', widget=forms.CheckboxSelectMultiple)
    transmission = django_filters.MultipleChoiceFilter(method='filter_by_transmission', label='Skrzynia biegów', widget=forms.CheckboxSelectMultiple)
    type = django_filters.MultipleChoiceFilter(method='filter_by_type', label='Typ nadwozia', widget=forms.CheckboxSelectMultiple)
    colour = django_filters.MultipleChoiceFilter(method='filter_by_colour', label='Kolor', widget=forms.CheckboxSelectMultiple)
    condition = django_filters.MultipleChoiceFilter(method='filter_by_condition', label='Stan', widget=forms.CheckboxSelectMultiple)
    city = django_filters.MultipleChoiceFilter(method='filter_by_city', label='Miasto', widget=forms.CheckboxSelectMultiple)
    province = django_filters.MultipleChoiceFilter(method='filter_by_province', label='Województwo', widget=forms.CheckboxSelectMultiple)

    # checkboxy z m2m
    features = django_filters.ModelMultipleChoiceFilter(queryset=Feature.objects.all(), method='filter_by_features', label='Wyposażenie', conjoined=True, widget=forms.CheckboxSelectMultiple)
    
    # zakresy
    production_year__gte = django_filters.NumberFilter(field_name='car__production_year', lookup_expr='gte', label='Rok produkcji od')
    production_year__lte = django_filters.NumberFilter(field_name='car__production_year', lookup_expr='lte', label='Rok produkcji do')
    mileage_km__gte = django_filters.NumberFilter(field_name='car__mileage_km', lookup_expr='gte', label='Przebieg od')
    mileage_km__lte = django_filters.NumberFilter(field_name='car__mileage_km', lookup_expr='lte', label='Przebieg do')
    price__gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Cena od')
    price__lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Cena do')
    
    class Meta:
        model = Offer
        fields = ['price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # wybory dostępne w filtrach
        self.set_choices("brand", "car__vehicle_brand")
        self.set_choices("fuel", "car__fuel_type")
        self.set_choices("drive", "car__drive")
        self.set_choices("transmission", "car__transmission")
        self.set_choices("type", "car__type")
        self.set_choices("colour", "car__colour")
        self.set_choices("condition", "car__condition")
        self.set_choices("city", "city")
        self.set_choices("province", "province")

    # metody
    def set_choices(self, filter_name, field_path):
        # ustawia choices na podstawie danych w bazie
        values = (
            Offer.objects
            .values_list(field_path, flat=True)
            .distinct()
            .order_by(field_path)
        )
        self.filters[filter_name].extra["choices"] = [
            (v, v) for v in values if v
        ]

    def filter_multi(self, queryset, field, values):
        # wspólna logika dla checkboxów MultipleChoice
        if not values:
            return queryset
        return queryset.filter(**{f"{field}__in": values})
    
    # checkboxy
    def filter_by_brand(self, qs, name, value):
        return self.filter_multi(qs, "car__vehicle_brand", value)

    def filter_by_fuel(self, qs, name, value):
        return self.filter_multi(qs, "car__fuel_type", value)

    def filter_by_drive(self, qs, name, value):
        return self.filter_multi(qs, "car__drive", value)

    def filter_by_transmission(self, qs, name, value):
        return self.filter_multi(qs, "car__transmission", value)

    def filter_by_type(self, qs, name, value):
        return self.filter_multi(qs, "car__type", value)

    def filter_by_colour(self, qs, name, value):
        return self.filter_multi(qs, "car__colour", value)

    def filter_by_condition(self, qs, name, value):
        return self.filter_multi(qs, "car__condition", value)

    def filter_by_city(self, qs, name, value):
        return self.filter_multi(qs, "city", value)

    def filter_by_province(self, qs, name, value):
        return self.filter_multi(qs, "province", value)
    
    # checkbozy z m2m
    def filter_by_features(self, queryset, name, values):
        if not values:
            return queryset
        
        for feature in values:
            queryset = queryset.filter(car__features=feature)
        return queryset.distinct()