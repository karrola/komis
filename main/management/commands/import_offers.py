import csv
import time
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from main.models import Car, Offer, Feature


BATCH_OFFERS = 100  # ile Offer zapisać jednocześnie (bulk_create)


def safe_int(val):
    if val is None or val == '':
        return None
    try:
        return int(float(val))
    except Exception:
        return None

def safe_float(val):
    if val is None or val == '':
        return None
    try:
        return float(val)
    except Exception:
        return None

def safe_decimal(val):
    if val is None or val == '':
        return None
    try:
        return Decimal(str(val))
    except (InvalidOperation, ValueError):
        return None

def parse_date_try_formats(s):
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s)
        return dt
    except Exception:
        pass
    fmts = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
    ]
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            return dt
        except Exception:
            continue
    return None

def parse_features_text(s):
    """Prosta funkcja rozdzielająca pole Features; zwraca listę nazw cech."""
    if not s:
        return []
    return s[1:-1].replace("'", '').split(', ')


class Command(BaseCommand):
    help = "Import offers CSV into Car and Offer models (supports Features -> Feature M2M)."

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='Path to csv file')
        parser.add_argument('--delimiter', type=str, default=',', help='CSV delimiter (default ,)')
        parser.add_argument('--encoding', type=str, default='utf-8-sig', help='File encoding (default utf-8-sig)')
        parser.add_argument('--progress-interval', type=int, default=5000,
                            help='How many rows between progress prints (default 5000)')

    def handle(self, *args, **options):
        path = options['csvfile']
        delim = options['delimiter']
        enc = options['encoding']
        progress_interval = options['progress_interval']

        offers_to_create = []
        total_offers = 0
        total_cars = 0

        # cache istniejących/utworzonych Feature (name -> Feature instance)
        feature_cache = {f.name: f for f in Feature.objects.all()}

        start_time = time.time()

        try:
            with open(path, encoding=enc, newline='') as f:
                reader = csv.DictReader(f, delimiter=delim)
                for i, row in enumerate(reader, start=1):
                    # helper: get value and strip
                    def g(k):
                        return row.get(k, '').strip() if row.get(k) is not None else ''

                    # --- przygotuj Car ---
                    car = Car.objects.create(
                        vehicle_brand = g('Vehicle_brand') or None,
                        vehicle_model = g('Vehicle_model') or None,
                        vehicle_version = g('Vehicle_version') or None,
                        vehicle_generation = g('Vehicle_generation') or None,
                        production_year = safe_int(g('Production_year') or None),
                        mileage_km = safe_float(g('Mileage_km') or None),
                        power_hp = safe_float(g('Power_HP') or None),
                        displacement_cm3 = safe_float(g('Displacement_cm3') or None),
                        fuel_type = g('Fuel_type') or None,
                        co2_emissions = safe_float(g('CO2_emissions') or None),
                        drive = g('Drive') or None,
                        transmission = g('Transmission') or None,
                        type = g('Type') or None,
                        doors_number = safe_int(g('Doors_number') or None),
                        colour = g('Colour') or None,
                        origin_country = g('Origin_country') or None,
                        first_owner = g('First_owner') or None,
                        first_registration_date = (parse_date_try_formats(g('First_registration_date')) and parse_date_try_formats(g('First_registration_date')).date()) or None,
                        sold_price = safe_decimal(g('Price')),
                        condition = g('Condition') or None,
                    )
                    total_cars += 1

                    # --- obsługa Features: sparsuj i przypisz ManyToMany ---
                    features_raw = g('Features') or None
                    if features_raw:
                        feature_names = parse_features_text(features_raw)
                        # dla każdej nazwy weź Feature z cache lub utwórz i dodaj do cache
                        to_add = []
                        for name in feature_names:
                            if not name:
                                continue
                            feat = feature_cache.get(name)
                            if feat is None:
                                feat, created = Feature.objects.get_or_create(name=name)
                                feature_cache[name] = feat
                            to_add.append(feat)
                        if to_add:
                            # add wymaga zapisania car — mamy zapisane; dodaj ID-ami
                            car.features.add(*to_add)

                    # --- przygotuj Offer (do bulk_create) ---
                    price = safe_decimal(g('Price') or None)
                    offer_pub = parse_date_try_formats(g('Offer_publication_date') or None)
                    offer_end = parse_date_try_formats(g('Offer_end_date') or None)  # jeśli kolumna istnieje
                    offer_location = g('Offer_location') or None

                    offer = Offer(
                        car = car,
                        price = price,
                        active = False,
                        if_sold = True,
                        seller = None,  # brak informacji w CSV -> zostawiamy NULL
                        buyer = None,
                        offer_end_date = offer_end,
                        offer_publication_date = offer_pub,
                        offer_location = offer_location,
                    )
                    offers_to_create.append(offer)

                    # batch save offers
                    if len(offers_to_create) >= BATCH_OFFERS:
                        with transaction.atomic():
                            Offer.objects.bulk_create(offers_to_create, batch_size=BATCH_OFFERS)
                        total_offers += len(offers_to_create)
                        offers_to_create = []

                    # progress
                    if (i % progress_interval) == 0:
                        elapsed = time.time() - start_time
                        rate = i / elapsed if elapsed > 0 else 0
                        msg = (f"Processed rows: {i} | cars created: {total_cars} | offers queued: {len(offers_to_create)} | "
                               f"offers saved: {total_offers} | elapsed {elapsed:.1f}s | {rate:.1f} rows/s")
                        self.stdout.write(msg)

                # ostatnia partia offers
                if offers_to_create:
                    with transaction.atomic():
                        Offer.objects.bulk_create(offers_to_create, batch_size=BATCH_OFFERS)
                    total_offers += len(offers_to_create)

            total_elapsed = time.time() - start_time
            final_msg = (f"Import finished. Rows processed: {i}. Cars created: {total_cars}. Offers created: {total_offers}. "
                         f"Time: {total_elapsed:.1f}s, avg { (i/total_elapsed) if total_elapsed>0 else 0:.1f} rows/s")
            self.stdout.write(self.style.SUCCESS(final_msg))

        except FileNotFoundError:
            raise CommandError(f'File not found: {path}')
        except Exception as e:
            raise CommandError(f'Error during import: {e}')
