from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction
from django.core.cache import cache

import requests

from payapp.models import PaymentRequest, Transaction
from register.models import AccountHolder

from .forms import SignupForm, LoginForm

def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        email = request.user.email
        user = AccountHolder.objects.filter(email=email).first()
        payments = list(Transaction.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp').all())
        payment_requests = list(
            PaymentRequest.objects.filter(
                Q(req_sender=user) | Q(req_recipient=user)
            ).order_by('-timestamp').all()
        )
        return render(request, "pages/index.html", 
                      {'user': user, 
                       'payments': payments,
                       'payment_requests': payment_requests
                    })
                       
    return redirect('login')

def add_user_auth(form: SignupForm):
    username = form.cleaned_data['username']
    password = form.cleaned_data['password']
    email = form.cleaned_data['email']
    first_name = form.cleaned_data['first_name']
    last_name = form.cleaned_data['last_name']

    user = User.objects.create_user(
        username=username, 
        password=password, 
        email=email, 
        first_name=first_name, 
        last_name=last_name)
    user.save()

@transaction.atomic
def user_signup(request):
    page = "pages/signup.html"
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            holder = form.save(commit=False)
            currency = form.cleaned_data['currency']
            url = f"http://{request.get_host()}/payapp/convert/?"
            params = {'base_currency': 'EUR', 'target_currency': currency, 'amount': 1000}
            response = requests.get(url, params)
            if response.status_code == 200:
                converted_amount = response.json()['converted_amount']
                holder.balance = converted_amount
                holder.save()
                add_user_auth(form)
                return redirect('login')
    else:
        form = SignupForm()
    return render(request, page, {'form': form})
        
# login page
def user_login(request):
    page =  "pages/login.html"
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:             
                cache.set('user', user.email)
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, page, {'form': form})

# logout page
def user_logout(request):
    logout(request)
    cache.delete('user')
    return redirect('login')