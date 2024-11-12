from django.contrib import admin
from .models import Game, GameRegistration

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'start_time', 'location', 'get_total_players_count')
    list_filter = ('date',)
    search_fields = ('location',)
    ordering = ('-date',)


@admin.register(GameRegistration)
class GameRegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'guests_count')
    list_filter = ('game', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'game__location')
    ordering = ('-game',)
