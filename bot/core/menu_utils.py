from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_language_keyboard():
    keyboard = [
        [InlineKeyboardButton('Беларуская', callback_data='lang_be')],
        [InlineKeyboardButton('Українська', callback_data='lang_uk')],
        [InlineKeyboardButton('Polski', callback_data='lang_pl')],
        [InlineKeyboardButton('English', callback_data='lang_en')],
        [InlineKeyboardButton('Русский', callback_data='lang_ru')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def show_language_selection(update, context, _):
    reply_markup = get_language_keyboard()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_('Please choose your preferred language:'),
        reply_markup=reply_markup
    )
