from asgiref.sync import sync_to_async
from django.utils import timezone
import pytz
import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laser_tag_admin.settings')
django.setup()
from laser_tag_admin.users.models import User
from laser_tag_admin.games.models import Game


@sync_to_async
def get_or_create_user(user_id, first_name, last_name, username):
    # Проверяем, существует ли пользователь с данным ID, если нет, создаем нового
    return User.objects.get_or_create(
        telegram_id=user_id,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'language': 'en',
            'registration_date': timezone.now(),  # Записываем текущую дату и время
            'notifications_enabled': True  # Уведомления включены по умолчанию
        }
    )

@sync_to_async
def update_user_language(user_id, language):
    User.objects.filter(telegram_id=user_id).update(language=language)

@sync_to_async
def update_user_phone_number(user_id, phone_number):
    User.objects.filter(telegram_id=user_id).update(phone_number=phone_number)

@sync_to_async
def get_upcoming_games():
    warsaw_timezone = pytz.timezone('Europe/Warsaw')
    current_datetime = timezone.now().astimezone(warsaw_timezone)
    upcoming_games = Game.objects.filter(
        date__gt=current_datetime.date()
    ) | Game.objects.filter(
        date=current_datetime.date(),
        start_time__gt=current_datetime.time()
    )
    return list(upcoming_games)
