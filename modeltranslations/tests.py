from operator import attrgetter
from django.db.models import Q

from django.test import TestCase
from modeltranslations.expressions import ConditionalJoin
from modeltranslations.models import Article, ArticleTranslation


class TranslationAnnotationTest(TestCase):
    def setUp(self):
        self.a1 = Article.objects.create()
        self.at1_de = ArticleTranslation(
            article=self.a1,
            lang='de',
            title='Das ist ein Titel',
            body='Heute wurde publiziert, dass es einen neuen Titel gibt'
        )
        self.at1_de.save()
        self.at1_en = ArticleTranslation(
            article=self.a1,
            lang='en',
            title='This is a title',
            body='')
        self.at1_en.save()

        self.a2 = Article.objects.create()
        self.at1_de = ArticleTranslation(
            article=self.a2,
            lang='de',
            title='Django ist da',
            body='Die neue Django Version ist da!'
        )
        self.at1_de.save()
        self.at1_en = ArticleTranslation(
            article=self.a2,
            lang='en',
            title='Django is here',
            body='The new Django version is here!')
        self.at1_en.save()

    def test_translations_and_fallback(self):
        # Dynamic run-time fallback population of language fields
        qs = Article.objects.annotate(
            title=ConditionalJoin(
                'articletranslation__title',
                conditions=Q(articletranslation__lang='en')
            ),
            body=ConditionalJoin(
                'articletranslation__body',
                conditions=Q(articletranslation__lang='en')
            )
        ).annotate(
            title_de=ConditionalJoin(
                'articletranslation__title',
                conditions=Q(articletranslation__lang='de')
            )
        ).order_by('pk')

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

        self.assertQuerysetEqual(
            qs, [
                'Das ist ein Titel',
                'Django ist da',
            ],
            attrgetter('title_de')
        )
