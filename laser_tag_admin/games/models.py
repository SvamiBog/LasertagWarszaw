from django.db import models
from django.utils import timezone
import pytz

class Game(models.Model):
    date = models.DateField(verbose_name='Дата игры')
    start_time = models.TimeField(verbose_name='Время начала игры')
    location = models.CharField(max_length=255, verbose_name='Место проведения игры')
    players_count = models.PositiveIntegerField(default=0, editable=False, verbose_name='Количество записанных игроков')

    def __str__(self):
        return f"Игра {self.id} - {self.date} {self.start_time}"

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
