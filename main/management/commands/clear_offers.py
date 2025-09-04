from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from main.models import Offer, Car, Feature

class Command(BaseCommand):
    help = "Usuń WSZYSTKIE rekordy Offer, Car i Feature z bazy. Opcja --yes potwierdza operację."

    def add_arguments(self, parser):
        parser.add_argument('--yes', action='store_true', help='Potwierdź usunięcie bez pytania')
        parser.add_argument('--dry-run', action='store_true', help='Pokaż ile rekordów zostałoby usuniętych, nie usuwaj')

    def handle(self, *args, **options):
        confirm = options['yes']
        dry_run = options['dry_run']

        offers_count = Offer.objects.count()
        cars_count = Car.objects.count()
        features_count = Feature.objects.count()

        self.stdout.write(f"Offers: {offers_count}, Cars: {cars_count}, Features: {features_count}")

        if dry_run:
            self.stdout.write(self.style.NOTICE("Dry-run: nic nie zostało usunięte."))
            return

        if not confirm:
            self.stdout.write("Aby potwierdzić usunięcie wpisz dokładnie: YES (wielkie litery) i naciśnij Enter.")
            ans = input("Potwierdź (YES/NO): ").strip()
            if ans != "YES":
                raise CommandError("Anulowano — nic nie zostało usunięte.")

        # wykonaj kasowanie w transakcji
        try:
            with transaction.atomic():
                # usuń oferty, potem samochody, potem cechy (kolejność nie jest krytyczna jeśli kaskady ustawione)
                Offer.objects.all().delete()
                Car.objects.all().delete()
                Feature.objects.all().delete()
        except Exception as e:
            raise CommandError(f"Błąd podczas usuwania: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Usunięto: Offers {offers_count}, Cars {cars_count}, Features {features_count}"
        ))