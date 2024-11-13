#!/bin/sh

# Применяем миграции и собираем статику
python manage.py migrate
python manage.py collectstatic --noinput

# Запускаем веб-сервер в фоне
gunicorn laser_tag_admin.wsgi:application --bind 0.0.0.0:$PORT &

# Запускаем бота
poetry run python bot/telegram_bot.py
