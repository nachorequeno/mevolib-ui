# Generated by Django 4.2.7 on 2024-01-19 15:23

from django.db import migrations, models
import pathlib


class Migration(migrations.Migration):

    dependencies = [
        ('nextflowApp', '0014_alter_inferencedocument_docfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParamInferenceDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docfile', models.FileField(upload_to=pathlib.PurePosixPath('nextflowFiles/uploads/param_inference'))),
            ],
        ),
    ]
