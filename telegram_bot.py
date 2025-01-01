# main.py

import os
import logging
import asyncio
import django

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

# Инициализация Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laser_tag_admin.settings')
django.setup()

# Импортируем необходимые классы и функции
from bot.admin.admin_handlers import AdminHandler
from bot.user.user_handlers import UserHandler
from bot.handlers.common_handlers import (
    start_handler,
    language_choice_handler,
    phone_number_received_handler,
    button_handler,
    message_handler,
)
from bot.core.database_manager import DatabaseManager
from logging_config import setup_logging


# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Создаем экземпляры классов
db_manager = DatabaseManager()
admin_handler = AdminHandler()
user_handler = UserHandler()

async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CallbackQueryHandler(language_choice_handler, pattern='^lang_'))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.CONTACT, phone_number_received_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Инициализация и запуск бота
    await application.run_polling()

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    # Настройка логирования
    setup_logging()
    asyncio.run(main())

    # Запуск основного цикла бота
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())