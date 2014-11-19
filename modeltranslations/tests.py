from operator import attrgetter
from django.db.models import Q
from django.test import TestCase
from django.utils.translation import activate
from modeltranslations.models import Article, ArticleTranslation


class TranslationAnnotationTest(TestCase):
    def setUp(self):
        self.a1 = Article.objects.create()
        self.at1_de = ArticleTranslation(
            article=self.a1,
            lang='de-ch',
            title='Das ist ein Titel',
            body='Heute wurde publiziert, dass es einen neuen Titel gibt'
        )
        self.at1_de.save()
        self.at1_en = ArticleTranslation(
            article=self.a1,
            lang='en-us',
            title='This is a title',
            body='')
        self.at1_en.save()

        self.a2 = Article.objects.create()
        self.at1_de = ArticleTranslation(
            article=self.a2,
            lang='de-ch',
            title='Django ist da',
            body='Die neue Django Version ist da!'
        )
        self.at1_de.save()
        self.at1_en = ArticleTranslation(
            article=self.a2,
            lang='en-us',
            title='Django is here',
            body='The new Django version is here!')
        self.at1_en.save()

    def test_translations(self):
        activate('en-us')
        qs = Article.translated_objects.all().order_by('pk')

        self.assertQuerysetEqual(
            qs, [
                'This is a title',
                'Django is here',
            ],
            attrgetter('title')
        )

        self.assertQuerysetEqual(
            qs, [
                '',
                'The new Django version is here!',
            ],
            attrgetter('body')
        )

    def test_language_override(self):
        activate('en-us')
        qs = Article.translated_objects.language('de-ch').all().order_by('pk')

        self.assertQuerysetEqual(
            qs, [
                'Das ist ein Titel',
                'Django ist da',
            ],
            attrgetter('title')
        )

    def test_explicit_fallbacks(self):
        activate('en-us')
        qs = Article.translated_objects.fallback('de-ch').order_by('pk')

        self.assertQuerysetEqual(
            qs, [
                'This is a title',
                'Django is here',
            ],
            attrgetter('title')
        )

        self.assertQuerysetEqual(
            qs, [
                'Heute wurde publiziert, dass es einen neuen Titel gibt',
                'The new Django version is here!',
            ],
            attrgetter('body')
        )

        self.assertQuerysetEqual(
            qs, [
                'Das ist ein Titel',
                'Django ist da',
            ],
            attrgetter('title_fallback')
        )

    def test_implicit_fallbacks(self):
        activate('en-us')
        qs = Article.translated_objects.fallback('de-ch').filter(
            title__icontains='This is a title'
        ).order_by('pk')

        self.assertQuerysetEqual(
            qs, [
                'This is a title',
            ],
            attrgetter('title')
        )

        self.assertQuerysetEqual(
            qs, [
                'Heute wurde publiziert, dass es einen neuen Titel gibt',
            ],
            attrgetter('body')
        )

    def test_filter_on_language(self):
        activate('en-us')
        qs = Article.translated_objects.filter(title__icontains='is').order_by('pk')
        self.assertQuerysetEqual(
            qs, [
                'This is a title',
                'Django is here',
            ],
            attrgetter('title')
        )

        activate('de-ch')
        qs = Article.translated_objects.filter(title__icontains='is').order_by('pk')
        self.assertQuerysetEqual(
            qs, [
                'Das ist ein Titel',
                'Django ist da',
            ],
            attrgetter('title')
        )

    def test_filter_on_fallback(self):
        # Search for articles that have an english title containing "this does not exist"
        # or a german title containing "das ist"
        activate('en-us')
        qs = Article.translated_objects.fallback('de-ch').filter(
            Q(title__icontains='this does not exist') |
            Q(title_fallback__icontains='das ist')
        ).order_by('pk')

        self.assertQuerysetEqual(
            qs, [
                'This is a title',
            ],
            attrgetter('title')
        )