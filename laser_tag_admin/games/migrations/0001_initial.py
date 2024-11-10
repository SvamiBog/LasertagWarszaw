# Generated by Django 5.1.3 on 2024-11-10 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата игры')),
                ('start_time', models.TimeField(verbose_name='Время начала игры')),
                ('location', models.CharField(max_length=255, verbose_name='Место проведения игры')),
                ('players_count', models.PositiveIntegerField(default=0, verbose_name='Количество записанных игроков')),
                ('status', models.CharField(choices=[('upcoming', 'Предстоящая игра'), ('ongoing', 'Проходит сейчас'), ('finished', 'Закончена')], default='upcoming', max_length=10, verbose_name='Статус игры')),
            ],
            options={
                'verbose_name': 'Игра',
                'verbose_name_plural': 'Игры',
            },
        ),
    ]
