import os
import gettext
import django
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from bot.admin.admin_handlers import (
    send_admin_menu,
    send_admin_settings_menu,
    send_announcement,
    broadcast_message_handler,
    handle_admin_game_interaction)
from bot.user.user_handlers import (
    send_user_menu,
    send_user_settings_menu,
    handle_user_game_interaction,
    show_subscription_status,
    toggle_subscription)
from bot.core.menu_utils import get_language_keyboard, show_language_selection
from bot.core.database_utils import (
    get_or_create_user,
    update_user_phone_number,
    update_user_language,
    get_closest_game)
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
import nest_asyncio
import asyncio


# Настройка логирования
logging.basicConfig(level=logging.INFO)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laser_tag_admin.settings')
django.setup()
from laser_tag_admin.users.models import User
from laser_tag_admin.games.models import Game


nest_asyncio.apply()  # Применяем патч для устранения проблем с вложенными вызовами asyncio

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получаем токен для Telegram бота из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

LANG_NAMES = {
    'be': 'Беларуская',
    'uk': 'Українська',
    'pl': 'Polski',
    'en': 'English',
    'ru': 'Русский'
}

# Инициализация gettext для поддержки нескольких языков
langs = {
    'be': gettext.translation('messages', localedir='locale', languages=['be']),
    'uk': gettext.translation('messages', localedir='locale', languages=['uk']),
    'pl': gettext.translation('messages', localedir='locale', languages=['pl']),
    'en': gettext.translation('messages', localedir='locale', languages=['en']),
    'ru': gettext.translation('messages', localedir='locale', languages=['ru'])
}

# Словарь для хранения выбранного языка пользователей
user_lang = {}


# Обработчик команды /start, выводит пользователю выбор языка
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id  # Получаем ID пользователя
    user_lang[user_id] = 'en'  # По умолчанию устанавливаем английский язык

    # Проверяем наличие пользователя в базе данных и создаем его при необходимости
    await get_or_create_user(
        user_id,
        update.effective_user.first_name,
        update.effective_user.last_name,
        update.effective_user.username
    )

    # Отправляем сообщение с кнопками выбора языка
    reply_markup = get_language_keyboard()
    await update.message.reply_text('Choose your language / Выберите язык:', reply_markup=reply_markup)


# Обработчик выбора языка, сохраняет выбранный язык и обновляет запись пользователя
async def language_choice(update: Update, context: CallbackContext) -> None:
    """
    Обработчик выбора языка, сохраняет выбранный язык и обновляет запись пользователя.
    """
    query = update.callback_query
    user_id = query.message.chat.id

    if query.data.startswith('lang_'):
        selected_lang = query.data.split('_')[1]
        user_lang[user_id] = selected_lang
        langs[selected_lang].install()  # Устанавливаем gettext на нужный язык
        _ = langs[selected_lang].gettext

        # Обновляем язык пользователя в базе данных
        await update_user_language(user_id, selected_lang)

        # Формируем приветственное сообщение
        welcome_message = _('Language has been updated. You have selected the {} language.').format(selected_lang)

        # Редактируем предыдущее сообщение с приветственным сообщением
        await query.edit_message_text(text=welcome_message)

        # Проверка наличия номера телефона и запрос его только при необходимости
        await check_and_request_phone_number(user_id, update, context, _)

        # Переход к основному меню после обновления языка
        await send_main_menu(update, context, _, query)



async def check_and_request_phone_number(user_id, update: Update, context: CallbackContext, _) -> None:
    """
    Проверяет, есть ли номер телефона в базе данных, и запрашивает его, если отсутствует.
    """
    # Получаем пользователя из базы данных
    user = await sync_to_async(User.objects.get)(telegram_id=user_id)

    if not user.phone_number:  # Проверяем, отсутствует ли номер телефона
        # Запрашиваем номер телефона, если он отсутствует
        await request_phone_number(update, context, _)


# Запрашивает у пользователя номер телефона после выбора языка
async def request_phone_number(update: Update, context: CallbackContext, _) -> None:
    # Создаем кнопку для запроса номера телефона
    button = KeyboardButton(_('Share your phone number'), request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)

    # Отправляем сообщение с кнопкой запроса номера телефона
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_('Please share your phone number so we can register you.'),
        reply_markup=reply_markup
    )


# Обработчик получения номера телефона от пользователя
async def phone_number_received(update: Update, context: CallbackContext) -> None:
    user_phone_number = update.message.contact.phone_number  # Получаем номер телефона
    user_id = update.effective_chat.id  # Получаем ID пользователя
    _ = langs[user_lang.get(user_id, 'en')].gettext

    # Обновляем номер телефона пользователя в базе данных
    await update_user_phone_number(user_id, user_phone_number)

    # Создаем кнопку для перехода к основному меню
    keyboard = [[InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопкой перехода к меню
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_('Thank you! Your phone number has been registered.'),
        reply_markup=reply_markup
    )

    # Переход к основному меню
    await send_main_menu(update, context, _)


async def send_main_menu(update, context: CallbackContext, _, query=None) -> None:
    """
    Определяет, какое меню отправить пользователю: администраторское или пользовательское.
    Если передан query, изменяет предыдущее сообщение.
    """
    user_id = update.effective_chat.id
    user = await sync_to_async(User.objects.get)(telegram_id=user_id)

    # Формируем меню для пользователя или администратора
    if user.is_admin:
        await send_admin_menu(update, context, _, query)
    else:
        await send_user_menu(update, context, _, query)


async def button_handler(update: Update, context: CallbackContext) -> None:
    """
    Обработчик для кнопок, который перенаправляет на нужные функции.
    """
    query = update.callback_query
    user_id = query.message.chat.id
    _ = langs[user_lang.get(user_id, 'en')].gettext

    # Получаем пользователя из базы данных
    user = await sync_to_async(User.objects.get)(telegram_id=user_id)

    if query.data == 'settings':
        if user.is_admin:
            await send_admin_settings_menu(update, context, _, query)
        else:
            await send_user_settings_menu(update, context, _, query)
        await query.answer()

    elif query.data == 'change_language':
        await show_language_selection(update, context, _, query)
        await query.answer()

    elif query.data == 'main_menu':
        await send_main_menu(update, context, _, query)
        await query.answer()

    elif query.data.startswith('announce_'):
        game_id = int(query.data.split('_')[1])
        game = await sync_to_async(Game.objects.get)(id=game_id)
        await send_announcement(update, context, game, _, query)
        await query.answer()

    elif query.data == 'close_message':
        await query.delete_message()  # Удаляет сообщение с кнопками
        await query.answer()

    elif query.data == 'broadcast_message':
        if user.is_admin:
            await context.bot.send_message(
                chat_id=user_id,
                text=_('Please enter the message you want to broadcast to all users:')
            )
            context.user_data['awaiting_broadcast_message'] = True
            await query.answer()

    elif query.data == 'open_game':
        # Получаем ближайшую игру
        closest_game = await get_closest_game()
        if closest_game:
            if user.is_admin:
                await handle_admin_game_interaction(update, context, _, user, closest_game, query)
            else:
                await handle_user_game_interaction(update, context, _, user, closest_game, query)
            await query.answer()
        else:
            await query.answer(_('No upcoming games available.'), show_alert=True)

    elif query.data == 'subscription_status':
        await show_subscription_status(update, context, _, query)
        await query.answer()

    elif query.data == 'toggle_subscription':
        await toggle_subscription(update, context, _)
        await query.answer()

        # Обработка кнопок регистрации и отмены регистрации
    elif query.data.startswith('register_'):
        try:
            game_id = int(query.data.split('_')[1])
            game = await sync_to_async(Game.objects.get)(id=game_id)
            await handle_user_game_interaction(update, context, _, user, game, query)
        except (ValueError, Game.DoesNotExist) as e:
            logging.error(f"Ошибка при регистрации на игру: {e}")
            await query.answer(_('Error during registration.'), show_alert=True)

    elif query.data.startswith('unregister_'):
        try:
            game_id = int(query.data.split('_')[1])
            game = await sync_to_async(Game.objects.get)(id=game_id)
            await handle_user_game_interaction(update, context, _, user, game, query)
        except (ValueError, Game.DoesNotExist) as e:
            logging.error(f"Ошибка при отмене регистрации на игру: {e}")
            await query.answer(_('Error during unregistration.'), show_alert=True)


# Основная функция запуска бота
async def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()  # Создаем экземпляр приложения Telegram

    # Добавляем обработчики команд и callback
    application.add_handler(CommandHandler("start", start))  # Обработчик команды /start
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: broadcast_message_handler(update, context, langs[user_lang.get(update.effective_chat.id, 'en')].gettext))) # Обработчик сообщений
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_.*$'))  # Обработчик выбора языка
    application.add_handler(CallbackQueryHandler(button_handler))  # Обработчик для всех остальных callback кнопок
    application.add_handler(MessageHandler(filters.CONTACT, phone_number_received))  # Обработчик получения номера телефона

    # Запускаем бот в режиме polling (опрос сервера)
    await application.run_polling()

# Запуск основного цикла событий
if __name__ == "__main__":
    loop = asyncio.get_event_loop()  # Создаем цикл событий
    try:
        loop.run_until_complete(main())  # Запускаем основную функцию
    except KeyboardInterrupt:
        pass  # Обрабатываем прерывание работы пользователем
