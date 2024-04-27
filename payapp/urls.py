from django.urls import path
import payapp.views as views

urlpatterns = [
    path('convert/', views.convert_currency, name='convert_currency'),
    path('send/', views.send_money, name='send_money'),
    path('request/', views.request_payment, name='request'),
    path('renew/', views.renew_request, name='renew'),
    path('reject/', views.reject_request, name='reject'),
    path('accept/', views.accept_request, name='accept'),
]
