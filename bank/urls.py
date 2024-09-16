from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # User-related endpoints
    path('', views.dashboard, name='dashboard'),  # Dashboard view
    path('transfer/', views.transfer, name='transfer'),  # Transfer funds view
    path('generate-otp/', views.generate_otp, name='generate_otp'),  # Generate OTP for transfer
    path('notifications/', views.notifications, name='notifications'),  # User notifications view
    path('transaction-history/', views.transaction_history, name='transaction_history'),  # Transaction history view
    path('profile/', views.profile, name='profile'),  # User profile and settings view
    path('contact-admin/', views.contact_admin, name='contact_admin'),  # Contact admin view
    path('account_summary/', views.account_summary, name='account_summary'),
    
    # Authentication (if not handled automatically via Django)
    path('register/', views.register, name='register'),  # Register view
    path('login/', views.CustomLoginView.as_view(), name='login'),  # Login view
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),  # Logout view
]
