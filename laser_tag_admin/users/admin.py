from django.contrib import admin
from .models import TelegramUser

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'last_name', 'phone_number', 'games_played', 'subscribed_to_chat')
    search_fields = ('telegram_id', 'first_name', 'last_name', 'phone_number')
    list_filter = ('subscribed_to_chat',)
    ordering = ('telegram_id',)
