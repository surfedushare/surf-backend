# Generated by Django 2.0.13 on 2019-08-30 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filters', '0008_auto_20190829_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='filteritem',
            name='mptt_category_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filter_items', to='filters.MpttFilterItem'),
        ),
    ]
