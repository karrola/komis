from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

class Feature(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    vehicle_brand = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_version = models.CharField(max_length=150, null=True, blank=True)
    vehicle_generation = models.CharField(max_length=150, null=True, blank=True)
    production_year = models.IntegerField()
    mileage_km = models.FloatField()
    power_hp = models.FloatField(null=True, blank=True)
    displacement_cm3 = models.FloatField(null=True, blank=True)
    fuel_type = models.CharField(max_length=50)
    co2_emissions = models.FloatField(null=True, blank=True)
    drive = models.CharField(max_length=50, null=True, blank=True)
    transmission = models.CharField(max_length=50)
    type = models.CharField(max_length=50, null=True, blank=True)
    doors_number = models.IntegerField(null=True, blank=True)
    colour = models.CharField(max_length=50, null=True, blank=True)
    origin_country = models.CharField(max_length=100, null=True, blank=True)
    first_owner = models.CharField(max_length=100, null=True, blank=True)
    first_registration_date = models.DateField(null=True, blank=True)
    sold_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=100)
    features = models.ManyToManyField(Feature, blank=True, related_name='cars')

    def __str__(self):
        brand = self.vehicle_brand
        model = self.vehicle_model
        year = self.production_year
        return f"{brand} {model} ({year})".strip()


class Offer(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='offers')
    image = models.ImageField(upload_to='car_offers/', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)     # czy oferta jest aktywna
    if_sold = models.BooleanField(default=False)   # czy przedmiot sprzedany
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='offers_sold')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                              on_delete=models.SET_NULL, related_name='offers_bought')
    offer_end_date = models.DateTimeField(null=True, blank=True)
    offer_publication_date = models.DateTimeField(default=timezone.now)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    slug = models.SlugField(max_length=250, unique=True, blank=True)


    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)

        if creating and not self.slug:
            # slug = car + pk (unikalny)
            base_slug = slugify(self.car)
            self.slug = f"{base_slug}-{self.pk}"
            super().save(update_fields=["slug"])

    def __str__(self):
        return f"Offer {self.pk} — {self.price if self.price else 'n/a'}"
