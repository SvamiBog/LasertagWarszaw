# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Устанавливаем Poetry и зависимости
RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

# Копируем весь проект
COPY . .

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Применяем миграции базы данных
RUN python manage.py migrate --noinput

# Открываем порт 8000
EXPOSE 8000

# Запускаем приложение с Gunicorn
CMD ["gunicorn", "laser_tag_admin.wsgi:application", "--bind", "0.0.0.0:8000"]
