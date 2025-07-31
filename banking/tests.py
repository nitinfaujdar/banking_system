from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from banking.models import Tenant, Organization, BankAccount

User = get_user_model()


class AccountTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create required data
        self.tenant = Tenant.objects.create(name="TestTenant", domain="test.local")

        self.organization = Organization.objects.create(
            name="TestOrg",
            timezone="UTC"
        )

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )

        self.bank_account = BankAccount.objects.create(
            user=self.user,
            organization=self.organization,
            currency='USD',
            balance=1000.00
        )

        # Obtain access token (update this if you use custom token endpoint)
        login_response = self.client.post(reverse('login'), {
            "username": "testuser",   # change to 'email' if login expects email
            "password": "testpass"
        })

        self.assertEqual(login_response.status_code, 200)
        token = login_response.data.get("access") or login_response.data.get("token")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_account_balance_fetch(self):
        url = reverse('account-detail', args=[self.bank_account.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(float(response.data.get('balance')), 1000.00)

    def test_user_login_success(self):
        # Redo login for testing
        client = APIClient()
        response = client.post(reverse('login'), {
            "username": "testuser",
            "password": "testpass"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)  # or "token" depending on your setup
