# Generated by Django 2.0.13 on 2019-08-30 08:13

from django.db import migrations
from surf.apps.themes.models import Theme
from surf.apps.filters.models import FilterCategoryItem, MpttFilterItem

def clone_filter_items_to_mptt(apps, schema_editor):
    # Somehow MPTT doesn't enjoy being imported by apps.get_model (it'll error on not having values for 'lft' and 'rgt'
    # So use direct imports instead.
    # #Theme = apps.get_model('themes', 'Theme')
    # FilterCategoryItem = apps.get_model('filters', 'FilterCategoryItem')
    # MpttFilterItem = apps.get_model('filters', 'MpttFilterItem')
    theme_root_node = MpttFilterItem.objects.get(external_id="custom_theme.id")
    vakgebied_root_node = MpttFilterItem.objects.get(external_id="lom.classification.obk.discipline.id")
    for theme in Theme.objects.all():
        filter_category_item = theme.filter_category_item
        mpttfilteritem, created = MpttFilterItem.objects.get_or_create(name=filter_category_item.title,
                                                                       parent=theme_root_node)
        theme.mptt_filter_category_item = mpttfilteritem

        disciplines = theme.disciplines
        for discipline in disciplines.all():
            mpttfilteritem, created = MpttFilterItem.objects.get_or_create(name=discipline.title,
                                                                           parent=vakgebied_root_node)
            theme.mptt_disciplines.add(mpttfilteritem)

        theme.save()


def reverse(apps, schema_editor):
    Theme = apps.get_model('themes', 'Theme')
    for theme in Theme.objects.all():
        theme.mptt_filter_category_item = None
        theme.mptt_disciplines.clear()
        theme.save()


class Migration(migrations.Migration):

    dependencies = [
        ('themes', '0004_auto_20190830_0813'),
    ]

    operations = [
        migrations.RunPython(clone_filter_items_to_mptt, reverse)
    ]