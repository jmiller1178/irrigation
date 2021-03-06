# Generated by Django 2.2.7 on 2020-02-02 15:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sprinklesmart', '0014_irrigationsystem_system_zone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='irrigationsystem',
            name='system_zone',
        ),
        migrations.AddField(
            model_name='irrigationsystem',
            name='system_enabled_zone',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='system_enabled_zone', to='sprinklesmart.Zone'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='irrigationsystem',
            name='valves_enabled_zone',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='valves_enabled_zone', to='sprinklesmart.Zone'),
            preserve_default=False,
        ),
    ]
