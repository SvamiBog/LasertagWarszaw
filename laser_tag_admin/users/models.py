from django.db import models

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True, unique=True, verbose_name="ID в Telegram")
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Фамилия")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    games_played = models.PositiveIntegerField(default=0, verbose_name="Количество игр")
    subscribed_to_chat = models.BooleanField(default=False, verbose_name="Подписан на общий чат")

    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.telegram_id})"