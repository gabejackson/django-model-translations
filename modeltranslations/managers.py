# encoding: utf-8
from django.db import models
from django.db.models import Q, Count
from django.utils.translation import get_language
from modeltranslations.expressions import ConditionalJoin
from modeltranslations.utils import normalize_language_code, get_languages


class TranslationManager(models.Manager):
    lang = None
    fallback_lang = None
    all_langs = False

    def get_queryset(self):
        qs = super(TranslationManager, self).get_queryset()

        # First get all fields on the translation model
        target_fields = self.translation_model.get_translation_field_names()
        target_related_name = self.translation_model._meta.model_name

        # Create annotations of all fields
        if self.all_langs:
            for language in get_languages():
                lang_q_args = {'%s__lang' % target_related_name: language}
                for field in target_fields:
                    annotation = {}
                    annotation[field+'_'+normalize_language_code(language)] = ConditionalJoin(
                        '%s__%s' % (target_related_name, field),
                        conditions=Q(**lang_q_args)
                    )
                    qs = qs.annotate(**annotation)
            # Used to easily find which instances do not have any translation objects
            qs = qs.annotate(_num_translation_objects=Count(target_related_name))
        else:
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
        self.all_langs = False

        return qs

    def language(self, lang):
        if lang in get_languages():
            self.lang = lang
        else:
            raise Exception("Language `%s` is not in LANGUAGES. Available languages are %s" % (lang, get_languages()))
        return self

    def all_languages(self):
        self.all_langs = True
        return self

    def fallback(self, lang):
        if lang in get_languages():
            self.fallback_lang = lang
        else:
            raise Exception("Language `%s` is not in LANGUAGES. Available languages are %s" % (lang, get_languages()))
        return self

    def _get_query_language(self):
        if self.lang:
            return self.lang
        return get_language()