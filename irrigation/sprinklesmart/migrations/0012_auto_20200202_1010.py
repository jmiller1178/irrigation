# Generated by Django 2.2.7 on 2020-02-02 10:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sprinklesmart', '0011_auto_20200126_1142'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('short_name', models.CharField(max_length=1)),
            ],
            options={
                'verbose_name': 'System Mode',
                'verbose_name_plural': 'System Modes',
                'db_table': 'system_mode',
            },
        ),
    ]