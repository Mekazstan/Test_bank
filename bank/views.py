import random
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView
from .forms import ContactAdminForm, RegisterForm, TransferForm
from .models import Account, Transaction, Transfer, Notification
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registration
            messages.success(request, 'Registration successful.')
            return redirect('dashboard')  # Redirect to a page after successful registration
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return reverse('dashboard')  # Redirect to the dashboard after successful login

@login_required
def dashboard(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(account=account)
    return render(request, 'bank/dashboard.html', {'account': account, 'transactions': transactions})

@login_required
def profile(request):
    # Return the profile details of the logged-in user
    user = request.user
    profile_data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        # Add any other user-related data you need, such as:
        # 'phone_number': user.profile.phone_number (if you have a related profile model)
    }

    # Render the profile details in the template
    return render(request, 'profile.html', {
        'profile_data': profile_data
    })

@login_required
def deposit(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        account = get_object_or_404(Account, user=request.user)
        account.balance += amount
        account.save()

        Transaction.objects.create(account=account, transaction_type='deposit', amount=amount)
        return redirect('dashboard')
    return render(request, 'bank/deposit.html')

@login_required
def withdraw(request):
    if request.method == 'POST':
        try:
            amount = float(request.POST.get('amount'))
        except (ValueError, TypeError):
            return HttpResponseBadRequest('Invalid amount')

        account = get_object_or_404(Account, user=request.user)
        if account.balance >= amount:
            account.balance -= amount
            account.save()

            Transaction.objects.create(account=account, transaction_type='withdrawal', amount=amount)
            return redirect('dashboard')
        else:
            return render(request, 'bank/withdraw.html', {'error': 'Insufficient funds'})
    return render(request, 'bank/withdraw.html')

@login_required
def transfer(request):
    from_account = Account.objects.get(user=request.user)
    if request.method == 'POST':
        to_account_number = request.POST.get('to_account')
        amount = float(request.POST.get('amount'))
        pin = request.POST.get('pin')

        # Validate account number
        try:
            to_account = Account.objects.get(account_number=to_account_number)
        except Account.DoesNotExist:
            return render(request, 'bank/transfer.html', {'error': 'Account does not exist'})

        # Ensure daily transaction limit
        if from_account.transaction_count >= from_account.max_transaction_count:
            return render(request, 'bank/transfer.html', {'error': 'Transaction limit exceeded. Please contact admin.'})

        # Pin Validation
        transfer_record = Transfer.objects.filter(from_account=from_account, pin=pin).first()
        if not transfer_record:
            return render(request, 'bank/transfer.html', {'error': 'Invalid Pin'})

        # Validate sufficient funds
        if from_account.balance < amount:
            return render(request, 'bank/transfer.html', {'error': 'Insufficient funds'})

        # Perform the transfer
        from_account.balance -= amount
        from_account.transaction_count += 1
        from_account.save()

        to_account.balance += amount
        to_account.save()

        # Record transactions
        Transaction.objects.create(account=from_account, transaction_type='transfer', amount=amount)
        Transaction.objects.create(account=to_account, transaction_type='deposit', amount=amount)

        # Send Notifications
        Notification.objects.create(user=to_account.user, message=f"You received ${amount} from {from_account.user.username}")
        send_mail(
            'Transaction Alert',
            f"You received ${amount} from {from_account.user.username}",
            'noreply@bankapp.com',
            [to_account.user.email],
            fail_silently=False,
        )

        return redirect('dashboard')
    
    return render(request, 'bank/transfer.html')


@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user, is_read=False)
    for notification in user_notifications:
        notification.is_read = True
        notification.save()
    return render(request, 'bank/notifications.html', {'notifications': user_notifications})


@login_required
def generate_otp(request):
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            to_account_number = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']

            # Check if account exists
            to_account = get_object_or_404(Account, account_number=to_account_number)

            # Generate a random OTP
            otp = str(random.randint(100000, 999999))
            
            # Save the transfer record with the OTP
            Transfer.objects.create(from_account=request.user.account, to_account=to_account, amount=amount, otp=otp)

            # Send OTP via email
            send_mail(
                'Your OTP for Transfer',
                f"Your OTP for transferring ${amount} is {otp}",
                'noreply@bankapp.com',
                [request.user.email],
                fail_silently=False,
            )

            return render(request, 'bank/transfer.html', {'success': 'OTP sent to your email'})
    else:
        form = TransferForm()

    return render(request, 'bank/generate_otp.html', {'form': form})

@login_required
def transaction_history(request):
    # Fetch transactions for the current user
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')  # Most recent first

    # Render the transactions in a template
    return render(request, 'transaction_history.html', {
        'transactions': transactions
    })


@login_required
def contact_admin(request):
    if request.method == 'POST':
        form = ContactAdminForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            email_from = request.user.email
            admin_email = 'admin@example.com'

            send_mail(subject, message, email_from, [admin_email])

            messages.success(request, 'Your message has been sent to the admin.')
            return redirect('contact_admin_confirmation')  # Redirect to a confirmation page
    else:
        form = ContactAdminForm()

    return render(request, 'contact_admin.html', {'form': form})

@login_required
def account_summary(request):
    account = get_object_or_404(Account, user=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-date')
    return render(request, 'bank/account_summary.html', {'account': account, 'transactions': transactions})