from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'last_name', 'username', 'phone_number', 'language', 'notifications_enabled', 'registration_date')
    search_fields = ('telegram_id', 'first_name', 'last_name', 'username', 'phone_number')
    list_filter = ('language', 'notifications_enabled')
    ordering = ('telegram_id',)
