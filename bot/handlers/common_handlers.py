import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext

from bot.utils.localization import get_gettext, LANGUAGES
from bot.keyboards.common_keyboards import get_language_keyboard
from bot.core.database_manager import DatabaseManager
from bot.admin.admin_handlers import AdminHandler
from bot.user.user_handlers import UserHandler

db_manager = DatabaseManager()
admin_handler = AdminHandler()
user_handler = UserHandler()

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: CallbackContext):
    user, created = await db_manager.get_or_create_user(
        user_id=update.effective_user.id,
        first_name=update.effective_user.first_name or "",
        last_name=update.effective_user.last_name or "",
        username=update.effective_user.username or ""
    )

    # Устанавливаем язык пользователя по умолчанию
    lang_code = user.language or 'en'
    _ = get_gettext(lang_code)

    # Отправляем сообщение с выбором языка
    reply_markup = get_language_keyboard()
    await update.message.reply_text(_('Choose your language:'), reply_markup=reply_markup)

async def language_choice_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data.startswith('lang_'):
        selected_lang = query.data.split('_')[1]
        await db_manager.update_user_language(user_id, selected_lang)
        _ = get_gettext(selected_lang)

        # Отправляем подтверждение
        welcome_message = _('Language has been updated. You have selected the {} language.').format(
            LANGUAGES[selected_lang])
        await query.delete_message()
        await query.answer(welcome_message, show_alert=False)

        # Проверяем наличие номера телефона
        user = await db_manager.get_user_by_telegram_id(user_id)
        if not user.phone_number:
            await request_phone_number(update, context, _)
        else:
            await send_main_menu(update, context, user, _)

async def phone_number_received_handler(update: Update, context: CallbackContext):
    user_phone_number = update.message.contact.phone_number
    user_id = update.effective_chat.id
    user = await db_manager.get_user_by_telegram_id(user_id)
    lang_code = user.language or 'en'
    _ = get_gettext(lang_code)

    # Обновляем номер телефона
    await db_manager.update_user_phone_number(user_id, user_phone_number)

    await update.message.reply_text(
        text=_('Thank you! Your phone number has been registered.'),
        reply_markup=ReplyKeyboardRemove(),
        quote=False
    )

    await send_main_menu(update, context, user, _)


async def send_main_menu(update: Update, context: CallbackContext, user, _, query=None):
    if user.is_admin:
        await admin_handler.send_admin_menu(update, context, _, query)
    else:
        await user_handler.send_user_menu(update, context, _, query)


async def button_handler(update: Update, context: CallbackContext):
    """Handler for all callback queries (button presses)."""
    query = update.callback_query
    user_id = query.from_user.id
    user = await db_manager.get_user_by_telegram_id(user_id)
    lang_code = user.language or 'en'
    _ = get_gettext(lang_code)
    data = query.data

    if data == 'settings':
        if user.is_admin:
            await admin_handler.send_admin_settings_menu(update, context, _, query)
        else:
            await user_handler.send_user_settings_menu(update, context, _, query)
        await query.answer()

    elif data == 'change_language':
        reply_markup = get_language_keyboard()
        await query.edit_message_text(_('Choose your language:'), reply_markup=reply_markup)
        await query.answer()

    elif data == 'main_menu':
        await send_main_menu(update, context, user, _, query)
        await query.answer()

    elif data == 'open_game':
        game = await db_manager.get_closest_game()
        if game:
            if user.is_admin:
                await admin_handler.handle_admin_game_interaction(update, context, _, user, game, query)
            else:
                await user_handler.handle_user_game_interaction(update, context, _, user, game, query)
            await query.answer()
        else:
            await query.answer(_('No upcoming games available.'), show_alert=True)

    elif data == 'subscription_status':
        await user_handler.show_subscription_status(update, context, _, query)
        await query.answer()

    elif data == 'toggle_subscription':
        await user_handler.toggle_subscription(update, context, _)
        await query.answer(_('Subscription status updated.'))

    elif data == 'club_card':
        if user.is_admin:
            await admin_handler.handle_admin_club_card(update, context, _, query)
        else:
            await user_handler.handle_user_club_card(update, context, _, user, query)
        await query.answer()

    elif data == 'broadcast_message':
        if user.is_admin:
            await context.bot.send_message(
                chat_id=user_id,
                text=_('Please enter the message you want to broadcast to all users:')
            )
            context.user_data['awaiting_broadcast_message'] = True
            await query.answer()

    elif data == 'send_game_info_general_chat':
        game = await db_manager.get_closest_game()
        if game:
            await admin_handler.send_game_info_to_general_chat(context, game, _)
            await query.answer(_('Game info sent to general chat.'))
        else:
            await query.answer(_('No upcoming games found.'), show_alert=True)

    elif data.startswith('register_'):
        try:
            game_id = int(data.split('_')[1])
            game = await db_manager.get_game_by_id(game_id)
            if game:
                await db_manager.register_user_for_game(user, game)
                await query.answer(_('You have been registered for the game.'))
                # Обновляем информацию об игре для пользователя
                await user_handler.handle_user_game_interaction(update, context, _, user, game, query=query)
            else:
                await query.answer(_('Game not found.'), show_alert=True)
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            await query.answer(_('Error during registration.'), show_alert=True)

    elif data.startswith('unregister_'):
        try:
            game_id = int(data.split('_')[1])
            game = await db_manager.get_game_by_id(game_id)
            if game:
                await db_manager.unregister_user_from_game(user, game)
                await query.answer(_('You have been unregistered from the game.'))
                # Обновляем информацию об игре для пользователя
                await user_handler.handle_user_game_interaction(update, context, _, user, game, query=query)
            else:
                await query.answer(_('Game not found.'), show_alert=True)
        except Exception as e:
            logging.error(f"Error during unregistration: {e}")
            await query.answer(_('Error during unregistration.'), show_alert=True)



    elif query.data.startswith('announce_'):
        game_id = int(query.data.split('_')[1])
        game = await db_manager.get_game_by_id(game_id)
        await admin_handler.send_announcement(update, context, game, _, query)
        await query.answer()


    elif data == 'confirm_payment':
        # Handle payment confirmation logic here
        await query.answer(_('Payment confirmed.'), show_alert=True)
        # You may want to update the user's subscription status in the database

    elif data == 'close_message':
        await query.delete_message()
        await query.answer()

    else:
        # Handle unknown callback data
        await query.answer(_('Unknown command.'), show_alert=True)


async def message_handler(update: Update, context: CallbackContext):
    """Handler for incoming text messages."""
    user_id = update.effective_chat.id
    user = await db_manager.get_user_by_telegram_id(user_id)
    lang_code = user.language or 'en'
    _ = get_gettext(lang_code)

    # Check if the user is an admin and awaiting a broadcast message
    if context.user_data.get('awaiting_broadcast_message') and user.is_admin:
        await admin_handler.broadcast_message_handler(update, context, _)
    else:
        # Handle other text messages (you can customize this part)
        await update.message.reply_text(_('Sorry, I did not understand that command.'))



async def request_phone_number(update: Update, context: CallbackContext, _):
    button = KeyboardButton(_('Share your phone number'), request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_('Please share your phone number so we can register you.'),
        reply_markup=reply_markup
    )
