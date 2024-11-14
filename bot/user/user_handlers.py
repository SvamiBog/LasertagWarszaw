from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from asgiref.sync import sync_to_async
from bot.core.database_utils import (
    get_user_by_telegram_id,
    save_user,
    get_game_registrations,
    get_user_registrations,
    get_total_players_count_for_game
)
import logging


# Настройка логирования
logging.basicConfig(level=logging.INFO)


async def send_user_menu(update, context: CallbackContext, _, query=None) -> None:
    """
    Отправляет меню пользователя. Если передан query, редактирует существующее сообщение.
    """
    keyboard = [
        [InlineKeyboardButton(_('Open Game'), callback_data='open_game')],
        [InlineKeyboardButton(_('Club Card'), callback_data='club_card')],
        [InlineKeyboardButton(_('General Chat'), url='https://t.me/lasertawarsaw')],
        [InlineKeyboardButton(_('Settings'), callback_data='settings')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    menu_text = _('User Menu:')

    if query:
        current_text = query.message.text
        if current_text != menu_text:
            await query.edit_message_text(text=menu_text, reply_markup=reply_markup)
        else:
            print(_("Message not changed, skipping edit."))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=menu_text, reply_markup=reply_markup)


async def send_user_settings_menu(update, context: CallbackContext, _, query=None) -> None:
    """
    Отправляет меню настроек для пользователя.
    """
    logging.info("Функция send_user_settings_menu вызвана.")  # Логирование

    # Создаем кнопки для меню настроек пользователя
    keyboard = [
        [InlineKeyboardButton(_('Subscription Status'), callback_data='subscription_status')],
        [InlineKeyboardButton(_('Change Language'), callback_data='change_language')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Если передан query, редактируем сообщение, иначе отправляем новое сообщение
    if query:
        await query.edit_message_text(text=_('User Settings menu:'), reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_('User Settings menu:'), reply_markup=reply_markup)


async def show_subscription_status(update, context: CallbackContext, _, query) -> None:
    """
    Отображает статус подписки пользователя с возможностью переключения.
    """
    user_id = update.effective_chat.id
    user = await get_user_by_telegram_id(user_id)
    subscription_status = _('Enabled') if user.notifications_enabled else _('Disabled')

    status_message = f"{_('Subscription status')}: {subscription_status}"

    # Кнопки для переключения статуса и возврата в меню
    keyboard = [
        [InlineKeyboardButton(_('Toggle Subscription'), callback_data='toggle_subscription')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверка, чтобы избежать ошибки "Message is not modified"
    if query.message.text != status_message:
        await query.edit_message_text(text=status_message, reply_markup=reply_markup)
    else:
        await query.answer(_('No changes were made to the message.'))


# Обработчик для переключения подписки
async def toggle_subscription(update, context: CallbackContext, _) -> None:
    """
    Переключает статус подписки пользователя и отображает обновленный статус.
    """
    user_id = update.effective_chat.id
    user = await get_user_by_telegram_id(user_id)

    # Переключаем статус подписки
    user.notifications_enabled = not user.notifications_enabled
    await save_user(user)  # Сохраняем изменения в базе данных

    # Определяем новый статус подписки
    subscription_status = _('Enabled') if user.notifications_enabled else _('Disabled')
    status_message = f"{_('Subscription status')}: {subscription_status}"

    # Кнопки для переключения статуса и возврата в меню
    keyboard = [
        [InlineKeyboardButton(_('Toggle Subscription'), callback_data='toggle_subscription')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    await query.edit_message_text(text=status_message, reply_markup=reply_markup)
    await query.answer(_('Subscription status updated.'))


async def handle_user_game_interaction(update, context, _, user, game, query=None):
    """
    Обрабатывает взаимодействие с игрой для пользователя, отображает список участников.
    """
    if query is None:
        query = update.callback_query

    # Проверяем, есть ли игра
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

    # Кнопки для регистрации и отмены регистрации
    keyboard = [
        [InlineKeyboardButton(_('Register for Game'), callback_data=f'register_{game.id}')],
        [InlineKeyboardButton(_('Unregister from Game'), callback_data=f'unregister_{game.id}')],
        [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Проверяем, отличается ли новое сообщение или разметка от текущего
    if query.message.text != message or query.message.reply_markup != reply_markup:
        await query.edit_message_text(text=message, reply_markup=reply_markup)
    else:
        await query.answer('Message is not modified.')

    await query.answer()


async def show_user_game_registrations(update, context, user, _):
    """
    Отображает список игр, на которые пользователь записан, с кнопками.
    """
    registrations = await get_user_registrations(user)

    if registrations:
        keyboard = []
        for reg in registrations:
            game = await sync_to_async(lambda: reg.game)()  # Убедитесь, что доступ к game осуществляется асинхронно
            button_text = f"{game.date.strftime('%d.%m.%Y')} {game.start_time.strftime('%H:%M')}"
            callback_data = f"game_info_{game.id}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

        # Добавляем кнопку для возврата в главное меню
        keyboard.append([InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=_('Your registered games:'),
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.answer(
            text=_('You have no game registrations.'),
            show_alert=True
        )
