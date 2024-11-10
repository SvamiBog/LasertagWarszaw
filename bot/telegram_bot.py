import os
import gettext
import django
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from dotenv import load_dotenv
from asgiref.sync import sync_to_async
import nest_asyncio
import asyncio
from django.utils import timezone


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laser_tag_admin.settings')
django.setup()

from laser_tag_admin.users.models import User

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

# Асинхронная функция для создания или получения пользователя в базе данных
@sync_to_async
def get_or_create_user(user_id, first_name, last_name, username):
    # Проверяем, существует ли пользователь с данным ID, если нет, создаем нового
    return User.objects.get_or_create(
        telegram_id=user_id,
        defaults={
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'language': 'en',
            'registration_date': timezone.now(),  # Записываем текущую дату и время
            'notifications_enabled': True  # Уведомления включены по умолчанию
        }
    )

# Асинхронная функция для обновления языка пользователя в базе данных
@sync_to_async
def update_user_language(user_id, language):
    User.objects.filter(telegram_id=user_id).update(language=language)

# Асинхронная функция для обновления номера телефона пользователя в базе данных
@sync_to_async
def update_user_phone_number(user_id, phone_number):
    User.objects.filter(telegram_id=user_id).update(phone_number=phone_number)

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

    # Создаем кнопки для выбора языка
    keyboard = [
        [InlineKeyboardButton('Беларуская', callback_data='lang_be')],
        [InlineKeyboardButton('Українська', callback_data='lang_uk')],
        [InlineKeyboardButton('Polski', callback_data='lang_pl')],
        [InlineKeyboardButton('English', callback_data='lang_en')],
        [InlineKeyboardButton('Русский', callback_data='lang_ru')],
    ]

    # Отправляем сообщение с кнопками выбора языка
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose your language / Выберите язык:', reply_markup=reply_markup)

# Обработчик выбора языка, сохраняет выбранный язык и обновляет запись пользователя
async def language_choice(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Получаем callback query (ответ пользователя)
    user_id = query.message.chat.id  # Получаем ID пользователя

    if query.data.startswith('lang_'):  # Проверяем, начинается ли data с 'lang_'
        selected_lang = query.data.split('_')[1]  # Получаем выбранный язык
        user_lang[user_id] = selected_lang  # Сохраняем выбранный язык для пользователя

        # Обновляем язык пользователя в базе данных
        await update_user_language(user_id, selected_lang)

        # Явно загружаем перевод для конкретного языка пользователя
        user_translation = langs[selected_lang]  # Получаем объект переводов для выбранного языка
        _ = user_translation.gettext  # Получаем функцию для перевода

        # Отправляем приветственное сообщение на выбранном языке
        await query.answer()
        full_language_name = LANG_NAMES.get(selected_lang, selected_lang)
        translated_message = _('Welcome to the Laser Tag Bot! You have selected the {} language.').format(full_language_name)
        await query.edit_message_text(text=translated_message)

        # Запрашиваем номер телефона
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

    # Отправляем сообщение об успешной регистрации
    await update.message.reply_text(
        _('Thank you for sharing your phone number! You are now registered.'),
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру
    )

    # Переход к основному меню
    await send_main_menu(update, context, _)

# Отправляет основное меню пользователю после регистрации
async def send_main_menu(update: Update, context: CallbackContext, _) -> None:
    # Создаем кнопки для основного меню
    keyboard = [
        [InlineKeyboardButton(_('Register for the Game'), callback_data='register_game')],
        [InlineKeyboardButton(_('Unsubscribe from Notifications'), callback_data='unsubscribe')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с кнопками основного меню
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Please choose an option:'),
                                   reply_markup=reply_markup)

# Основная функция запуска бота
async def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()  # Создаем экземпляр приложения Telegram

    # Добавляем обработчики команд и callback
    application.add_handler(CommandHandler("start", start))  # Обработчик команды /start
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_.*$'))  # Обработчик выбора языка
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
