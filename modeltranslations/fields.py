from django.conf import settings
from django.db.models import ForeignKey, CharField
from django.db.models.fields.related import add_lazy_relation
from django.utils.translation import get_language
from modeltranslations.managers import TranslationManager


class TranslationDescriptor(object):
    def __init__(self, name):
        self.name = name
        self.hidden_name = '_'+name

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        if getattr(instance, self.hidden_name):
            return getattr(instance, self.hidden_name)
        if hasattr(instance, self.name+"_fallback"):
            return getattr(instance, self.name+"_fallback")
        return ''

    def __set__(self, instance, value):
        setattr(instance, self.hidden_name, value)


class TranslationForeignKey(ForeignKey):
    def contribute_to_class(self, cls, name, virtual_only=False):
        if not filter(lambda field: field.name == 'lang', cls._meta.fields):
            cls.add_to_class('lang', CharField(max_length=20, db_index=True, name='lang', default=get_language, choices=settings.LANGUAGES))
        cls.translation_foreign_key_name = name

        # This methods allows getting the cached translation field names from both cls and instance
        def get_translation_field_names(cls):
            if not cls._translation_fields:
                for field in cls._meta.fields:
                    if field.name in ('id', 'lang'):
                        continue
                    if field.name == cls.translation_foreign_key_name:
                        continue
                    cls._translation_fields.append(field.name)
            return cls._translation_fields

        setattr(cls, '_translation_fields', [])
        setattr(cls, get_translation_field_names.__name__, classmethod(get_translation_field_names))

        super(TranslationForeignKey, self).contribute_to_class(cls, name)

    def contribute_to_related_class(self, cls, related):
        self.model._meta.unique_together = ((self.name, 'lang',),)

        def add_translation_descriptors(field, model, cls):
            for f in related.model.get_translation_field_names():
                setattr(cls, f, TranslationDescriptor(f))

        add_lazy_relation(cls, None, self.model, add_translation_descriptors)

        # Add translation manager which deals with automatic annotation of translated fields
        manager = TranslationManager()
        manager.translation_model = self.model

        cls.add_to_class('translated_objects', manager)

        super(TranslationForeignKey, self).contribute_to_related_class(cls, related)
