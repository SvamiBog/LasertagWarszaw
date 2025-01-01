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

# Переменные
SRC_DIR = .
LOCALE_DIR = locale
DOMAIN = messages

# Языки для перевода
LANGUAGES = be en pl ru uk

# Шаблон перевода
POT_FILE = $(DOMAIN).pot

# Файл правил
.PHONY: extract update compile clean

# Извлечение строк для перевода
extract:
	find $(SRC_DIR) -name "*.py" | xargs xgettext -o $(POT_FILE)

# Обновление файлов перевода (.po)
update:
	@for lang in $(LANGUAGES); do \
		mkdir -p $(LOCALE_DIR)/$$lang/LC_MESSAGES; \
		if [ -f $(LOCALE_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).po ]; then \
			msgmerge -U $(LOCALE_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).po $(POT_FILE); \
		else \
			msginit -i $(POT_FILE) -o $(LOCALE_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).po --locale=$$lang; \
		fi \
	done

# Компиляция переводов (.mo)
compile:
	@for lang in $(LANGUAGES); do \
		msgfmt -o $(LOCALE_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo $(LOCALE_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).po; \
	done

# Очистка сгенерированных файлов
clean:
	rm -f $(POT_FILE)
	@for lang in $(LANGUAGES); do \
		rm -f $(LOCALE_DIR)/$$lang/LC_MESSAGES/$(DOMAIN).mo; \
	done

