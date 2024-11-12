from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Update
import logging
from bot.core.database_utils import get_users_for_announcement, get_users_for_broadcast, get_total_players_count_for_game


# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def send_admin_menu(update, context: CallbackContext, _, query=None) -> None:
    """
    Отправляет меню администратора. Если передан query, редактирует существующее сообщение.
    """
    keyboard = [
        [InlineKeyboardButton(_('Game Calendar'), callback_data='game_calendar')],
        [InlineKeyboardButton(_('Broadcast Message'), callback_data='broadcast_message')],
        [InlineKeyboardButton(_('Settings'), callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(text=_('Admin Menu:'), reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Admin Menu:'), reply_markup=reply_markup)



async def send_admin_settings_menu(update, context, _, query):
    """
    Отправляет меню настроек администратору.
    """
    # Создаем кнопки для меню настроек администратора
    keyboard = [
        [InlineKeyboardButton(_('Change Language'), callback_data='change_language')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=_('Admin Settings Menu:'), reply_markup=reply_markup)


async def handle_admin_game_interaction(update, context, _, user, game, query=None):
    """
    Обрабатывает взаимодействие администратора с игрой.
    """
    message = _('Game Details:\n')
    message += f"{_('Date')}: {game.date.strftime('%d.%m.%Y')}\n"
    message += f"{_('Start Time')}: {game.start_time.strftime('%H:%M')}\n"
    message += f"{_('Location')}: {game.location}\n"
    message += _('Players count: ') + str(await get_total_players_count_for_game(game)) + '\n'

    # Кнопки для администратора
    keyboard = [
        [InlineKeyboardButton(_('Send Announcement'), callback_data=f'announce_{game.id}')],
        [InlineKeyboardButton(_('Back to Game List'), callback_data='game_calendar')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        # Редактируем существующее сообщение
        await query.edit_message_text(text=message, reply_markup=reply_markup)
    else:
        # Отправляем новое сообщение, если query не передан
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)


async def send_announcement(update, context, game, _, query=None):
    """
    Отправляет рассылку по пользователям, которые не отказались от уведомлений.
    """
    users = await get_users_for_announcement()  # Получаем список пользователей

    message = _('Announcement for upcoming game:\n')
    message += f"{_('Date')}: {game.date.strftime('%d.%m.%Y')}\n"
    message += f"{_('Start Time')}: {game.start_time.strftime('%H:%M')}\n"
    message += f"{_('Location')}: {game.location}\n"

    success_count = 0
    fail_count = 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user.telegram_id, text=message)
            success_count += 1
        except Exception as e:
            logging.warning(f"Не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            fail_count += 1

    response_message = _('Announcement sent to subscribed users.\n')
    response_message += f"{_('Success')}: {success_count}\n"
    response_message += f"{_('Failed')}: {fail_count}\n"

    # Создаём клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton(_('View Game Details'), callback_data=f'game_info_{game.id}')],
        [InlineKeyboardButton(_('Close'), callback_data='close_message')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(text=response_message, reply_markup=reply_markup)
    else:
        await update.callback_query.answer(response_message)

    # Показ нового меню для администратора после рассылки
    await send_admin_menu(update, context, _)


async def broadcast_message_handler(update: Update, context: CallbackContext, _) -> None:
    """
    Обрабатывает ввод сообщения от администратора для рассылки.
    """
    # Проверяем, ожидается ли ввод сообщения для рассылки и является ли пользователь администратором
    if context.user_data.get('awaiting_broadcast_message'):
        broadcast_message = update.message.text  # Получаем текст сообщения
        context.user_data['awaiting_broadcast_message'] = False  # Сбрасываем флаг ожидания

        # Получаем пользователей для рассылки
        users = await get_users_for_broadcast()

        # Отправляем сообщение каждому пользователю
        for recipient in users:
            try:
                await context.bot.send_message(chat_id=recipient.telegram_id, text=broadcast_message)
            except Exception as e:
                logging.warning(f"Не удалось отправить сообщение пользователю {recipient.telegram_id}: {e}")

        # Подтверждаем администратору успешное завершение рассылки
        await update.message.reply_text(_('Broadcast sent successfully to all subscribed users.'))

        # Открываем новое меню для администратора после рассылки
        await send_admin_menu(update, context, _)
