from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    REQUIRED_FIELDS = ['email']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=100, default='UTC')
    failed_otp_attempts = models.IntegerField(default=0)
    otp_sent_at = models.DateTimeField(null=True, blank=True)


# tenants/models.py
class Tenant(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, unique=True)

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('user', 'tenant')

class Organization(models.Model):
    name = models.CharField(max_length=255)
    timezone = models.CharField(max_length=64)

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=12, unique=True, editable=False)
    currency = models.CharField(max_length=3, choices=[('USD','US Dollar'),('EUR','Euro'),('GBP','British Pound')])
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = get_random_string(length=12, allowed_chars='0123456789')
        super().save(*args, **kwargs)

class Transaction(models.Model):
    from_account = models.ForeignKey(BankAccount, related_name='outgoing', on_delete=models.SET_NULL, null=True)
    to_account = models.ForeignKey(BankAccount, related_name='incoming', on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    type = models.CharField(max_length=16, choices=[('deposit','Deposit'),('withdraw','Withdraw'),('transfer','Transfer')])
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)