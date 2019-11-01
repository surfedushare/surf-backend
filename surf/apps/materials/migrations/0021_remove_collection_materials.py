# Generated by Django 2.0.13 on 2019-11-01 12:55

from django.db import migrations


def copy_materials_to_old_collections(apps, schema_editor):
    Collection = apps.get_model('materials', 'Collection')
    CollectionMaterial = apps.get_model('materials', 'CollectionMaterial')

    for collection in Collection.objects.all():
        for material in collection.new_materials.all():
            collection.materials.add(material)

        collection.save()


def remove_old_materials(apps, schema_editor):
    # this is just here to allow the reverse migration
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0020_auto_20191101_1236'),
    ]

    operations = [
        migrations.RunPython(remove_old_materials, copy_materials_to_old_collections),
        migrations.RemoveField(
            model_name='collection',
            name='materials',
        ),
        migrations.RenameField(
            model_name='collection',
            old_name='new_materials',
            new_name='materials',
        ),
    ]
