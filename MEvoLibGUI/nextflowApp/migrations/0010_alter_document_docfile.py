# Generated by Django 4.2.7 on 2024-01-18 11:52

from django.db import migrations, models
import pathlib


class Migration(migrations.Migration):

    dependencies = [
        ('nextflowApp', '0009_alter_document_docfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(upload_to=pathlib.PurePosixPath('nextflowFiles/uploads/inference')),
        ),
    ]
