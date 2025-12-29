import django_filters
from django import forms
from .models import Offer, Feature, Car


class OfferFilter(django_filters.FilterSet):
    # pola Car z choices
    fuel = django_filters.MultipleChoiceFilter(
        field_name="car__fuel_type",
        choices=Car.FUEL_CHOICES,
        label="Rodzaj paliwa",
        widget=forms.CheckboxSelectMultiple,
    )
    drive = django_filters.MultipleChoiceFilter(
        field_name="car__drive",
        choices=Car.DRIVE_CHOICES,
        label="Napęd",
        widget=forms.CheckboxSelectMultiple,
    )
    transmission = django_filters.MultipleChoiceFilter(
        field_name="car__transmission",
        choices=Car.TRANSMISSION_CHOICES,
        label="Skrzynia biegów",
        widget=forms.CheckboxSelectMultiple,
    )
    type = django_filters.MultipleChoiceFilter(
        field_name="car__type",
        choices=Car.TYPE_CHOICES,
        label="Typ nadwozia",
        widget=forms.CheckboxSelectMultiple,
    )
    colour = django_filters.MultipleChoiceFilter(
        field_name="car__colour",
        choices=Car.COLOUR_CHOICES,
        label="Kolor",
        widget=forms.CheckboxSelectMultiple,
    )
    condition = django_filters.MultipleChoiceFilter(
        field_name="car__condition",
        choices=Car.CONDITION_CHOICES,
        label="Stan",
        widget=forms.CheckboxSelectMultiple,
    )
    province = django_filters.MultipleChoiceFilter(
        field_name="province",
        choices=Offer.PROVINCE_CHOICES,
        label="Województwo",
        widget=forms.CheckboxSelectMultiple,
    )

    # pola bez choices — dynamiczne wartości z bazy
    brand = django_filters.MultipleChoiceFilter(
        field_name="car__vehicle_brand",
        label="Marka",
        widget=forms.CheckboxSelectMultiple,
    )
    city = django_filters.MultipleChoiceFilter(
        field_name="city",
        label="Miasto",
        widget=forms.CheckboxSelectMultiple,
    )


    # M2M
    features = django_filters.ModelMultipleChoiceFilter(
        queryset=Feature.objects.all(),
        label="Wyposażenie",
        conjoined=True,
        widget=forms.CheckboxSelectMultiple,
    )

    # zakresy liczbowe
    production_year__gte = django_filters.NumberFilter(
        field_name="car__production_year", lookup_expr="gte", label="Rok produkcji od"
    )
    production_year__lte = django_filters.NumberFilter(
        field_name="car__production_year", lookup_expr="lte", label="Rok produkcji do"
    )
    mileage_km__gte = django_filters.NumberFilter(
        field_name="car__mileage_km", lookup_expr="gte", label="Przebieg od"
    )
    mileage_km__lte = django_filters.NumberFilter(
        field_name="car__mileage_km", lookup_expr="lte", label="Przebieg do"
    )
    price__gte = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="Cena od"
    )
    price__lte = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="Cena do"
    )

    class Meta:
        model = Offer
        fields = ["price"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # dla pól bez choices ustaw dynamiczne wartości z bazy
        self.set_choices_raw("brand", "car__vehicle_brand")
        self.set_choices_raw("city", "city")

    def set_choices_raw(self, filter_name, field_path):
        values = Offer.objects.values_list(field_path, flat=True).distinct().order_by(field_path)
        self.filters[filter_name].extra["choices"] = [(v, v) for v in values if v]