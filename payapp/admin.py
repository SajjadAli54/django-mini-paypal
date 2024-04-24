from django.contrib import admin

from payapp.models import Transaction, PaymentRequest

admin.site.register(Transaction)
admin.site.register(PaymentRequest)
