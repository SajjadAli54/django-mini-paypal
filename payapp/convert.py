"""
Exchange Rate between Currencies
USD, EUR, and GBP
"""

def get_exchange_rate(base_currency, target_currency):
    if base_currency == target_currency:
        return 1.0
    if base_currency == 'USD':
        if target_currency == 'EUR':
            return 0.85
        if target_currency == 'GBP':
            return 0.75
    if base_currency == 'EUR':
        if target_currency == 'USD':
            return 1.18
        if target_currency == 'GBP':
            return 0.89
    if base_currency == 'GBP':
        if target_currency == 'USD':
            return 1.33
        if target_currency == 'EUR':
            return 1.12