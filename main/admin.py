from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Feature, Car, Offer

#Futures admin
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# Car admin
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle_brand", "vehicle_model", "production_year", "mileage_km", "power_hp", "colour")
    search_fields = ("vehicle_brand", "vehicle_model", "vehicle_version", "vehicle_generation")
    list_filter = ("vehicle_brand", "fuel_type", "transmission", "production_year")
    filter_horizontal = ("features",)         # ładne UI dla ManyToMany
    readonly_fields = ()                      # dodaj pola tylko do odczytu jeśli chcesz
    raw_id_fields = ()                        # użyj ('features',) niepotrzebne; M2M obsługiwane przez filter_horizontal

# Offer admin
class OfferAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "price", "active", "if_sold", "seller", "buyer", "offer_publication_date", "offer_end_date")
    search_fields = ("car__vehicle_model", "car__vehicle_brand", "seller__email", "buyer__email", "offer_location")
    list_filter = ("active", "if_sold", "offer_location")
    date_hierarchy = "offer_publication_date"
    raw_id_fields = ("car", "seller", "buyer")   # szybkie ładowanie przy dużych tabelach

# Rejestracja adminów
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Offer, OfferAdmin)