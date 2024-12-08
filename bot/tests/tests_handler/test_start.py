import pytest
from unittest.mock import MagicMock
from asgiref.sync import sync_to_async
from telegram import Update, User, Chat, Message, Bot
from telegram.ext import CallbackContext
from bot.handlers.common_handlers import start_handler
from bot.tests.test_utils.test_factories import generate_random_user_data
from laser_tag_admin.users.models import User as DBUser


@pytest.mark.asyncio
@pytest.mark.django_db
async def test_start_handler():
    data_user = generate_random_user_data()
    user = User(
        id=data_user['telegram_id'],
        first_name=data_user['first_name'],
        last_name=data_user['last_name'],
        username=data_user['username'],
        is_bot=False
    )
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

    # Дополнительная проверка: пользователь с данным telegram_id существует в БД
    user_count = await sync_to_async(DBUser.objects.filter(telegram_id=data_user['telegram_id']).count)()
    assert user_count == 1, f"Пользователь с telegram_id={data_user['telegram_id']} не был создан в базе данных."
