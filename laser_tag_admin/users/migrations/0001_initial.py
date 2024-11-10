# Generated by Django 5.1.3 on 2024-11-10 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('telegram_id', models.BigIntegerField(primary_key=True, serialize=False, unique=True, verbose_name='ID в Telegram')),
                ('first_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Фамилия')),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='Номер телефона')),
                ('games_played', models.PositiveIntegerField(default=0, verbose_name='Количество игр')),
                ('subscribed_to_chat', models.BooleanField(default=False, verbose_name='Подписан на общий чат')),
            ],
            options={
                'verbose_name': 'Пользователь Telegram',
                'verbose_name_plural': 'Пользователи Telegram',
            },
        ),
    ]
