# Generated by Django 2.2.7 on 2020-02-22 12:49

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('sprinklesmart', '0015_auto_20200202_1538'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='rpigpiorequest',
            managers=[
                ('todays_requests', django.db.models.manager.Manager()),
            ],
        ),
    ]
