import pytest
from unittest.mock import MagicMock
from telegram import Update, User, Chat, Message, Bot
from telegram.ext import CallbackContext
from bot.handlers.common_handlers import start_handler


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_start_handler():
    user = User(id=123, first_name="TestUser", is_bot=False)
    chat = Chat(id=123, type="private")
    message = Message(message_id=1, date=None, chat=chat, text="/start", from_user=user)
    update = Update(update_id=1, message=message)

    context = MagicMock(spec=CallbackContext)
    # Создаём mock bot с интерфейсом Bot
    context.bot = MagicMock(spec=Bot)

    # Назначаем бота сообщению
    message.set_bot(context.bot)

    await start_handler(update, context)

    context.bot.send_message.assert_called_once()
    args, kwargs = context.bot.send_message.call_args
    assert kwargs["chat_id"] == chat.id
    assert "Choose your language" in kwargs["text"]