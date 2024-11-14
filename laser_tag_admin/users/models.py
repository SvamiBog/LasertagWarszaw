from django.db import models
from django.utils import timezone
from pytz import timezone as pytz_timezone

# Установим временную зону Варшава
warsaw_tz = pytz_timezone('Europe/Warsaw')

class User(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True, unique=True, verbose_name="ID в Telegram")
    first_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Фамилия")
    username = models.CharField(max_length=150, unique=True, null=True, blank=True, verbose_name="Имя пользователя")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    language = models.CharField(max_length=10, default='en', verbose_name="Язык")
    notifications_enabled = models.BooleanField(default=True, verbose_name="Уведомления включены")
    registration_date = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    subscription_end_date = models.DateField(null=True, blank=True, verbose_name="Дата окончания подписки")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['registration_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.telegram_id})"

    def has_active_subscription(self):
        """
        Проверяет, есть ли активная подписка у пользователя.
        """
        if self.subscription_end_date:
            return self.subscription_end_date >= timezone.now().date()
        return False
