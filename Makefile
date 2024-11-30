# Переменные для использования в командах
ENV_FILE=.env

# Команда для установки зависимостей
install:
	poetry install

run-bot:
	python telegram_bot.py

# Команда для запуска сервера разработки
run:
	poetry run python manage.py runserver

# Команда для выполнения миграций
migrate:
	poetry run python manage.py migrate

# Команда для создания суперпользователя
createsuperuser:
	poetry run python manage.py createsuperuser

# Команда для запуска тестов
test:
	poetry run pytest --cov=bot --cov=laser_tag_admin --cov-report=html

# Команда для запуска шелла Django
shell:
	poetry run python manage.py shell

# Команда для создания файла с переводами (.pot)
translations:
	$(VENV) pybabel extract -F babel.cfg -o locale/messages.pot .

# Команда для компиляции переводов (.mo)
compile:
	$(VENV) pybabel compile -d locale
