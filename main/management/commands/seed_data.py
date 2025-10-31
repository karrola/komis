import os
import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Offer, Car  # dopasuj do swoich modeli

class Command(BaseCommand):
    help = "Tworzy superusera i importuje dane z CSV"

    def handle(self, *args, **kwargs):
        # 1️⃣ Tworzymy superusera, jeśli nie istnieje
        User = get_user_model()
        admin_pw = os.getenv("DJANGO_ADMIN_PASSWORD", "admin123")  # fallback
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@admin.pl", admin_pw)
            self.stdout.write(self.style.SUCCESS("Superuser stworzony"))
        else:
            self.stdout.write("Superuser już istnieje")

        # 2️⃣ Import CSV, tylko jeśli nie ma żadnych ofert
        if Offer.objects.exists():
            self.stdout.write("Dane już są zaimportowane, nic nie robimy")
            return

        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../prepared_car_sales.csv")
        csv_path = os.path.abspath(csv_path)

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"Plik CSV nie istnieje: {csv_path}"))
            return

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # dopasuj pola do swoich modeli
                car, created = Car.objects.get_or_create(
                    vin=row["vin"],
                    defaults={"make": row["make"], "model": row["model"], "year": row["year"]},
                )
                Offer.objects.create(
                    car=car,
                    price=row["price"],
                    description=row.get("description", ""),
                )

        self.stdout.write(self.style.SUCCESS("CSV zaimportowane pomyślnie"))