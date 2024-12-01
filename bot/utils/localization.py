# bot/utils/localization.py

import gettext
import os

# Путь к файлам локализации
LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'locale')

LANGUAGES = {
    'en': 'English',
    'ru': 'Русский',
    'be': 'Беларуская',
    'uk': 'Українська',
    'pl': 'Polski',
}

# Словарь для хранения gettext переводчиков для каждого языка
langs = {}

# Инициализируем переводчики для каждого языка
for lang_code in LANGUAGES:
    try:
        translation = gettext.translation(
            'messages',
            localedir=LOCALE_DIR,
            languages=[lang_code]
        )
    except FileNotFoundError:
        # Если файлы перевода не найдены, используем NullTranslations
        translation = gettext.NullTranslations()
    langs[lang_code] = translation

def get_gettext(lang_code):
    """Возвращает функцию gettext для заданного языка."""
    return langs.get(lang_code, langs['en']).gettext
