from telegram import Update
from telegram.ext import CallbackContext

def view_players(update: Update, context: CallbackContext) -> None:
    """Обработчик для просмотра списка игроков на игру"""
    # Логика для просмотра игроков
    update.message.reply_text("Список игроков на игру:")
    # Подгружаем информацию об игре и отправляем её
