import pytest
from unittest.mock import AsyncMock
from asgiref.sync import sync_to_async
from telegram import Update, User, Chat, Message, CallbackQuery, Bot
from telegram.ext import CallbackContext
from bot.handlers.common_handlers import button_handler
from laser_tag_admin.users.models import User as DBUser
from bot.tests.test_utils.test_factories import generate_random_user_data

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("callback_data,expected_method_call,expected_text_substring", [
    ("change_language", "edit_message_text", "Choose your language"),
    ("main_menu", "edit_message_text", "User Menu:"),
    ("subscription_status", "edit_message_text", "Subscription status"),
    ("toggle_subscription", "edit_message_text", "Subscription status: Disabled"),
    ("settings", "edit_message_text", "User Settings menu:")
])
async def test_button_handler_basic_buttons(callback_data, expected_method_call, expected_text_substring, db):
    data_user = generate_random_user_data()

    await sync_to_async(DBUser.objects.create)(
        telegram_id=data_user['telegram_id'],
        language=data_user['language'],
        first_name=data_user['first_name'],
        last_name=data_user['last_name'],
        username=data_user['username'],
        phone_number=data_user['phone_number']
    )

    user = User(
        id=data_user['telegram_id'],
        first_name=data_user['first_name'],
        last_name=data_user['last_name'],
        username=data_user['username'],
        is_bot=False
    )

    chat = Chat(id=data_user['telegram_id'], type="private")
    message = Message(message_id=10, date=None, chat=chat, text="Previous text", from_user=user)
    callback_query = CallbackQuery(
        id="query_id",
        from_user=user,
        message=message,
        data=callback_data,
        chat_instance="some_chat_instance"
    )
    update = Update(update_id=2, callback_query=callback_query)

    context = AsyncMock(spec=CallbackContext)
    context.bot = AsyncMock(spec=Bot)

    # Привязываем bot к message и callback_query
    message.set_bot(context.bot)
    callback_query.set_bot(context.bot)

    context.bot.edit_message_text = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.bot.answer_callback_query = AsyncMock()  # Если query.answer() вызывается, это пригодится

    await button_handler(update, context)

    if expected_method_call == "edit_message_text":
        context.bot.edit_message_text.assert_called_once()
        args, kwargs = context.bot.edit_message_text.call_args
        assert expected_text_substring in kwargs["text"]
    else:
        context.bot.send_message.assert_called_once()
        args, kwargs = context.bot.send_message.call_args
        assert expected_text_substring in kwargs["text"]
