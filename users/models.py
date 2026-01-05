from django.db import models

from django.contrib.auth.models import AbstractUser
from main.models import Offer

# Create your models here.

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    favourites = models.ManyToManyField(Offer, blank=True, related_name='interested_users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    def __str__(self):
        return self.email