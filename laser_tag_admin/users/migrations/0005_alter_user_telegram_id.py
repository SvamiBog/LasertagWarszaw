# Generated by Django 5.1.3 on 2024-12-08 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_subscription_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='telegram_id',
            field=models.BigIntegerField(primary_key=True, serialize=False, verbose_name='ID в Telegram'),
        ),
    ]
