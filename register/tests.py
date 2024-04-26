from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from payapp.convert import get_exchange_rate
from register.models import AccountHolder
from payapp.models import PaymentRequest, Transaction
from .forms import SignupForm, LoginForm

"""
All Test Passed
"""
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.index_url = reverse('home')
        self.user = User.objects.create_user(
            username='testuser', password='testpassword', email='test@example.com')
        self.account_holder = AccountHolder.objects.create(
            username='testuser', currency='USD', balance=1000 * get_exchange_rate("EUR", "USD"))

    def test_index_view_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/index.html')

    def test_index_view_unauthenticated_user(self):
        response = self.client.get(self.index_url)
        self.assertRedirects(response, self.login_url)

    def test_signup_view(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/signup.html')

        data = {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'currency': 'EUR'
        }
        response = self.client.post(self.signup_url, data)
        self.assertRedirects(response, self.login_url)

        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(AccountHolder.objects.filter(username='newuser').exists())

    def test_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login.html')

        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(response, self.index_url)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
