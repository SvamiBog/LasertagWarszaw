# bot/keyboards/common_keyboards.py

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.localization import LANGUAGES

def get_language_keyboard():
    """Генерирует инлайн-клавиатуру для выбора языка."""
    buttons = [
        [InlineKeyboardButton(LANGUAGES[lang_code], callback_data=f'lang_{lang_code}')]
        for lang_code in LANGUAGES
    ]
    return InlineKeyboardMarkup(buttons)
