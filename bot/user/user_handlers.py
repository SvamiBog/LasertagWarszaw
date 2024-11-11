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

    # Отправляем сообщение с кнопками меню настроек пользователя
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('User Settings menu:'), reply_markup=reply_markup)


async def handle_user_game_interaction(update, context, _, user, game):
    """
    Обрабатывает взаимодействие с игрой для пользователя.
    """
    query = update.callback_query

    # Формируем сообщение для пользователя
    message = _('Game Details:\n')
    message += f"{game.date.strftime('%d.%m.%y')} - {game.start_time.strftime('%H:%M')}\n"
    message += _('You can register or unregister from this game.')

    # Кнопки для пользователя
    keyboard = [
        [InlineKeyboardButton(_('Register for Game'), callback_data=f'register_{game.id}')],
        [InlineKeyboardButton(_('Unregister from Game'), callback_data=f'unregister_{game.id}')],
        [InlineKeyboardButton(_('View Participants'), callback_data=f'view_{game.id}')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    await query.answer()
