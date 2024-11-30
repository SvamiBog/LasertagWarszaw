from asgiref.sync import sync_to_async
from django.utils import timezone
import os
import django
from django.db import transaction
from datetime import datetime


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laser_tag_admin.settings')
django.setup()
from laser_tag_admin.users.models import User
from laser_tag_admin.games.models import Game
from laser_tag_admin.games.models import GameRegistration


def async_db_function(func):
    async def wrapper(*args, **kwargs):
        return await sync_to_async(func)(*args, **kwargs)
    return wrapper


@async_db_function
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


@async_db_function
def update_user_language(user_id, language):
    User.objects.filter(telegram_id=user_id).update(language=language)


@async_db_function
def update_user_phone_number(user_id, phone_number):
    User.objects.filter(telegram_id=user_id).update(phone_number=phone_number)


@async_db_function
def get_users_for_announcement():
    """
    Получает список пользователей, которые подписаны на рассылку игр.
    """
    return list(User.objects.filter(notifications_enabled=True))  # Возвращаем список для избежания проблем в async


@async_db_function
def get_users_for_broadcast():
    """
    Возвращает всех пользователей, которые подписаны на уведомления.
    """
    return list(User.objects.all())


@async_db_function
def get_user_by_telegram_id(user_id):
    """
    Асинхронно получает пользователя по telegram_id.
    """
    return User.objects.get(telegram_id=user_id)


@async_db_function
def save_user(user):
    """
    Асинхронно сохраняет изменения в объекте пользователя.
    """
    user.save()


@async_db_function
def register_user_for_game(user, game):
    with transaction.atomic():
        registration, created = GameRegistration.objects.get_or_create(user=user, game=game)
        if not created:
            registration.guests_count += 1
        registration.save()
        return registration.guests_count


@async_db_function
def unregister_user_from_game(user, game):
    try:
        registration = GameRegistration.objects.get(user=user, game=game)
        if registration.guests_count > 0:
            registration.guests_count -= 1
            registration.save()
            return registration.guests_count
        else:
            registration.delete()
            return 0
    except GameRegistration.DoesNotExist:
        return None


@async_db_function
def get_game_registrations(game):
    """
    Возвращает список регистраций для указанной игры.
    """
    return list(GameRegistration.objects.filter(game=game))


@async_db_function
def get_user_game_registrations(user):
    """
    Возвращает список игр, на которые пользователь зарегистрирован.
    """
    return list(GameRegistration.objects.filter(user=user).select_related('game'))


@async_db_function
def get_user_registrations(user):
    """
    Возвращает список регистраций пользователя.
    """
    return list(GameRegistration.objects.filter(user=user))


@async_db_function
def get_total_players_count_for_game(game):
    """
    Асинхронный метод для получения общего количества игроков, включая гостей, для заданной игры.
    """
    registrations = GameRegistration.objects.filter(game=game)
    total_count = sum(1 + reg.guests_count for reg in registrations)
    return total_count


async def get_closest_game():
    # Получаем текущее время
    now = timezone.localtime()

    # Ищем ближайшую игру с учётом времени
    closest_game = await Game.objects.filter(
        date__gte=now.date()
    ).exclude(
        date=now.date(), start_time__lt=now.time()
    ).order_by('date', 'start_time').afirst()

    return closest_game



@async_db_function
def is_user_registered_for_game(user, game):
    """
    Проверяет, зарегистрирован ли пользователь на указанную игру.
    """
    return GameRegistration.objects.filter(user=user, game=game).exists()


@async_db_function
def get_active_subscriptions():
    current_date = datetime.now().date()
    return User.objects.filter(subscription_end_date__isnull=False, subscription_end_date__gte=current_date)

