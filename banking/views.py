from rest_framework import generics, permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from django.db import transaction as db_transaction
from django.db.models import F, Sum
from rest_framework.authtoken.models import Token
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
import requests
from rest_framework.authtoken.models import Token
from django.conf import settings
from decimal import Decimal
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from .permissions import IsInGroup
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

User = get_user_model()

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['admin']


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['admin']


class AssignRoleViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['admin']

    def create(self, request):
        serializer = UserRoleSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            role = serializer.validated_data['role']
            user.groups.clear()
            user.groups.add(role)
            return Response({'status': 'role assigned'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]

class UserRoleAssignmentView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = UserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        group = serializer.validated_data['group']
        user.groups.add(group)
        return Response({"message": f"Role '{group.name}' assigned to user '{user.username}'"}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        serializer = UserRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        group = serializer.validated_data['group']
        user.groups.remove(group)
        return Response({"message": f"Role '{group.name}' removed from user '{user.username}'"}, status=status.HTTP_200_OK)

class UserRoleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        roles = user.groups.values_list('name', flat=True)
        permissions = Permission.objects.filter(group__user=user).values_list('codename', flat=True).distinct()
        return Response({
            "username": user.username,
            "roles": list(roles),
            "permissions": list(permissions)
        })

class RegisterView(APIView):
    def post(self, request):
        request.data['username'] = request.data.get('email')
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response({"error": "User with this email already exists"}, status=400)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = get_random_string(length=6, allowed_chars='0123456789')
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_mail('Your OTP', f'Your OTP is {otp}', settings.EMAIL_HOST_USER, [user.email])
            return Response({'message': 'OTP sent to email'}, status=201)
        return Response(serializer.errors, status=400)


class SendOTPView(APIView):
    def post(self, request):
        user = User.objects.filter(email=request.data.get('email')).first()
        if not user:
            return Response({"error": "User with this email does not exist"}, status=400)
        otp = get_random_string(length=6, allowed_chars='0123456789')
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_mail('Your OTP', f'Your OTP is {otp}', settings.EMAIL_HOST_USER, [user.email])
        return Response({'message': 'OTP sent to email'}, status=200)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        if str(user.otp) != str(otp):
            return Response({'error': 'Invalid OTP'}, status=400)

        if timezone.now() - user.otp_created_at > timezone.timedelta(minutes=10):
            return Response({'error': 'OTP expired'}, status=400)

        user.otp = None
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'OTP verified successfully', 'token': token.key}, status=200)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)


class BankAccountListCreateView(generics.ListCreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['user', 'admin']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['user', 'admin']


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['admin']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = User.objects.count()
        context['total_accounts'] = Account.objects.count()
        context['total_transactions'] = Transaction.objects.count()
        context['currency_summary'] = Transaction.objects.values('to_account__currency').annotate(
            total_amount=Sum('amount')
        )
        return context

class TransactionListCreateView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all().order_by('-timestamp')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsInGroup]
    required_groups = ['user', 'admin']

    def perform_create(self, serializer):
        data = self.request.data
        with db_transaction.atomic():
            from_acc = BankAccount.objects.select_for_update().get(account_number=data.get('from_account'))
            to_acc = BankAccount.objects.select_for_update().get(account_number=data.get('to_account'))
            amount = float(data.get('amount'))

            if from_acc.currency != to_acc.currency:
                rate = get_conversion_rate(from_acc.currency, to_acc.currency)
                amount_converted = Decimal(amount) * Decimal(rate * 0.99)
                if from_acc.balance < amount:
                    raise serializers.ValidationError('Insufficient funds')
                from_acc.balance = F('balance') - amount
                to_acc.balance = F('balance') + amount_converted
            else:
                if from_acc.balance < amount:
                    raise serializers.ValidationError('Insufficient funds')
                from_acc.balance = F('balance') - amount
                to_acc.balance = F('balance') + amount

            from_acc.save()
            to_acc.save()
            serializer.save()


def get_conversion_rate(from_currency, to_currency):
    res = requests.get(f"https://api.exchangerate.host/latest?base={from_currency}")
    rate = Decimal(res.json()['rates'][to_currency])
    spread = Decimal("0.01")
    return rate * (1 - spread)
