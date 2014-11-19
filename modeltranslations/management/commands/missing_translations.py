from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from modeltranslations.utils import normalize_language_code, \
    get_normalized_language_codes


class Command(BaseCommand):
    help = 'Finds all untranslated strings of a certain language'

    def handle(self, *args, **options):
        reference_language = normalize_language_code(settings.LANGUAGE_CODE)
        for model in apps.get_models():
            for field in model._meta.fields:
                if field.get_internal_type() == 'TranslationForeignKey':
                    Target = field.rel.to
                    for instance in Target.translated_objects.all_languages().all():
                        for field in model.get_translation_field_names():
                            reference_value = getattr(instance, field+'_'+reference_language)
                            for language in get_normalized_language_codes():
                                if language == reference_language:
                                    continue
                                if reference_value and not getattr(instance, field+'_'+language):
                                    print u'#: %s.%s.%s' % (Target._meta.object_name, instance.pk, language)
                                    print u'msgid "%s"' % reference_value
                                    print u'msgstr ""'
