# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-27 12:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sprinklesmart', '0007_zone_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='zone',
            name='sortOrder',
            field=models.IntegerField(default=0),
        ),
    ]
