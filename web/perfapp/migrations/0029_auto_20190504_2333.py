# Generated by Django 2.1.5 on 2019-05-05 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfapp', '0028_remove_job_fail_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attempt',
            name='time_stamp',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]