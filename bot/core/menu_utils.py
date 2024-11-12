from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def get_language_keyboard():
    keyboard = [
        [InlineKeyboardButton('Беларуская', callback_data='lang_be')],
        [InlineKeyboardButton('Українська', callback_data='lang_uk')],
        [InlineKeyboardButton('Polski', callback_data='lang_pl')],
        [InlineKeyboardButton('English', callback_data='lang_en')],
        [InlineKeyboardButton('Русский', callback_data='lang_ru')],
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_language_selection(update, context: CallbackContext, _, query=None) -> None:
    """
    Отображает меню для выбора языка. Если передан query, редактирует существующее сообщение.
    """
    reply_markup = get_language_keyboard()

    if query:
        await query.edit_message_text(text=_('Please choose your preferred language:'), reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_('Please choose your preferred language:'),
            reply_markup=reply_markup
        )
