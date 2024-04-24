from django import forms
from django.contrib.auth.models import User

from register.models import AccountHolder

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = AccountHolder
        fields = ['currency', 'email', 'username', 'first_name', 'last_name', 'password']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)