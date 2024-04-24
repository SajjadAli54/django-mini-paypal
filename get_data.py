from register.models import AccountHolder
from django.core.cache import cache

url = "http://127.0.0.1:8000/payapp/convert/?"


def logout():
    cache.delete('user')

def set_email(email: str):
    cache.set('user', email)

def get_email() -> str:
    email = cache.get('user')
    if email:
        return email
    else:
        return None

def get_url() -> str:
    global url
    return url

def set_url(new_url: str):
    global url
    url = new_url
    return url