from django.db import models
from modeltranslations.fields import TranslationForeignKey


class Article(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)


class ArticleTranslation(models.Model):
    article = TranslationForeignKey('Article')
    title = models.CharField(max_length=100)
    body = models.TextField()
