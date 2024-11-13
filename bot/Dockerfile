# bot/Dockerfile

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry и зависимости
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Копируем код бота
COPY . .

# Устанавливаем переменную PYTHONPATH
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["poetry", "run", "python", "bot/telegram_bot.py"]
