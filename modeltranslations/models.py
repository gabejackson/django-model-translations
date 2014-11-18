from django.db import models


class Article(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)


class ArticleTranslation(models.Model):
    article = models.ForeignKey(Article)
    lang = models.CharField(max_length=4)
    title = models.CharField(max_length=100)
    body = models.TextField()
