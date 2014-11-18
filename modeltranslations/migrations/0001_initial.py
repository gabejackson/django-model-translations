# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.translation
import modeltranslations.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('lang', models.CharField(default=django.utils.translation.get_language, max_length=20, db_index=True, choices=[(b'en-us', b'English'), (b'de-ch', b'German')])),
                ('article', modeltranslations.fields.TranslationForeignKey(to='modeltranslations.Article')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
