# Generated by Django 2.0.13 on 2019-10-21 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0009_auto_20191021_0916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='members',
        ),
    ]
