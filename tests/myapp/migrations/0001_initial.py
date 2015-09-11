# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import citadel.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('citadel', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuriedTreasure',
            fields=[
                ('secretivemodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='citadel.SecretiveModel')),
                ('location', citadel.fields.SecretField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            bases=('citadel.secretivemodel',),
        ),
    ]
