from django.db import models

from register.models import AccountHolder


# Create your models here.

EURO = 'EUR'
USD = 'USD'
GBP = 'GBP'

CURRENCY = [
        (EURO, "Euro"),
        (USD, "US Dollars"),
        (GBP, "British Pounds")
]
class Transaction(models.Model):

    sender = models.ForeignKey(AccountHolder, related_name='sent_transactions', on_delete=models.PROTECT)
    recipient = models.ForeignKey(AccountHolder, related_name='received_transactions', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=EURO)
    timestamp = models.DateTimeField(auto_now_add=True)

PENDING = "PENDING"
REJECTED = "REJECTED"
ACCEPTED = "ACCEPTED"

REQUEST_STATUS = [
    (PENDING, "Pending"),
    (REJECTED, "Rejected"),
    (ACCEPTED, "Accepted")
]

class PaymentRequest(models.Model):
    req_sender = models.ForeignKey(AccountHolder, related_name="+" ,on_delete=models.PROTECT)
    req_recipient = models.ForeignKey(AccountHolder, related_name="+", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY, default=EURO)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default=PENDING)