# encoding: utf-8
from django.db import models
from django.db.models import Count
from django.utils.translation import get_language
from modeltranslations.expressions import LanguageJoin
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

        if self.all_langs:
            # Annotate all language entries
            for language in get_languages():
                for field in target_fields:
                    annotation = {
                        field+'_'+normalize_language_code(language): LanguageJoin(target_related_name, field, language)
                    }
                    qs = qs.annotate(**annotation)
            # Used to easily find which instances do not have any translation objects
            qs = qs.annotate(_num_translation_objects=Count(target_related_name))
        else:
            # Annotate desired language entries
            for field in target_fields:
                annotation = {
                    field: LanguageJoin(target_related_name, field, self._get_query_language())
                }
                qs = qs.annotate(**annotation)

            if self.fallback_lang:
                # Annotate additional fallback language entries
                for field in target_fields:
                    annotation = {
                        field+'_fallback': LanguageJoin(target_related_name, field, self.fallback_lang)
                    }
                    qs = qs.annotate(**annotation)

        # Reset attributes to avoid later queries reusing them
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