# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-25 15:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sprinklesmart', '0002_auto_20171124_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='irrigationschedule',
            name='sortOrder',
            field=models.IntegerField(default=0),
        ),
    ]