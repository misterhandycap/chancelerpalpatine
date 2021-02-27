import os

from dotenv import load_dotenv

load_dotenv()

import gettext

_ = lambda s: s

def change_language(language_code):
    language_translation = gettext.translation(
        'base',
        localedir=os.path.join('bot', 'i18n'),
        languages=[language_code]
    )
    language_translation.install()
    return language_translation
