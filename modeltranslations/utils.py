from django.conf import settings
from django.utils.translation import get_language


def get_translation(instance, language_code=None):
    opts = instance._meta
    if not language_code:
        language_code = get_language()
    accessor = getattr(instance, opts.translations_accessor)
    return accessor.get(language_code=language_code)

def normalize_language_code(language_code):
    return language_code.replace('-', '_')

def get_languages():
    return dict(settings.LANGUAGES).keys()

def get_normalized_language_codes():
    langs = []
    for lang in get_languages():
        langs.append(lang.replace('-', '_'))
    return langs