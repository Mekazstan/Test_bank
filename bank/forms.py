from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class ContactAdminForm(forms.Form):
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)


class TransferForm(forms.Form):
    to_account = forms.CharField(max_length=20, label='Recipient Account Number')
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label='Amount', min_value=0.01)
    pin = forms.CharField(max_length=6, required=False, label='PIN')  # Optional, if you are using PINs for security

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount

    def clean_to_account(self):
        to_account = self.cleaned_data.get('to_account')
        if not to_account.isdigit():  # Simple validation to check if it's a numeric account number
            raise forms.ValidationError('Invalid account number.')
        return to_account

class TransactionFilterForm(forms.Form):
    date_from = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    transaction_type = forms.ChoiceField(choices=[('', 'All'), ('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer')], required=False)
    min_amount = forms.DecimalField(required=False, decimal_places=2, max_digits=10)
    max_amount = forms.DecimalField(required=False, decimal_places=2, max_digits=10)