# Generated by Django 2.0.13 on 2019-11-12 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filters', '0012_auto_20191112_0918'),
        ('themes', '0006_update_filtercat_disciplines'),
        ('materials', '0020_remove_old_collection_materials'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FilterCategory',
        ),
        migrations.DeleteModel(
            name='FilterCategoryItem',
        ),
    ]