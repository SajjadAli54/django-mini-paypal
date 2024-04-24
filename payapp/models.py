from django.db import models

from register.models import AccountHolder


# Create your models here.

class Transaction(models.Model):
    EURO = 'EUR'
    USD = 'USD'
    GBP = 'GBP'

    CURRENCY = [
        (EURO, "Euro"),
        (USD, "US Dollars"),
        (GBP, "British Pounds")
    ]

    sender = models.ForeignKey(AccountHolder, related_name='sent_transactions', on_delete=models.PROTECT)
    recipient = models.ForeignKey(AccountHolder, related_name='received_transactions', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=EURO)
    timestamp = models.DateTimeField(auto_now_add=True)