# Generated by Django 2.0.13 on 2019-08-19 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0014_set_material_applaud_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='disciplines',
        ),
    ]
