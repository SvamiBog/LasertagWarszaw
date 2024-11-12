# Dockerfile for Django Web Application
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root

# Применение миграций и сбор статических файлов
RUN poetry run python manage.py migrate
RUN poetry run python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
