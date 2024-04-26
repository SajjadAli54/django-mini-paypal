from decimal import Decimal
from django.shortcuts import redirect, render
from django.contrib import messages

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import transaction

from rest_framework.status import HTTP_200_OK
from rest_framework.decorators import api_view

from payapp.forms import *
from register.models import AccountHolder
from webapps2024.helper import get_converted_amount
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
@api_view(['GET', 'POST'])
def send_money(request: HttpRequest):
    if not request.user.is_authenticated:
        messages.error(request, "Kindly Log in first to send money!")
        return redirect('home')
    if request.method == 'POST':
        form = SendMoneyForm(request.POST)
        if form.is_valid():
            email = request.user.email
            if not email:
                messages.error(request, 'You are logged out!')
                return ('login')

            sender = AccountHolder.objects.filter(email=email).first()
            recipient = form.cleaned_data['recipient']
            amount = form.cleaned_data['amount']

            if email == recipient.email:
                messages.error(request, "You cannot send money to yourself!")
                return redirect('send_money')
            if sender.balance < amount:
                messages.error(request, "Insufficient Balance")
                return redirect("send_money")

            sender.balance -= amount
            base_currency = sender.currency
            target_currency = recipient.currency

            converted_amount = get_converted_amount(request, base_currency, target_currency, amount)
            recipient.balance += Decimal(str(converted_amount))

            payment = form.save(commit=False)
            payment.sender = sender
            payment.currency = base_currency
            sender.save()
            recipient.save()
            payment.save()
            return redirect('home')        
    else:
        form = SendMoneyForm()
    return render(request, "pages/send_money.html", {'form': form})

@transaction.atomic
@api_view(['GET', 'POST'])
def request_payment(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        messages.error(request, "Kindly Log in first to Request Money!")
        return redirect('home')

    if request.method == 'POST':
        form = PaymentRequestForm(request.POST)
        if form.is_valid():
            email = request.user.email
            sender = AccountHolder.objects.filter(email=email).first()
            recipient = form.cleaned_data['req_recipient']

            if email == recipient.email:
                messages.error(request, "You cannot request yourself to pay you the money!")
                return redirect("request_money")
          
            payment: PaymentRequest = form.save(commit=False)
            payment.req_sender = sender
            payment.save()
            return redirect('home')
    else:
        form = PaymentRequestForm()
    return render(request, "pages/request_money.html", {'form': form})

@api_view(['GET'])
@transaction.atomic
def renew_request(request: HttpRequest) -> HttpResponse:
    pk = request.GET.get("pk")
    payment_req = PaymentRequest.objects.filter(pk=pk).first()
    if not payment_req or payment_req.status == "ACCEPTED":
        messages.error(request, "Payment Request is already processed or Could not be found!")
        return redirect('home')
    payment_req.status = "PENDING"
    payment_req.is_completed = False
    payment_req.save()
    return redirect('home')

@api_view(['GET'])
@transaction.atomic
def reject_request(request: HttpRequest) -> HttpResponse:
    pk = request.GET.get("pk")
    payment_req = PaymentRequest.objects.filter(pk=pk).first()
    if not payment_req or payment_req.status == "ACCEPTED":
        messages.error(request, "Payment Request is already processed or Could not be found!")
        return redirect('home')
    payment_req.status = "REJECTED"
    payment_req.is_completed = True
    payment_req.save()
    return redirect('home')

@api_view(['GET'])
@transaction.atomic
def accept_request(request: HttpRequest)-> HttpResponse:
    pk = request.GET.get("pk")
    payment_req = PaymentRequest.objects.filter(pk=pk).first()
    req_sender = payment_req.req_sender
    req_recipient = payment_req.req_recipient
    amount = payment_req.amount
    base_currency = payment_req.currency
    target_currency = req_sender.currency
    
    converted_amount = get_converted_amount(request, base_currency, target_currency, amount)
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