import gettext
import os

def i18n(text, language_code):
    language_translation = gettext.translation(
        'base',
        localedir=os.path.join('bot', 'i18n'),
        languages=[language_code]
    )
    return language_translation.gettext(text)
