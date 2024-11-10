# Переменные для использования в командах
ENV_FILE=.env

# Команда для установки зависимостей
install:
	poetry install

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
	poetry run pytest --cov=laser_tag_admin --cov-report=html

# Команда для запуска шелла Django
shell:
	poetry run python manage.py shell

# Команда для загрузки переменных окружения и проверки соединения с базой данных
check-env:
	@echo "SECRET_KEY=$$(grep DJANGO_SECRET_KEY $(ENV_FILE))"
	@echo "DB_NAME=$$(grep DB_NAME $(ENV_FILE))"
	@echo "DB_USER=$$(grep DB_USER $(ENV_FILE))"
