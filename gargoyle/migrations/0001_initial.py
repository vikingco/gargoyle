# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('key', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('value', jsonfield.fields.JSONField(default=b'{}')),
                ('label', models.CharField(max_length=64, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(null=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(1, b'Disabled'), (2, b'Selective'), (3, b'Global'), (4, b'Inherit')])),
            ],
            options={
                'verbose_name': 'switch',
                'verbose_name_plural': 'switches',
                'permissions': (('can_view', 'Can view'),),
            },
        ),
    ]
