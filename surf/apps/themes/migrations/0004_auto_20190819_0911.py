# Generated by Django 2.0.13 on 2019-08-19 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('themes', '0003_improved_translations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theme',
            name='disciplines',
        ),
        migrations.RemoveField(
            model_name='theme',
            name='filter_category_item',
        ),
    ]
