# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0025_migrate_publis'),
    ]

    operations = [
        migrations.DeleteModel('Publication'),
    ]
