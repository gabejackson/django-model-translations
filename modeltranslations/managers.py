# encoding: utf-8
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import get_language
from modeltranslations.expressions import ConditionalJoin


class TranslationManager(models.Manager):
    lang = None
    fallback_lang = None

    def get_queryset(self):
        qs = super(TranslationManager, self).get_queryset()

        # First get all fields on the translation model
        target_fields = []
        for field in self.translation_model._meta.fields:
            if field.name in ('id', 'lang'):
                continue
            if field.name == self.translation_model.translation_foreign_key_name:
                continue
            target_fields.append(field.name)

        # Create annotations of all fields
        target_related_name = self.translation_model._meta.model_name
        lang_q_args = {'%s__lang' % target_related_name: self._get_query_language()}
        for field in target_fields:
            annotation = {}
            annotation[field] = ConditionalJoin(
                '%s__%s' % (target_related_name, field),
                conditions=Q(**lang_q_args)
            )
            qs = qs.annotate(**annotation)

        if self.fallback_lang:
            lang_q_args = {'%s__lang' % target_related_name: self.fallback_lang}
            for field in target_fields:
                annotation = {}
                annotation[field+'_fallback'] = ConditionalJoin(
                    '%s__%s' % (target_related_name, field),
                    conditions=Q(**lang_q_args)
                )
                qs = qs.annotate(**annotation)

        # Reset language and fallback to avoid later queries using these
        self.lang = None
        self.fallback_lang = None

        return qs

    def language(self, lang):
        if lang in dict(settings.LANGUAGES).keys():
            self.lang = lang
        else:
            raise Exception("Language `%s` is not in LANGUAGES. Available languages are %s" % (lang, dict(settings.LANGUAGES).keys()))
        return self

    def fallback(self, lang):
        if lang in dict(settings.LANGUAGES).keys():
            self.fallback_lang = lang
        else:
            raise Exception("Language `%s` is not in LANGUAGES. Available languages are %s" % (lang, dict(settings.LANGUAGES).keys()))
        return self

    def _get_query_language(self):
        if self.lang:
            return self.lang
        return get_language()