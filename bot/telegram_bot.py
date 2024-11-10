import os
import gettext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
import nest_asyncio
import asyncio


nest_asyncio.apply()


# Загрузка переменных окружения из .env файла
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

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


async def start(update: Update, context: CallbackContext) -> None:
    """
    Обработчик команды /start, выводит пользователю выбор языка.
    """
    user_id = update.effective_chat.id
    user_lang[user_id] = 'en'  # По умолчанию - английский язык

    # Кнопки для выбора языка
    keyboard = [
        [InlineKeyboardButton('Беларуская', callback_data='lang_be')],
        [InlineKeyboardButton('Українська', callback_data='lang_uk')],
        [InlineKeyboardButton('Polski', callback_data='lang_pl')],
        [InlineKeyboardButton('English', callback_data='lang_en')],
        [InlineKeyboardButton('Русский', callback_data='lang_ru')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Choose your language / Выберите язык:', reply_markup=reply_markup)


async def language_choice(update: Update, context: CallbackContext) -> None:
    """
    Обработчик выбора языка, сохраняет выбранный язык и отправляет приветственное сообщение.
    """
    query = update.callback_query
    user_id = query.message.chat.id

    if query.data.startswith('lang_'):
        selected_lang = query.data.split('_')[1]
        user_lang[user_id] = selected_lang
        langs[selected_lang].install()  # Устанавливаем gettext на нужный язык
        _ = langs[selected_lang].gettext

        # Отправляем приветственное сообщение после выбора языка
        await query.answer()
        welcome_message = _('Welcome to the Laser Tag Bot! You have selected the {} language.').format(selected_lang)
        await query.edit_message_text(text=welcome_message)

        # Запрашиваем номер телефона
        await request_phone_number(update, context, _)


async def request_phone_number(update: Update, context: CallbackContext, _) -> None:
    """
    Запрашивает у пользователя номер телефона после выбора языка.
    """
    # Кнопка для запроса номера телефона
    button = KeyboardButton(_('Share your phone number'), request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_('Please share your phone number so we can register you.'),
        reply_markup=reply_markup
    )


async def phone_number_received(update: Update, context: CallbackContext) -> None:
    """
    Обработчик получения номера телефона от пользователя.
    """
    user_phone_number = update.message.contact.phone_number
    user_id = update.effective_chat.id
    _ = langs[user_lang.get(user_id, 'en')].gettext

    # Сохраняем номер телефона пользователя (в базу данных или иную логику)
    await update.message.reply_text(
        _('Thank you for sharing your phone number! You are now registered.'),
        reply_markup=ReplyKeyboardMarkup([], remove_keyboard=True)
    )

    # Переход к основному меню
    await send_main_menu(update, context, _)


async def send_main_menu(update: Update, context: CallbackContext, _) -> None:
    """
    Отправляет основное меню пользователю после регистрации.
    """
    # Кнопки основного меню
    keyboard = [
        [InlineKeyboardButton(_('Register for the Game'), callback_data='register_game')],
        [InlineKeyboardButton(_('Unsubscribe from Notifications'), callback_data='unsubscribe')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Please choose an option:'),
                                   reply_markup=reply_markup)


async def main() -> None:
    """
    Основная функция запуска бота.
    """
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд и колбэков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_.*$'))
    application.add_handler(CommandHandler("phone_number", phone_number_received))

    # Запуск бота
    await application.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
