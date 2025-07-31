# 🏦 Django Banking System API

A multi-tenant, secure banking application built with Django and Django REST Framework (DRF), supporting:
- OTP-based authentication
- Account creation for the users
- Role-based access control (RBAC)
- Multi-currency fund transfers
- Admin dashboard
- Swagger API documentation

---

## 📦 Features

- ✅ User registration with OTP verification
- ✅ Login with token-based authentication
- ✅ Fund transfers with currency conversion
- ✅ Role & permission management (admin/user)
- ✅ Multi-tenancy support with organizations
- ✅ Admin transaction reports
- ✅ Timezone-aware data
- ✅ Redis caching for balances
- ✅ Swagger and ReDoc documentation

---

## 🛠️ Project Setup Instructions

python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

## Access Application
🔐 Admin Panel: http://localhost:8000/admin/

📘 Swagger UI: http://localhost:8000/swagger/

📘 ReDoc: http://localhost:8000/redoc/

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/banking_system.git
cd banking_system

📘 API Endpoints
Method	URL	Description
POST	/register/	Register user
POST	/send-otp/	Send OTP to email
POST	/verify-otp/	Verify OTP
POST	/login/	Login with OTP
GET/POST	/accounts/	List/Create Bank Account
GET	/transactions/	View Transactions
POST	/transactions/	Initiate Transaction
GET/POST	/roles/	Manage roles (Admin only)
POST	/assign-role/	Assign role to user (Admin)
GET	/admin-dashboard/	Dashboard stats (Admin)