from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'start_time', 'location', 'players_count')
    list_filter = ('date',)
    search_fields = ('location',)
    ordering = ('-date',)
