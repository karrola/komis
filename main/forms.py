from django import forms
from django.forms import Form, ModelForm
from main.models import Car, Offer
from django.utils import timezone

# klasy które automatycznie dodają wygląd inputów bootstrapa do formularzy
class BootstrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')

# formularz informacji o samochodzie
class CarForm(BootstrapModelForm, ModelForm):
    class Meta:
        model = Car
        exclude = ['sold_price']
        
        labels = {
                "vehicle_brand": "Marka", 
                "vehicle_model": "Model", 
                "vehicle_version": "Wersja", 
                "vehicle_generation": "Generacja", 
                "production_year": "Rok produkcji", 
                "mileage_km": "Przebieg", 
                "power_hp": "Moc", 
                "displacement_cm3": "Pojemność", 
                "fuel_type": "Rodzaj paliwa", 
                "co2_emissions": "Emisja CO₂", 
                "drive": "Napęd", 
                "transmission": "Skrzynia biegów", 
                "type": "Typ nadwozia", 
                "doors_number": "Liczba drzwi", 
                "colour": "Kolors", 
                "condition": "Stan", 
                "features": "Wyposażenie",
        }
        widgets = {
            "production_year": forms.NumberInput(attrs={"min": "1920"}),
            "mileage_km": forms.NumberInput(attrs={"min": "1"}),
            "power_hp": forms.NumberInput(attrs={"min": "30", "max": "2000"}),
            "displacement_cm3": forms.NumberInput(attrs={"min": "100", "max": "1000"}),
            "co2_emissions": forms.NumberInput(attrs={"min": "1", "max": "500"}),
            "doors_number": forms.NumberInput(attrs={"min": "1", "max": "6"}),
            "features": forms.CheckboxSelectMultiple(),
        }

# formularz szczegółów oferty
class PriceForm(BootstrapModelForm, ModelForm):
    class Meta:
        model = Offer
        fields = ["price", "image", "city", "province", "description"]
        labels = {
            "price": "Cena",
            "image": "Zdjęcie",
            "city": "Miasto",
            "province": "Województwo",
            "description": "Opis oferty"
        }
        widgets = {
            "price": forms.NumberInput(attrs={"placeholder": "Przepisz proponowaną cenę lub wprowadź własną..."})
        }


# formularz zakończenia oferty
class EndOfferForm(BootstrapModelForm, ModelForm):
    SOLD_CHOICES = [
        (True, 'Sprzedana'),
        (False, 'Nie sprzedana'),
    ]

    if_sold = forms.ChoiceField(
        choices=SOLD_CHOICES,
        label='Status oferty',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Offer
        fields = ["if_sold"]


