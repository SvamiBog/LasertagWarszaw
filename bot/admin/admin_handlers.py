import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Update
from asgiref.sync import sync_to_async
import logging
import gettext
import os
from dotenv import load_dotenv
from bot.core.database_utils import (
    get_users_for_announcement,
    get_users_for_broadcast,
    get_total_players_count_for_game,
    get_game_registrations,
    get_closest_game,
    get_active_subscriptions)


# Настройка логирования
logging.basicConfig(level=logging.INFO)
load_dotenv()

langs = {
    'be': gettext.translation('messages', localedir='locale', languages=['be']),
    'uk': gettext.translation('messages', localedir='locale', languages=['uk']),
    'pl': gettext.translation('messages', localedir='locale', languages=['pl']),
    'en': gettext.translation('messages', localedir='locale', languages=['en']),
    'ru': gettext.translation('messages', localedir='locale', languages=['ru'])
}


async def send_admin_menu(update, context: CallbackContext, _, query=None) -> None:
    """
    Отправляет меню администратора. Если передан query, редактирует существующее сообщение.
    """
    keyboard = [
        [InlineKeyboardButton(_('Open Game'), callback_data='open_game')],
        [InlineKeyboardButton(_('Broadcast Message'), callback_data='broadcast_message')],
        [InlineKeyboardButton(_('Send Game Info to General Chat'), callback_data='send_game_info_general_chat')],
        [InlineKeyboardButton(_('Club Card'), callback_data='club_card')],
        [InlineKeyboardButton(_('Settings'), callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(text=_('Admin Menu:'), reply_markup=reply_markup)
    except telegram.error.BadRequest as e:
        if "Message to edit not found" in str(e):
            # Альтернативное действие, например, отправка нового сообщения
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_('Admin Menu:'),
                                           reply_markup=reply_markup)

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


async def send_announcement(update, context, game, _, query=None):
    """
    Отправляет рассылку по пользователям, которые не отказались от уведомлений, на языке, выбранном пользователем.
    """
    # Получаем список пользователей, которые не отказались от уведомлений
    users = await get_users_for_announcement()  # Ожидается, что эта функция вернет пользователей с notifications_enabled=True

    success_count = 0
    fail_count = 0

    for user in users:
        user_lang_code = user.language  # Извлекаем язык пользователя из модели
        user_gettext = langs.get(user_lang_code, langs['en']).gettext  # Получаем переводчик на основе языка пользователя

        # Формируем сообщение для пользователя на его языке
        message = user_gettext('Announcement for upcoming game:\n')
        message += f"{user_gettext('Date')}: {game.date.strftime('%d.%m.%Y')}\n"
        message += f"{user_gettext('Start Time')}: {game.start_time.strftime('%H:%M')}\n"
        message += f"{user_gettext('Location')}: {game.location}\n"

        # Отправка сообщения пользователю
        try:
            await context.bot.send_message(chat_id=user.telegram_id, text=message)
            success_count += 1
        except Exception as e:
            logging.warning(f"Не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
            fail_count += 1

    # Создаем сообщение для администратора о результатах рассылки
    response_message = _('Announcement sent to subscribed users.\n')
    response_message += f"{_('Success')}: {success_count}\n"
    response_message += f"{_('Failed')}: {fail_count}\n"

    # Создаем клавиатуру с кнопками
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


async def handle_admin_game_interaction(update, context, _, user, game=None, query=None):
    """
    Обрабатывает взаимодействие администратора с ближайшей игрой.
    """
    if query is None:
        query = update.callback_query

    # Если игра не передана, получаем ближайшую игру
    if game is None:
        game = await get_closest_game()  # Предполагается, что эта функция возвращает ближайшую игру

    if not game:
        message = _('No upcoming games found.')
        keyboard = [[InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if query:
            await query.edit_message_text(text=message, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)
        await query.answer()
        return

    # Получаем список регистраций для данной игры
    registrations = await get_game_registrations(game)

    # Формируем сообщение с деталями игры
    message = _('Game Details:\n')
    message += f"{_('Date')}: {game.date.strftime('%d.%m.%Y')}\n"
    message += f"{_('Start Time')}: {game.start_time.strftime('%H:%M')}\n"
    message += f"{_('Location')}: {game.location}\n"
    message += _('Players count: ') + str(await get_total_players_count_for_game(game)) + '\n'
    message += f"\n{_('Participants List')}:\n"

    if registrations:
        for reg in registrations:
            # Получаем связанные данные пользователя с использованием sync_to_async
            reg_user = await sync_to_async(lambda: reg.user)()
            message += f"- {reg_user.first_name} {reg_user.last_name} (Guests: {reg.guests_count})\n"
    else:
        message += _('No participants yet.')

    # Кнопки для администратора
    keyboard = [
        [InlineKeyboardButton(_('Send Announcement'), callback_data=f'announce_{game.id}')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        # Редактируем существующее сообщение
        await query.edit_message_text(text=message, reply_markup=reply_markup)
    else:
        # Отправляем новое сообщение, если query не передан
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

    await query.answer()


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


async def send_game_info_to_general_chat(context: CallbackContext, game, _) -> None:
    """
    Отправляет сообщение с деталями игры и списком участников в общий чат.
    """
    # Получаем список регистраций для данной игры
    registrations = await get_game_registrations(game)

    # Формируем сообщение с деталями игры и участниками
    message = _('Game Details:\n')
    message += f"{_('Date')}: {game.date.strftime('%d.%m.%Y')}\n"
    message += f"{_('Start Time')}: {game.start_time.strftime('%H:%M')}\n"
    message += f"{_('Location')}: {game.location}\n"
    message += _('Players count: ') + str(await get_total_players_count_for_game(game)) + '\n'
    message += f"\n{_('Participants List')}:\n"

    if registrations:
        for reg in registrations:
            reg_user = await sync_to_async(lambda: reg.user)()
            message += f"- {reg_user.first_name} {reg_user.last_name} (Guests: {reg.guests_count})\n"
    else:
        message += _('No participants yet.')

    # Кнопки для регистрации и отмены регистрации (без кнопки "Main Menu")
    keyboard = [
        [InlineKeyboardButton(_('Register for Game'), callback_data=f'register_{game.id}')],
        [InlineKeyboardButton(_('Unregister from Game'), callback_data=f'unregister_{game.id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Получаем ID общего чата из переменных окружения
    general_chat_id = os.getenv('GENERAL_CHAT_ID')

    if general_chat_id:
        # Отправляем сообщение в общий чат
        await context.bot.send_message(chat_id=general_chat_id, text=message, reply_markup=reply_markup)
    else:
        logging.error('GENERAL_CHAT_ID is not set in the environment variables.')


async def handle_admin_club_card(update, context, _, query):
    active_users = await get_active_subscriptions()  # Вызываем корутину и получаем результат

    # Проверяем, существуют ли активные пользователи асинхронно
    active_users_exist = await sync_to_async(active_users.exists)()

    if active_users_exist:
        # Формируем сообщение с информацией о пользователях
        message = _('Active club card users:\n')
        for user in await sync_to_async(list)(active_users):
            message += f"{user.first_name} {user.last_name} - {user.subscription_end_date.strftime('%d.%m.%Y')}\n"
        print(f"DEBUG: Найдено активных пользователей: {len(active_users)}")
    else:
        message = _('No active club card users.')
        print("DEBUG: Нет активных пользователей")

    keyboard = [[InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(text=message, reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, reply_markup=reply_markup)

