# Generated by Django 2.1.5 on 2019-05-05 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfapp', '0029_auto_20190504_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='task_id',
            field=models.CharField(blank=True, default=None, max_length=40, null=True),
        ),
    ]
