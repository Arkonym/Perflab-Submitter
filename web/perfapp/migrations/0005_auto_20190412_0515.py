# Generated by Django 2.1.5 on 2019-04-12 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfapp', '0004_profile_max_score_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='last_login',
        ),
        migrations.AddField(
            model_name='job',
            name='config',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='job',
            name='percent_complete',
            field=models.SmallIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='job',
            name='task_id',
            field=models.SmallIntegerField(blank=True, default=-1),
        ),
        migrations.AddField(
            model_name='server',
            name='uID',
            field=models.SmallIntegerField(blank=True, default=-1),
        ),
        migrations.AlterField(
            model_name='job',
            name='FilterMain',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='job',
            name='Filter_c',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='job',
            name='Filter_h',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='job',
            name='Makefile',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='job',
            name='cs1300_c',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='job',
            name='cs1300_h',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='job',
            name='status',
            field=models.CharField(default='New', max_length=10),
        ),
    ]
