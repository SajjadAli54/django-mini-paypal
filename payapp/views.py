from decimal import Decimal
from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import transaction
from django.core.cache import cache


import requests
from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view

from payapp.forms import *
from register.models import AccountHolder
from .convert import get_exchange_rate

@api_view(['GET'])
def convert_currency(request):
    base_currency = request.GET.get('base_currency')
    target_currency = request.GET.get('target_currency')
    amount = request.GET.get('amount')
                
    exchange_rate = get_exchange_rate(base_currency, target_currency)
    converted_amount = float(amount) * exchange_rate
    response_data = {
        'converted_amount': converted_amount
    }
        
    return JsonResponse(response_data, status=HTTP_200_OK)

@transaction.atomic
def send_money(request: HttpRequest):
    if request.method == 'POST':
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            # email = cache.get('user')
            email = request.user.email
            if not email:
                return render(request, "send_money.html", {'form': form, 'error': 'You are logged out!'})

            sender = AccountHolder.objects.filter(email=email).first()
            recipient = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']

            if email == recipient.email:
                return render(request, "send_money.html", {'form': form, 'error': 'You cannot send money to yourself.'})
            if sender.balance < amount:
                return render(request, "send_money.html", {'form': form, 'error': 'Insufficient funds.'})

            sender.balance -= amount
            base_currency = sender.currency
            target_currency = recipient.currency

            url = f"http://{request.get_host()}/payapp/convert/?"
            params = {'base_currency': base_currency, 
                      'target_currency': target_currency, 
                      'amount': amount}
            response = requests.get(url, params)
            if response.status_code != 200:
                return render(request, "send_money.html", {'form': form, 'error': 'Error converting currency.'})
            converted_amount = response.json()['converted_amount']
            recipient.balance += Decimal(str(converted_amount))

            payment = form.save(commit=False)
            payment.sender = sender
            payment.currency = base_currency
            sender.save()
            recipient.save()
            payment.save()
            return redirect('home')
        else:
            return render(request, "send_money.html", {'form': form})
    else:
        form = SendMoneyForm()
    return render(request, "send_money.html", {'form': form})

@transaction.atomic
def request_payment(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            email = request.user.email
            if not email:
                return render(
                    request, 
                    "request_money.html", 
                    {
                        'form': form, 
                        'error': 'You are logged out!'
                        })

            sender = AccountHolder.objects.filter(email=email).first()
            recipient = form.cleaned_data['req_recipient']

            if email == recipient.email:
                return render(
                    request, 
                    "request_money.html", 
                    {
                        'form': form, 
                        'error': 'You cannot request money from yourself!'
                    })
          
            payment: PaymentRequest = form.save(commit=False)
            payment.req_sender = sender
            payment.save()
            return redirect('home')
        else:
            return render(request, "request_money.html", {'form': form})
    else:
        form = PaymentRequestForm()
    return render(request, "request_money.html", {'form': form})

@transaction.atomic
def reject_request(request: HttpRequest) -> HttpResponse:
    pk = request.GET.get("pk")
    payment_req = PaymentRequest.objects.filter(pk=pk).first()
    payment_req.status = "REJECTED"
    payment_req.is_completed = True
    payment_req.save()
    return redirect('home')

@transaction.atomic
def accept_request(request: HttpRequest)-> HttpResponse:
    pk = request.GET.get("pk")
    payment_req = PaymentRequest.objects.filter(pk=pk).first()
    req_sender = payment_req.req_sender
    req_recipient = payment_req.req_recipient
    amount = payment_req.amount
    base_currency = payment_req.currency
    target_currency = req_sender.currency
    
    url = f"http://{request.get_host()}/payapp/convert/?"
    params = {'base_currency': base_currency, 
        'target_currency': target_currency, 
        'amount': amount}
    response = requests.get(url, params)
    converted_amount = response.json()['converted_amount']
    if converted_amount <= req_recipient.balance:
        req_recipient.balance -= Decimal(str(converted_amount))
        req_sender.balance += amount
        payment = Transaction.objects.create(sender=req_recipient, 
                                             recipient=req_sender, 
                                             amount=converted_amount, 
                                             currency=target_currency)
        req_sender.save()
        req_recipient.save()
        payment.save()
        payment_req.status = "ACCEPTED"
        payment_req.is_completed = True
        payment_req.save()
        return redirect('home')
    return redirect('home', 'Not enough money!')