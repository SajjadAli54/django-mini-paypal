from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import transaction

from rest_framework.decorators import api_view

from payapp.convert import get_exchange_rate
from payapp.models import PaymentRequest, Transaction
from register.models import AccountHolder
from webapps2024.helper import get_converted_amount

from .forms import SignupForm, LoginForm

@api_view(["GET"])
def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        email = request.user.email
        user = AccountHolder.objects.filter(email=email).first()
        payments = list(Transaction.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-timestamp').all())
        payment_requests = list(
            PaymentRequest.objects.filter(
                Q(req_sender=user) | Q(req_recipient=user)
            ).order_by('-updated_at').all()
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
    return user

@api_view(["GET", "POST"])
@transaction.atomic
def user_signup(request):
    page = "pages/signup.html"
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            holder = form.save(commit=False)
            currency = form.cleaned_data['currency']
            converted_amount = get_converted_amount(request, 'EUR', currency, 1000)
            # converted_amount = 1000 * get_exchange_rate('EUR', currency)
            holder.balance = converted_amount
            user = add_user_auth(form)
            holder.password = user.password
            holder.save()
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
                login(request, user)
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, page, {'form': form})

# logout page
def user_logout(request):
    logout(request)
    return redirect('login')