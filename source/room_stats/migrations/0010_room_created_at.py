# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-19 22:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('room_stats', '0009_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]