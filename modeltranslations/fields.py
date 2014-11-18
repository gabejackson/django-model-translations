from django.conf import settings
from django.db.models import ForeignKey, CharField
from django.db.models.fields.related import add_lazy_relation
from django.utils.translation import get_language
from modeltranslations.managers import TranslationManager


class TranslationDescriptor(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        translation = getattr(instance, 'active_translation')
        rel_obj = getattr(translation, self.name)
        if rel_obj is None:
            raise Exception('no have dis')
        else:
            return rel_obj


class TranslationForeignKey(ForeignKey):
    def contribute_to_class(self, cls, name, virtual_only=False):
        if not filter(lambda field: field.name == 'lang', cls._meta.fields):
            cls.add_to_class('lang', CharField(max_length=20, db_index=True, name='lang', default=get_language, choices=settings.LANGUAGES))
        cls.translation_foreign_key_name = name
        super(TranslationForeignKey, self).contribute_to_class(cls, name)

    def contribute_to_related_class(self, cls, related):
        self.model._meta.unique_together = ((self.name, 'lang',),)

        def add_translation_descriptors(field, model, cls):
            for f in model._meta.fields:
                # FIXME: Filter out id, fk and such
                setattr(cls, f.name, TranslationDescriptor(f.name))

        add_lazy_relation(cls, None, self.model, add_translation_descriptors)

        # Add translation manager which deals with automatic annotation of translated fields
        manager = TranslationManager()
        manager.translation_model = self.model

        cls.add_to_class('translated_objects', manager)

        super(TranslationForeignKey, self).contribute_to_related_class(cls, related)
