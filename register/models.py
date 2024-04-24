from django.db import models
# Create your models here.

class AccountHolder(models.Model):
    EURO = 'EUR'
    USD = 'USD'
    GBP = 'GBP'

    CURRENCY = [
        (EURO, "Euro"),
        (USD, "US Dollars"),
        (GBP, "British Pounds")
    ]

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    currency = models.CharField(
        max_length=4, choices=CURRENCY, default=EURO)
    balance = models.DecimalField(max_digits=6, decimal_places=2, default=1000)

    def __str__(self):
        return self.email