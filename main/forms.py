from django import forms
from django.forms import Form, ModelForm
from main.models import Car, Offer
from django.utils import timezone

# klasy które automatycznie dodają wygląd inputów bootstrapa do formularzy
class BootstrapForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  
        for field in self.fields.values():  
            field.widget.attrs.setdefault('class', 'form-control')

class BootstrapModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

# formularz wyboru daty rezerwacji 
class CarForm(BootstrapModelForm, ModelForm):
    class Meta:
        model = Car
        fields = ["vehicle_brand", 
                  "vehicle_model", 
                  "vehicle_version", 
                  "vehicle_generation", 
                  "production_year", 
                  "mileage_km", 
                  "power_hp", 
                  "displacement_cm3", 
                  "fuel_type", 
                  "co2_emissions", 
                  "drive", 
                  "transmission", 
                  "type", 
                  "doors_number", 
                  "colour", 
                  "condition", 
                  "features"
                  ]
        
        labels = {
            "date_start": "Data rozpoczęcia rezerwacji",
            "date_end": "Data zakończenia rezerwacji",
            "time_start": "Godzina rozpoczęcia rezerwacji w każdym dniu",
            "time_end": "Godzina zakończenia rezerwacji w każdym dniu",
        }
        widgets = {
            "date_start": forms.DateInput(attrs={'type': 'date'}),
            "date_end": forms.DateInput(attrs={'type': 'date'}),
            "time_start": forms.TimeInput(attrs={'type': 'time'}),
            "time_end": forms.TimeInput(attrs={'type': 'time'}),
        }

    # walidacja formularza
    def clean(self):
        cleaned_data = super().clean()

        date_start = cleaned_data.get("date_start")
        date_end = cleaned_data.get("date_end")
        time_start = cleaned_data.get("time_start")
        time_end = cleaned_data.get("time_end")

        # przerywamy walidację jeśli brakuje jakiejś wartości żeby uniknąć błędów w walidacji spowodowanych porównywaniem pustych wartości
        if not all([date_start, date_end, time_start, time_end]):
            return cleaned_data

        today = timezone.localdate()
        time_now = timezone.localtime().time()

        # początek w przeszłości
        if date_start < today:
            self.add_error('date_start', "Nie można zarezerwować terminu w przeszłości.")

        # koniec w przeszłości
        if date_end < today:
            self.add_error('date_end', "Nie można zarezerwować terminu w przeszłości.")

        # ten sam dzień, godzina w przeszłości
        if date_start == today and time_end < time_now:
            self.add_error('time_end', "Nie można zarezerwować terminu w przeszłości.")

        # odwrotny zakres dat
        if date_start > date_end:
            self.add_error('date_end', "Data zakończenia musi być późniejsza niż data rozpoczęcia.")

        # odwrotny zakres godzin/zakres godzin przechodzi przez północ
        if time_end <= time_start:
            self.add_error('time_end', "Godzina zakończenia musi być późniejsza niż godzina początku. Jeśli chcesz dokonać rezerwacji, która przechodzi przez 00:00, musisz podzielić ją na dwie rezerwacje.")

        return cleaned_data

# formularz wyboryu miejsca rezerwacji
class ReservationChooseSpaceForm(BootstrapModelForm, ModelForm):
    class Meta:
        model = Reservation
        fields = ["date_start", "date_end", "time_start", "time_end", "parking_space", "number_plate"]
        labels = {
            "parking_space": "Miejsce parkingowe",
            "number_plate": "Numer rejestracyjny samochodu",
        }
        widgets = {
            "date_start": forms.HiddenInput(),
            "date_end": forms.HiddenInput(),
            "time_start": forms.HiddenInput(),
            "time_end": forms.HiddenInput(),
        }

    # dodatkowy argument pozwalający na przekazanie listy dotępnych miejsc do wyboru w formularzu    
    def __init__(self, *args, available_spaces=None, **kwargs):
        super().__init__(*args, **kwargs)
        if available_spaces is not None:
            self.fields['parking_space'].queryset = available_spaces





