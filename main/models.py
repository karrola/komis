from django.db import models
from django.conf import settings

class Feature(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    vehicle_brand = models.CharField(max_length=100, null=True, blank=True)
    vehicle_model = models.CharField(max_length=100, null=True, blank=True)
    vehicle_version = models.CharField(max_length=150, null=True, blank=True)
    vehicle_generation = models.CharField(max_length=150, null=True, blank=True)
    production_year = models.IntegerField(null=True, blank=True)
    mileage_km = models.FloatField(null=True, blank=True)
    power_hp = models.FloatField(null=True, blank=True)
    displacement_cm3 = models.FloatField(null=True, blank=True)
    fuel_type = models.CharField(max_length=50, null=True, blank=True)
    co2_emissions = models.FloatField(null=True, blank=True)
    drive = models.CharField(max_length=50, null=True, blank=True)
    transmission = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=50, null=True, blank=True)
    doors_number = models.IntegerField(null=True, blank=True)
    colour = models.CharField(max_length=50, null=True, blank=True)
    origin_country = models.CharField(max_length=100, null=True, blank=True)
    first_owner = models.CharField(max_length=100, null=True, blank=True)
    first_registration_date = models.DateField(null=True, blank=True)
    sold_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=100, null=True, blank=True)
    features = models.ManyToManyField(Feature, blank=True, related_name='cars')

    def __str__(self):
        brand = self.vehicle_brand or ''
        model = self.vehicle_model or ''
        year = self.production_year or ''
        return f"{brand} {model} ({year})".strip()


class Offer(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    active = models.BooleanField(default=True)     # czy oferta jest aktywna
    if_sold = models.BooleanField(default=False)   # czy przedmiot sprzedany
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='offers_sold')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='offers_bought')
    offer_end_date = models.DateTimeField(null=True, blank=True)
    offer_publication_date = models.DateTimeField(null=True, blank=True)
    offer_location = models.CharField(max_length=200, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Offer {self.pk} — {self.price if self.price else 'n/a'}"
