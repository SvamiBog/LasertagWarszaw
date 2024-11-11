from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def send_user_menu(update, context: CallbackContext, _) -> None:
    """
    Отправляет меню пользователя.
    """
    keyboard = [
        [InlineKeyboardButton(_('Game Calendar'), callback_data='game_calendar')],
        [InlineKeyboardButton(_('My Game Registrations'), callback_data='my_game_registrations')],
        [InlineKeyboardButton(_('Settings'), callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('User Menu:'), reply_markup=reply_markup)


async def send_user_settings_menu(update, context: CallbackContext, _) -> None:
    """
    Отправляет меню настроек для пользователя.
    """
    logging.info("Функция send_user_settings_menu вызвана.")  # Логирование
    # Создаем кнопки для меню настроек пользователя
    keyboard = [
        [InlineKeyboardButton(_('Change Language'), callback_data='change_language')],
        [InlineKeyboardButton(_('Unsubscribe from Game Notifications'), callback_data='unsubscribe')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    # Удаление предыдущего сообщения, если возможно
    try:
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение: {e}")

    # Отправляем сообщение с кнопками меню настроек пользователя
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('User Settings menu:'), reply_markup=reply_markup)
