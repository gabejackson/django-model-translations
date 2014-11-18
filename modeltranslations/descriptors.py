from django.apps import registry
from django.db.models import FieldDoesNotExist
from django.utils.translation import get_language
from modeltranslations.utils import get_translation


class BaseDescriptor(object):
    """
    Base descriptor class with a helper to get the translations instance.
    """
    def __init__(self, opts):
        self.opts = opts

    def translation(self, instance):
        cached = getattr(instance, self.opts.translations_cache, None)
        if cached is None:
            try:
                cached = get_translation(instance)
            except self.opts.translations_model.DoesNotExist:
                raise Exception('Accessing a translated field requires that '
                                'the instance has a translation loaded, or a '
                                'valid translation in current language (%s) '
                                'loadable from the database' % get_language())
            setattr(instance, self.opts.translations_cache, cached)
        return cached


class TranslatedAttribute(BaseDescriptor):
    """
    Basic translated attribute descriptor.
    
    Proxies attributes from the shared instance to the translated instance.
    """
    def __init__(self, opts, name):
        self.name = name
        super(TranslatedAttribute, self).__init__(opts)
        
    def __get__(self, instance, instance_type=None):
        if not instance:
            if registry.apps.ready:
                raise AttributeError('Attribute not available until registry is ready.')
            try:
                return self.opts.translations_model._meta.get_field_by_name(
                                                        self.name)[0].default
            except FieldDoesNotExist as e:
                raise AttributeError(*e.args)
        return getattr(self.translation(instance), self.name)
    
    def __set__(self, instance, value):
        setattr(self.translation(instance), self.name, value)
    
    def __delete__(self, instance):
        delattr(self.translation(instance), self.name)