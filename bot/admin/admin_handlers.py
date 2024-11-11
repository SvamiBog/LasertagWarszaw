from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def send_admin_menu(update, context: CallbackContext, _) -> None:
    """
    Отправляет меню администратора.
    """
    keyboard = [
        [InlineKeyboardButton(_('Upcoming Games'), callback_data='upcoming_games')],
        [InlineKeyboardButton(_('Broadcast Message'), callback_data='broadcast_message')],
        [InlineKeyboardButton(_('Settings'), callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Admin Menu:'), reply_markup=reply_markup)


async def send_admin_settings_menu(update, context: CallbackContext, _) -> None:
    """
    Отправляет меню настроек для администратора.
    """
    logging.info("Функция send_admin_settings_menu вызвана.")  # Логирование
    # Создаем кнопки для меню настроек администратора
    keyboard = [
        [InlineKeyboardButton(_('Change Language'), callback_data='change_language')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query

    # Удаление предыдущего сообщения, если возможно
    try:
        await context.bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    except Exception as e:
        logging.warning(f"Не удалось удалить сообщение: {e}")

    # Отправляем сообщение с кнопками меню настроек администратора
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Admin Settings menu:'), reply_markup=reply_markup)
