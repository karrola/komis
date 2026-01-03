from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MaxValueValidator, MinValueValidator 
from datetime import date

class Feature(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Car(models.Model):
    FUEL_CHOICES = [
        ('Gasoline', 'Benzyna'),
        ('Diesel', 'Diesel'),
        ('Gasoline + LPG', 'Benzyna + LPG'),
        ('Hybrid', 'Hybryda'),
        ('Electric', 'Elektryczny'),
        ('Gasoline + CNG', 'Benzyna + CNG'),
    ]

    DRIVE_CHOICES = [
        ('Front wheels', 'Napęd przedni'),
        ('4x4 (permanent)', '4x4 stały'),
        ('4x4 (attached automatically)', '4x4 automatyczny'),
        ('Rear wheels', 'Napęd tylny'),
        ('4x4 (attached manually)', '4x4 manualny'),
    ]

    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatyczna'),
        ('Manual', 'Manualna'),
    ]

    TYPE_CHOICES = [
        ('SUV', 'SUV'),
        ('compact', 'Kompakt'),
        ('minivan', 'Minivan'),
        ('city_cars', 'Samochód miejski'),
        ('station_wagon', 'Kombi'),
        ('sedan', 'Sedan'),
        ('small_cars', 'Małe samochody'),
        ('coupe', 'Coupe'),
        ('convertible', 'Kabriolet'),
    ]

    COLOUR_CHOICES = [
        ('gray', 'Szary'),
        ('black', 'Czarny'),
        ('white', 'Biały'),
        ('red', 'Czerwony'),
        ('silver', 'Srebrny'),
        ('blue', 'Niebieski'),
        ('green', 'Zielony'),
        ('beige', 'Beżowy'),
        ('burgundy', 'Bordowy'),
        ('other', 'Inny'),
        ('brown', 'Brązowy'),
        ('golden', 'Złoty'),
        ('yellow', 'Żółty'),
        ('violet', 'Fioletowy'),
    ]

    CONDITION_CHOICES = [
        ('New', 'Nowy'),
        ('Used', 'Używany'),
    ]

    vehicle_brand = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_version = models.CharField(max_length=150, null=True, blank=True)
    vehicle_generation = models.CharField(max_length=150, null=True, blank=True)
    production_year = models.IntegerField(validators=[MinValueValidator(1920), MaxValueValidator(date.today().year)])
    mileage_km = models.IntegerField(validators=[MinValueValidator(1)])
    power_hp = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(30), MaxValueValidator(2000)])
    displacement_cm3 = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(100), MaxValueValidator(1000)])
    fuel_type = models.CharField(max_length=50, choices=FUEL_CHOICES)
    co2_emissions = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(500)])
    drive = models.CharField(max_length=50, null=True, blank=True, choices=DRIVE_CHOICES)
    transmission = models.CharField(max_length=50, choices=TRANSMISSION_CHOICES)
    type = models.CharField(max_length=50, null=True, blank=True, choices=TYPE_CHOICES)
    doors_number = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(6)])
    colour = models.CharField(max_length=50, null=True, blank=True, choices=COLOUR_CHOICES)
    sold_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=100, choices=CONDITION_CHOICES)
    features = models.ManyToManyField(Feature, blank=True, related_name='cars')

    def __str__(self):
        brand = self.vehicle_brand
        model = self.vehicle_model
        year = self.production_year
        return f"{brand} {model} ({year})".strip()


class Offer(models.Model):
    PROVINCE_CHOICES = [
        ("DS", "Dolnośląskie"),
        ("KP", "Kujawsko-pomorskie"),
        ("LU", "Lubelskie"),
        ("LB", "Lubuskie"),
        ("LD", "Łódzkie"),
        ("MA", "Małopolskie"),
        ("MZ", "Mazowieckie"),
        ("OP", "Opolskie"),
        ("PK", "Podkarpackie"),
        ("PD", "Podlaskie"),
        ("PM", "Pomorskie"),
        ("SL", "Śląskie"),
        ("SK", "Świętokrzyskie"),
        ("WM", "Warmińsko-mazurskie"),
        ("WP", "Wielkopolskie"),
        ("ZP", "Zachodniopomorskie"),
    ]
        
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='offers')
    image = models.ImageField(upload_to='car_offers/', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    active = models.BooleanField(default=True)     # czy oferta jest aktywna
    if_sold = models.BooleanField(default=False)   # czy przedmiot sprzedany
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='offers')
    offer_end_date = models.DateTimeField(null=True, blank=True)
    offer_publication_date = models.DateTimeField(default=timezone.now)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=2, choices=PROVINCE_CHOICES)
    description = models.TextField(max_length=1000, blank=True, null=True)

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
