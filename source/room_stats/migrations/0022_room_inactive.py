# Generated by Django 2.0.1 on 2018-03-29 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room_stats', '0021_auto_20180327_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='inactive',
            field=models.BooleanField(default=False),
        ),
    ]