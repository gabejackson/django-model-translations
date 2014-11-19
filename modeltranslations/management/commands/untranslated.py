from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand
from modeltranslations.utils import normalize_language_code, \
    get_normalized_language_codes


class Command(BaseCommand):
    help = 'Finds all untranslated models'

    def handle(self, *args, **options):
        reference_language = normalize_language_code(settings.LANGUAGE_CODE)
        for model in apps.get_models():
            for field in model._meta.fields:
                if field.get_internal_type() == 'TranslationForeignKey':
                    Target = field.rel.to
                    for instance in Target.translated_objects.all_languages().all():
                        if not instance._num_translation_objects:
                            print u'#: %s.%s' % (Target._meta.object_name, instance.pk)
                            continue
                        tracker = 0
                        for field in model.get_translation_field_names():
                            for language in get_normalized_language_codes():
                                if getattr(instance, field+'_'+language):
                                    tracker += 1
                        if not tracker:
                            print u'#: %s.%s' % (Target._meta.object_name, instance.pk)