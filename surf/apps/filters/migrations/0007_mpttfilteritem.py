# Generated by Django 2.0.13 on 2019-08-09 12:53

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('locale', '0004_improved_translations'),
        ('filters', '0006_filtercategory_title_translations'),
    ]

    operations = [
        migrations.CreateModel(
            name='MpttFilterItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_from_edurep_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('external_id', models.CharField(blank=True, max_length=255, verbose_name='Field id in EduRep')),
                ('enabled_by_default', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='filters.MpttFilterItem')),
                ('title_translations', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='locale.Locale')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
