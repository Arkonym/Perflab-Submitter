# Generated by Django 2.1.5 on 2019-05-03 05:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfapp', '0025_error_time_stamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='error',
            name='errors',
        ),
    ]
