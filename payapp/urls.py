from django.urls import path
import payapp.views as views

urlpatterns = [
    path('convert/', views.convert_currency, name='convert_currency'),
    path('send/', views.send_money, name='send_money'),
    path('request/', views.request_payment, name='request'),
]
