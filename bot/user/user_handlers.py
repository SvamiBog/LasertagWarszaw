import logging
import os
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram import Update

from bot.core.database_manager import DatabaseManager

from asgiref.sync import sync_to_async  # Не забудьте импортировать sync_to_async

class UserHandler:
    """Класс для обработки действий пользователя."""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.general_chat_url = os.getenv('GENERAL_CHAT_URL', 'https://t.me/lasertawarsaw')
        self.payment_details = os.getenv('PAYMENT_DETAILS')
        logging.basicConfig(level=logging.INFO)


    async def send_user_menu(self, update: Update, context: CallbackContext, _, query=None) -> None:
        """Отправляет меню пользователя."""
        keyboard = [
            [InlineKeyboardButton(_('Open Game'), callback_data='open_game')],
            [InlineKeyboardButton(_('Club Card'), callback_data='club_card')],
            [InlineKeyboardButton(_('General Chat'), url=self.general_chat_url)],
            [InlineKeyboardButton(_('Settings'), callback_data='settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        menu_text = _('User Menu:')

        if query:
            current_text = query.message.text
            if current_text != menu_text:
                await query.edit_message_text(text=menu_text, reply_markup=reply_markup)
            else:
                logging.info(_("Message not changed, skipping edit."))
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=menu_text,
                reply_markup=reply_markup
            )


    async def send_user_settings_menu(self, update: Update, context: CallbackContext, _, query=None) -> None:
        """Отправляет меню настроек для пользователя."""
        logging.info("Функция send_user_settings_menu вызвана.")

        keyboard = [
            [InlineKeyboardButton(_('Subscription Status'), callback_data='subscription_status')],
            [InlineKeyboardButton(_('Change Language'), callback_data='change_language')],
            [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.edit_message_text(text=_('User Settings menu:'), reply_markup=reply_markup)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_('User Settings menu:'),
                reply_markup=reply_markup
            )


    async def show_subscription_status(self, update: Update, context: CallbackContext, _, query) -> None:
        """Отображает статус подписки пользователя с возможностью переключения."""
        user_id = update.effective_chat.id
        user = await self.db_manager.get_user_by_telegram_id(user_id)
        subscription_status = _('Enabled') if user.notifications_enabled else _('Disabled')

        status_message = f"{_('Subscription status')}: {subscription_status}"

        keyboard = [
            [InlineKeyboardButton(_('Toggle Subscription'), callback_data='toggle_subscription')],
            [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.message.text != status_message:
            await query.edit_message_text(text=status_message, reply_markup=reply_markup)
        else:
            await query.answer(_('No changes were made to the message.'))


    async def toggle_subscription(self, update: Update, context: CallbackContext, _) -> None:
        """Переключает статус подписки пользователя и отображает обновленный статус."""
        user_id = update.effective_chat.id
        user = await self.db_manager.get_user_by_telegram_id(user_id)

        user.notifications_enabled = not user.notifications_enabled
        await self.db_manager.save_user(user)

        subscription_status = _('Enabled') if user.notifications_enabled else _('Disabled')
        status_message = f"{_('Subscription status')}: {subscription_status}"

        keyboard = [
            [InlineKeyboardButton(_('Toggle Subscription'), callback_data='toggle_subscription')],
            [InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query = update.callback_query
        await query.edit_message_text(text=status_message, reply_markup=reply_markup)
        await query.answer(_('Subscription status updated.'))


    async def handle_user_game_interaction(self, update: Update, context: CallbackContext, _, user, game, query=None) -> None:
        """Обрабатывает взаимодействие с игрой для пользователя."""
        if query is None:
            query = update.callback_query

        if not game:
            message = _('No upcoming games found.')
            keyboard = []
            if update.effective_chat.type == 'private':
                keyboard.append([InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')])
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
            [InlineKeyboardButton(_('Register for Game'), callback_data=f'register_{game.id}')],
            [InlineKeyboardButton(_('Unregister from Game'), callback_data=f'unregister_{game.id}')]
        ]

        if update.effective_chat.type == 'private':
            keyboard.append([InlineKeyboardButton(_('Main Menu'), callback_data='main_menu')])

        reply_markup = InlineKeyboardMarkup(keyboard)

        if query.message.text != message or query.message.reply_markup != reply_markup:
            await query.edit_message_text(text=message, reply_markup=reply_markup)
        else:
            await query.answer(_('Message is not modified.'))

        await query.answer()


    async def show_user_game_registrations(self, update: Update, context: CallbackContext, user, _) -> None:
        """Отображает список игр, на которые пользователь записан."""
        registrations = await self.db_manager.get_user_registrations(user)

        if registrations:
            keyboard = []
            for reg in registrations:
                game = await sync_to_async(lambda: reg.game)()
                button_text = f"{game.date.strftime('%d.%m.%Y')} {game.start_time.strftime('%H:%M')}"
                callback_data = f"game_info_{game.id}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])

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


    async def handle_user_club_card(self, update: Update, context: CallbackContext, _, user, query=None) -> None:
        """Обрабатывает отображение данных для оплаты и проверку статуса клубной карты."""
        current_date = datetime.now().date()

        if user.subscription_end_date and user.subscription_end_date >= current_date:
            subscription_status = _('Your club card is active until {date}.').format(
                date=user.subscription_end_date.strftime('%d.%m.%Y')
            )
        else:
            subscription_status = _('Your club card is not active.')

        payment_message = f"{subscription_status}\n\n"
        payment_message += _('To activate or extend your club card, make a payment.\n')
        payment_message += f"{_('Payment details')}: {self.payment_details}\n"
        payment_message += f"{_('Payment comment')}: {user.telegram_id}"

        keyboard = [
            [InlineKeyboardButton(_('Confirm Payment'), callback_data='confirm_payment')],
            [InlineKeyboardButton(_('Menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if query:
            await query.edit_message_text(text=payment_message, reply_markup=reply_markup)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=payment_message,
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
