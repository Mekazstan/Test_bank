from django.contrib import admin
from .models import Account, Transaction, Transfer, Notification

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'balance', 'daily_transaction_limit', 'max_transaction_count')
    list_editable = ('daily_transaction_limit', 'max_transaction_count')

admin.site.register(Account, AccountAdmin)
admin.site.register(Transaction)
admin.site.register(Transfer)
admin.site.register(Notification)
