FROM python:3.12-slim

WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Установка зависимостей
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root

# Применение миграций
RUN poetry run python manage.py migrate

# Команда запуска бота
CMD ["poetry", "run", "python", "bot/telegram_bot.py"]
