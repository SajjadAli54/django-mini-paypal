from django import forms

from payapp.models import Transaction

from get_data import get_email
from register.models import AccountHolder


class SendMoneyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'].queryset = AccountHolder.objects.exclude(email=get_email())
    
    class Meta:
        model = Transaction
        fields = ['recipient', 'amount']
