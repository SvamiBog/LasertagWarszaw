from django.db import models
from django.utils import timezone
from laser_tag_admin.users.models import User
from asgiref.sync import sync_to_async
import pytz


class Game(models.Model):
    date = models.DateField(verbose_name='Дата игры')
    start_time = models.TimeField(verbose_name='Время начала игры')
    location = models.CharField(max_length=255, verbose_name='Место проведения игры')

    def __str__(self):
        return f"Игра {self.id} - {self.date} {self.start_time}"

    async def get_total_players_count(self):
        """
        Возвращает общее количество игроков, включая гостей.
        """
        registrations = await sync_to_async(list)(self.registrations.all())
        total_count = sum(1 + reg.guests_count for reg in registrations)
        return total_count

    def get_status_display(self):
        warsaw_timezone = pytz.timezone('Europe/Warsaw')
        current_datetime = timezone.now().astimezone(warsaw_timezone)
        game_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.start_time),
            warsaw_timezone
        )
        end_datetime = game_datetime + timezone.timedelta(hours=2)

        if current_datetime < game_datetime:
            return 'Предстоящая игра'
        elif game_datetime <= current_datetime <= end_datetime:
            return 'Проходит сейчас'
        else:
            return 'Закончена'

    class Meta:
        verbose_name = 'Игра'
        verbose_name_plural = 'Игры'



class GameRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations', verbose_name='Пользователь')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='registrations', verbose_name='Игра')
    guests_count = models.PositiveIntegerField(default=0, verbose_name='Количество гостей')

    def __str__(self):
        return f"{self.user} - Игра {self.game.id} ({self.guests_count} гостей)"

    class Meta:
        verbose_name = 'Регистрация на игру'
        verbose_name_plural = 'Регистрации на игры'
        unique_together = ('user', 'game')
