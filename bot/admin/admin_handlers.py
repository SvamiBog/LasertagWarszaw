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
        [InlineKeyboardButton(_('Game Calendar'), callback_data='game_calendar')],
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

    # Отправляем сообщение с кнопками меню настроек администратора
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Admin Settings menu:'), reply_markup=reply_markup)


async def handle_admin_game_interaction(update, context, _, user, game):
    """
    Обрабатывает взаимодействие с игрой для администратора.
    """
    query = update.callback_query

    # Формируем сообщение для администратора
    message = _('Game Details:\n')
    message += f"{game.date.strftime('%d.%m.%y')} - {game.start_time.strftime('%H:%M')}\n"
    message += _('Players count: ') + str(game.players_count) + '\n'
    message += _('Players list: [function to list players]')  # Подставьте функцию для отображения списка игроков

    # Кнопки для администратора
    keyboard = [
        [InlineKeyboardButton(_('Send Announcement'), callback_data=f'announce_{game.id}')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    await query.answer()
