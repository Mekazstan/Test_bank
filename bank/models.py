from django.contrib.auth.models import User
from django.db import models
from django.core.mail import send_mail

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    account_number = models.CharField(max_length=20, unique=True)
    daily_transaction_limit = models.DecimalField(max_digits=12, decimal_places=2, default=10000)  # Daily transaction limit
    transaction_count = models.PositiveIntegerField(default=0)  # Count of today's transactions
    max_transaction_count = models.PositiveIntegerField(default=5)  # Admin-set max number of transactions per day

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('transfer', 'Transfer'),
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='completed')

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

class Transfer(models.Model):
    from_account = models.ForeignKey(Account, related_name='transfers_made', on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, related_name='transfers_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    otp = models.CharField(max_length=6, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
