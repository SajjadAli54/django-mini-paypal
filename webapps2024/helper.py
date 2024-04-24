import requests


def get_converted_amount(request, base_currency, target_currency, amount):
    url = f"http://{request.get_host()}/payapp/convert/?"
    params = {
        'base_currency': base_currency, 
        'target_currency': target_currency, 
        'amount': amount}
    response = requests.get(url, params)
    return response.json()['converted_amount']
