import logging
import os

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext
from telegram import Update

from bot.utils.localization import get_gettext
from bot.core.database_manager import DatabaseManager

from asgiref.sync import sync_to_async


# Настройка логирования
logging.basicConfig(level=logging.INFO)

class AdminHandler:
    """Класс для обработки действий администратора."""


    def __init__(self):
        self.db_manager = DatabaseManager()
        self.general_chat_id = os.getenv('GENERAL_CHAT_ID')


    async def send_admin_menu(self, update: Update, context: CallbackContext, _, query=None) -> None:
        """Отправляет меню администратора."""
        keyboard = [
            [InlineKeyboardButton(_('Open Game'), callback_data='open_game')],
            [InlineKeyboardButton(_('Broadcast Message'), callback_data='broadcast_message')],
            [InlineKeyboardButton(_('Send Game Info to General Chat'), callback_data='send_game_info_general_chat')],
            [InlineKeyboardButton(_('Club Card'), callback_data='club_card')],
            [InlineKeyboardButton(_('Settings'), callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            try:
                await query.edit_message_text(text=_('Admin Menu:'), reply_markup=reply_markup)
            except Exception as e:
                logging.error(f"Error editing admin menu: {e}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=_('Admin Menu:'),
                    reply_markup=reply_markup
                )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_('Admin Menu:'),
                reply_markup=reply_markup
            )


    async def send_admin_settings_menu(self, update: Update, context: CallbackContext, _, query) -> None:
        """Отправляет меню настроек администратора."""
        keyboard = [
            [InlineKeyboardButton(_('Change Language'), callback_data='change_language')],
            [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=_('Admin Settings Menu:'), reply_markup=reply_markup)


    async def send_announcement(self, update: Update, context: CallbackContext, game, _, query=None) -> None:
        """Отправляет рассылку пользователям, которые подписаны на уведомления."""
        users = await self.db_manager.get_users_for_announcement()
        success_count = 0
        fail_count = 0
        registrations = await self.db_manager.get_game_registrations(game)

        for user in users:
            user_lang_code = user.language
            _ = get_gettext(user_lang_code)

            message = await self._format_game_details(game, registrations, _)

            keyboard = [
                [InlineKeyboardButton(_('Register for Game'), callback_data=f'register_{game.id}')],
                [InlineKeyboardButton(_('Unregister from Game'), callback_data=f'unregister_{game.id}')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                await context.bot.send_message(chat_id=user.telegram_id, text=message, reply_markup=reply_markup)
                success_count += 1
            except Exception as e:
                logging.warning(f"Не удалось отправить сообщение пользователю {user.telegram_id}: {e}")
                fail_count += 1

        # Для администратора используем общий язык или язык администратора
        admin_lang_code = update.effective_user.language_code or 'en'
        _ = get_gettext(admin_lang_code)

        response_message = _('Announcement sent to subscribed users.\n')
        response_message += f"{_('Success')}: {success_count}\n"
        response_message += f"{_('Failed')}: {fail_count}\n"

        admin_keyboard = [
            [InlineKeyboardButton(_('View Game Details'), callback_data=f'game_info_{game.id}')],
            [InlineKeyboardButton(_('Close'), callback_data='close_message')]
        ]
        admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)

        if query:
            await query.edit_message_text(text=response_message, reply_markup=admin_reply_markup)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=response_message,
                reply_markup=admin_reply_markup
            )

        await self.send_admin_menu(update, context, _)


    async def handle_admin_game_interaction(self, update: Update, context: CallbackContext, _, user, game=None, query=None) -> None:
        """Обрабатывает взаимодействие администратора с игрой."""
        if query is None:
            query = update.callback_query

        if game is None:
            game = await self.db_manager.get_closest_game()

        if not game:
            message = _('No upcoming games found.')
            keyboard = [[InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            if query:
                await query.edit_message_text(text=message, reply_markup=reply_markup)
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    reply_markup=reply_markup
                )
            await query.answer()
            return

        registrations = await self.db_manager.get_game_registrations(game)
        message = await self._format_game_details(game, registrations, _)

        keyboard = [
            [InlineKeyboardButton(_('Send Announcement'), callback_data=f'announce_{game.id}')],
            [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.edit_message_text(text=message, reply_markup=reply_markup)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup
            )

        await query.answer()


    async def broadcast_message_handler(self, update: Update, context: CallbackContext, _) -> None:
        """Обрабатывает ввод сообщения от администратора для рассылки."""
        if context.user_data.get('awaiting_broadcast_message'):
            broadcast_message = update.message.text
            context.user_data['awaiting_broadcast_message'] = False

            users = await self.db_manager.get_users_for_broadcast()

            for recipient in users:
                try:
                    await context.bot.send_message(chat_id=recipient.telegram_id, text=broadcast_message)
                except Exception as e:
                    logging.warning(f"Не удалось отправить сообщение пользователю {recipient.telegram_id}: {e}")

            await update.message.reply_text(_('Broadcast sent successfully to all users.'))
            await self.send_admin_menu(update, context, _)

    async def send_game_info_to_general_chat(self, context: CallbackContext, game, _) -> None:
        """Отправляет информацию об игре в общий чат."""
        registrations = await self.db_manager.get_game_registrations(game)
        message = await self._format_game_details(game, registrations, _)

        keyboard = [
            [InlineKeyboardButton(_('Register for Game'), callback_data=f'register_{game.id}')],
            [InlineKeyboardButton(_('Unregister from Game'), callback_data=f'unregister_{game.id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if self.general_chat_id:
            await context.bot.send_message(chat_id=self.general_chat_id, text=message, reply_markup=reply_markup)
        else:
            logging.error('GENERAL_CHAT_ID is not set in the environment variables.')

    async def handle_admin_club_card(self, update: Update, context: CallbackContext, _, query) -> None:
        """Обрабатывает запрос информации о клубных картах."""
        active_users = await self.db_manager.get_active_subscriptions()
        active_users_exist = await sync_to_async(active_users.exists)()

        if active_users_exist:
            message = _('Active club card users:\n')
            for user in await sync_to_async(list)(active_users):
                message += f"{user.first_name} {user.last_name} - {user.subscription_end_date.strftime('%d.%m.%Y')}\n"
        else:
            message = _('No active club card users.')

        keyboard = [[InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.edit_message_text(text=message, reply_markup=reply_markup)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup
            )


    async def _format_game_details(self, game, registrations, _) -> str:
        """Форматирует детали игры для отправки пользователям."""
        message = _('Game Details:\n')
        message += f"{_('Date')}: {game.date.strftime('%d.%m.%Y')}\n"
        message += f"{_('Start Time')}: {game.start_time.strftime('%H:%M')}\n"
        message += f"{_('Location')}: {game.location}\n"
        total_players = await self.db_manager.get_total_players_count_for_game(game)
        message += _('Players count: ') + str(total_players) + '\n'
        message += f"\n{_('Participants List')}:\n"

        if registrations:
            for reg in registrations:
                reg_user = await sync_to_async(lambda: reg.user)()
                message += f"- {reg_user.first_name} {reg_user.last_name} (Guests: {reg.guests_count})\n"
        else:
            message += _('No participants yet.')

        return message
