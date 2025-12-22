import csv
import time
import random
import uuid
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from main.models import Car, Offer, Feature
from django.utils.text import slugify

BATCH_OFFERS = 10000
ACTIVE_OFFERS_COUNT = 1000

def safe_int(val):
    if val is None or val == '':
        return None
    return int(float(val))

def safe_float(val):
    if val is None or val == '':
        return None
    return float(val)

def safe_decimal(val):
    if val is None or val == '':
        return None
    return Decimal(str(val))

def parse_date_try_formats(s):
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        pass
    fmts = ["%Y-%m-%d %H:%M:%S","%Y-%m-%d","%d.%m.%Y","%d/%m/%Y","%Y/%m/%d","%d-%m-%Y"]
    for f in fmts:
        try:
            return datetime.strptime(s, f)
        except Exception:
            continue
    return None

def parse_features_text(s):
    if not s:
        return []
    return s[1:-1].replace("'", "").split(", ")

class Command(BaseCommand):
    help = "Import offers CSV into Car and Offer models (with Features, M2M, 1000 active offers)."

    def add_arguments(self, parser):
        parser.add_argument("csvfile", type=str)
        parser.add_argument("--delimiter", type=str, default=",")
        parser.add_argument("--encoding", type=str, default="utf-8-sig")
        parser.add_argument("--progress-interval", type=int, default=5000)

    def handle(self, *args, **options):
        path = options["csvfile"]
        delim = options["delimiter"]
        enc = options["encoding"]
        progress_interval = options["progress_interval"]

        cars_to_create = []
        offers_temp = []
        feature_per_car = []

        feature_cache = {f.name: f for f in Feature.objects.all()}

        start_time = time.time()

        # miasta do losowania aktywnych ofert
        CITIES = [("Warszawa","Mazowieckie"),("Katowice","Śląskie"),
                  ("Kraków","Małopolskie"),("Gliwice","Śląskie")]

        try:
            with open(path, encoding=enc, newline="") as f:
                reader = csv.DictReader(f, delimiter=delim)
                for i, row in enumerate(reader, start=1):
                    def g(k): return row.get(k, "").strip() if row.get(k) else ""

                    # walidacja wymaganych pól
                    required_fields = [g("Vehicle_brand"), g("Vehicle_model"), g("Production_year"),
                                       g("Mileage_km"), g("Fuel_type"), g("Transmission"), g("Condition")]
                    if any(not f for f in required_fields):
                        continue

                    # Car
                    car = Car(
                        vehicle_brand=g("Vehicle_brand"),
                        vehicle_model=g("Vehicle_model"),
                        vehicle_version=g("Vehicle_version") or None,
                        vehicle_generation=g("Vehicle_generation") or None,
                        production_year=safe_int(g("Production_year")),
                        mileage_km=safe_float(g("Mileage_km")),
                        power_hp=safe_float(g("Power_HP") or None),
                        displacement_cm3=safe_float(g("Displacement_cm3") or None),
                        fuel_type=g("Fuel_type"),
                        co2_emissions=safe_float(g("CO2_emissions") or None),
                        drive=g("Drive") or None,
                        transmission=g("Transmission"),
                        type=g("Type") or None,
                        doors_number=safe_int(g("Doors_number") or None),
                        colour=g("Colour") or None,
                        origin_country=g("Origin_country") or None,
                        first_owner=g("First_owner") or None,
                        first_registration_date=(
                            parse_date_try_formats(g("First_registration_date")).date()
                            if parse_date_try_formats(g("First_registration_date")) else None
                        ),
                        condition=g("Condition"),
                    )
                    cars_to_create.append(car)

                    # Features
                    to_add = []
                    features_raw = g("Features")
                    if features_raw:
                        for name in parse_features_text(features_raw):
                            if not name: continue
                            feat = feature_cache.get(name)
                            if feat is None:
                                feat, _ = Feature.objects.get_or_create(name=name)
                                feature_cache[name] = feat
                            to_add.append(feat)
                    feature_per_car.append(to_add)

                    # Offer tymczasowo, bez ustawienia active/if_sold jeszcze
                    price = safe_decimal(g("Price"))
                    offer_pub = parse_date_try_formats(g("Offer_publication_date"))
                    offer_end = parse_date_try_formats(g("Offer_end_date"))

                    offer = Offer(
                        car=car,
                        price=price,
                        offer_end_date=offer_end,
                        offer_publication_date=timezone.make_aware(offer_pub) if offer_pub else timezone.now(),
                        city="",  # przypiszemy później
                        province="",
                        description=None,
                        slug=f"{slugify(car)}-{uuid.uuid4().hex[:8]}"
                    )
                    offers_temp.append(offer)

                    if i % progress_interval == 0:
                        elapsed = time.time() - start_time
                        self.stdout.write(f"Processed {i} rows | Cars: {len(cars_to_create)} | Offers temp: {len(offers_temp)}")

            # --- losowe 1000 aktywnych ofert ---
            total_offers_count = len(offers_temp)
            active_indices = random.sample(range(total_offers_count), min(ACTIVE_OFFERS_COUNT, total_offers_count))
            city_cycle = []
            for city in CITIES:
                city_cycle.extend([city]*(ACTIVE_OFFERS_COUNT//4))
            random.shuffle(city_cycle)
            city_iter = iter(city_cycle)

            for idx, offer in enumerate(offers_temp):
                is_active = idx in active_indices
                if is_active:
                    offer.active = True
                    offer.if_sold = False
                    offer.sold_price = None
                    offer.description = (
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                        "Morbi sagittis lectus purus, id dictum turpis eleifend sit amet. "
                        "Aenean vitae vehicula tortor. Phasellus et nulla convallis, tempus sem eu, mattis purus. "
                        "Nunc mattis ante sed nisi iaculis mollis. Maecenas at elit ut lacus sagittis congue "
                        "bibendum vitae ex. Phasellus finibus, ipsum vitae fermentum condimentum, dolor enim "
                        "rhoncus dui, sed ultrices justo diam ac odio."
                    )
                    offer.city, offer.province = next(city_iter)
                    offer.car.sold_price = None
                else:
                    offer.active = False
                    offer.if_sold = True
                    offer.car.sold_price = offer.price
                    offer.city, offer.province = random.choice(CITIES)

            # --- batch save ---
            BATCH_SIZE = BATCH_OFFERS
            for start in range(0, len(cars_to_create), BATCH_SIZE):
                end = start + BATCH_SIZE
                batch_cars = cars_to_create[start:end]
                batch_offers = offers_temp[start:end]

                with transaction.atomic():
                    Car.objects.bulk_create(batch_cars, batch_size=BATCH_SIZE)
                    Offer.objects.bulk_create(batch_offers, batch_size=BATCH_SIZE)

                    # M2M Features
                    for car_obj, feats in zip(batch_cars, feature_per_car[start:end]):
                        links = [Car.features.through(car_id=car_obj.pk, feature_id=f.pk) for f in feats]
                        Car.features.through.objects.bulk_create(links, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(f"Import finished | Cars: {len(cars_to_create)} | Offers: {len(offers_temp)}"))

        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")
        except Exception as e:
            raise CommandError(f"Error during import: {e}")