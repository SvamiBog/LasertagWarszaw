import pytest
from unittest.mock import AsyncMock
from asgiref.sync import sync_to_async
from telegram import Update, User, Chat, Message, CallbackQuery, Bot
from telegram.ext import CallbackContext
from bot.handlers.common_handlers import button_handler
from laser_tag_admin.users.models import User as DBUser

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("callback_data,expected_method_call,expected_text_substring", [
    ("change_language", "edit_message_text", "Choose your language"),
    ("main_menu", "edit_message_text", "User Menu:"),
    ("subscription_status", "edit_message_text", "Subscription status"),
    ("toggle_subscription", "edit_message_text", "Subscription status: Disabled")
])
async def test_button_handler_basic_buttons(callback_data, expected_method_call, expected_text_substring, db):
    # Чистим базу перед каждым тестом
    await sync_to_async(DBUser.objects.all().delete)()

    # Создаем тестового пользователя в БД
    await sync_to_async(DBUser.objects.create)(
        telegram_id=123,
        language='en',
        first_name='TestUserDB'
    )

    user = User(id=123, first_name="TestUser", is_bot=False)
    chat = Chat(id=123, type="private")
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