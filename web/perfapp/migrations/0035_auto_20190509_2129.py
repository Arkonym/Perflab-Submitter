# Generated by Django 2.1.5 on 2019-05-10 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfapp', '0034_auto_20190508_2257'),
    ]

    operations = [
        migrations.AddField(
            model_name='attempt',
            name='result_out',
            field=models.TextField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='error',
            name='errors',
            field=models.TextField(blank=True, default=None, null=True),
        ),
    ]
