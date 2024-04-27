from django import forms
from django.db.models import Q

from payapp.models import PaymentRequest, Transaction

from register.models import AccountHolder

class SendMoneyForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=0.1)
    
    def __init__(self, *args, **kwargs):
        email = kwargs.pop("email", None)
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = AccountHolder.objects.exclude(email=email)
    
    class Meta:
        model = Transaction
        fields = ['recipient', 'amount']

class PaymentRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        email = kwargs.pop("email", None)
        super().__init__(*args, **kwargs)
        self.fields['req_recipient'].queryset = AccountHolder.objects.exclude(email=email)
    
    class Meta:
        model = PaymentRequest
        fields = ['req_recipient', 'amount']
