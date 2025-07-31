from django.core.cache import cache

def get_cached_account_balance(account_id):
    key = f"account_balance_{account_id}"
    balance = cache.get(key)
    if balance is None:
        from banking.models import Account
        balance = Account.objects.get(id=account_id).balance
        cache.set(key, balance, timeout=60)
    return balance


def set_cached_account_balance(account_id, balance):
    key = f"account_balance_{account_id}"
    cache.set(key, balance, timeout=60)
