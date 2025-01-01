import logging
import os
import django
from django.utils import timezone
from django.db import transaction
from datetime import datetime

from asgiref.sync import sync_to_async

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laser_tag_admin.settings')
django.setup()

# Импорт моделей после инициализации Django
from laser_tag_admin.users.models import User
from laser_tag_admin.games.models import Game, GameRegistration


logger = logging.getLogger(__name__)

class DatabaseManager:
    """Класс для управления операциями с базой данных."""

    def __init__(self):
        logger.info("DatabaseManager initialized")


    def async_db_method(func):
        """Декоратор для асинхронных методов."""
        async def wrapper(self, *args, **kwargs):
            return await sync_to_async(func)(self, *args, **kwargs)
        return wrapper


    @async_db_method
    def get_or_create_user(self, user_id, first_name, last_name, username):
        """Получает или создает пользователя."""
        return User.objects.get_or_create(
            telegram_id=user_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'language': 'en',
                'registration_date': timezone.now(),
                'notifications_enabled': True,
            }
        )


    @async_db_method
    def update_user_language(self, user_id, language):
        """Обновляет язык пользователя."""
        User.objects.filter(telegram_id=user_id).update(language=language)


    @async_db_method
    def update_user_phone_number(self, user_id, phone_number):
        """Обновляет номер телефона пользователя."""
        User.objects.filter(telegram_id=user_id).update(phone_number=phone_number)


    @async_db_method
    def get_users_for_announcement(self):
        """Получает пользователей, подписанных на рассылку игр."""
        return list(User.objects.filter(notifications_enabled=True))


    @async_db_method
    def get_users_for_broadcast(self):
        """Получает всех пользователей."""
        return list(User.objects.all())


    @async_db_method
    def get_user_by_telegram_id(self, user_id):
        """Получает пользователя по Telegram ID."""
        return User.objects.get(telegram_id=user_id)


    @async_db_method
    def save_user(self, user):
        """Сохраняет пользователя."""
        user.save()


    @async_db_method
    def register_user_for_game(self, user, game):
        """Регистрирует пользователя на игру."""
        with transaction.atomic():
            registration, created = GameRegistration.objects.get_or_create(user=user, game=game)
            if not created:
                registration.guests_count += 1
            registration.save()
            return registration.guests_count


    @async_db_method
    def unregister_user_from_game(self, user, game):
        """Отменяет регистрацию пользователя на игру."""
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


    @async_db_method
    def get_game_registrations(self, game):
        """Получает регистрации на указанную игру."""
        return list(GameRegistration.objects.filter(game=game))


    @async_db_method
    def get_game_by_id(self, game_id):
        """Получает игру по её идентификатору."""
        try:
            return Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return None


    @async_db_method
    def get_user_game_registrations(self, user):
        """Получает игры, на которые зарегистрирован пользователь."""
        return list(GameRegistration.objects.filter(user=user).select_related('game'))


    @async_db_method
    def get_user_registrations(self, user):
        """Получает регистрации пользователя."""
        return list(GameRegistration.objects.filter(user=user))

    @async_db_method
    def get_total_players_count_for_game(self, game):
        """Получает общее количество игроков на игру."""
        registrations = GameRegistration.objects.filter(game=game)
        total_count = sum(1 + reg.guests_count for reg in registrations)
        return total_count

    async def get_closest_game(self):
        """Получает ближайшую игру."""
        now = timezone.localtime()
        closest_game = await Game.objects.filter(
            date__gte=now.date()
        ).exclude(
            date=now.date(),
            start_time__lt=now.time()
        ).order_by('date', 'start_time').afirst()
        return closest_game

    @async_db_method
    def is_user_registered_for_game(self, user, game):
        """Проверяет, зарегистрирован ли пользователь на игру."""
        return GameRegistration.objects.filter(user=user, game=game).exists()

    @async_db_method
    def get_active_subscriptions(self):
        """Получает активные подписки пользователей."""
        current_date = datetime.now().date()
        return User.objects.filter(
            subscription_end_date__isnull=False,
            subscription_end_date__gte=current_date
        )
