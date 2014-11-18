from django.utils.translation import get_language


def get_translation(instance, language_code=None):
    opts = instance._meta
    if not language_code:
        language_code = get_language()
    accessor = getattr(instance, opts.translations_accessor)
    return accessor.get(language_code=language_code)