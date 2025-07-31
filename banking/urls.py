from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

assign_role = AssignRoleViewSet.as_view({'post': 'create'})

urlpatterns = [
    path('', include(router.urls)),
    path('assign-role/', assign_role, name='assign-role'),
    path('register/', RegisterView.as_view(), name='register'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('admin_report', AdminDashboardView.as_view(), name='admin-report'),
    path('accounts/', BankAccountListCreateView.as_view(), name='account-list-create'),
    path('accounts/<int:pk>/', BankAccountDetailView.as_view(), name='account-detail'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
]