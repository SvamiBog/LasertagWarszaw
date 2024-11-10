import gettext

langs = {
    'be': gettext.translation('messages', localedir='locale', languages=['be']),
    'uk': gettext.translation('messages', localedir='locale', languages=['uk']),
    'pl': gettext.translation('messages', localedir='locale', languages=['pl']),
    'en': gettext.translation('messages', localedir='locale', languages=['en']),
    'ru': gettext.translation('messages', localedir='locale', languages=['ru'])
}

user_lang = {}

def get_translation(user_id):
    lang_code = user_lang.get(user_id, 'en')
    return langs.get(lang_code).gettext if lang_code in langs else langs['en'].gettext
