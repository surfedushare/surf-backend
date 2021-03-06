# Generated by Django 2.2.10 on 2020-03-25 10:57

import django.core.validators
from django.db import migrations, models
import surf.apps.communities.models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0010_auto_20200214_1051'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='communitydetail',
            name='unique materials in collection',
        ),
        migrations.AlterField(
            model_name='community',
            name='name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='featured_image',
            field=models.ImageField(blank=True, null=True, upload_to='communities', validators=[django.core.validators.validate_image_file_extension, surf.apps.communities.models.validate_featured_size]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='communities', validators=[django.core.validators.validate_image_file_extension, surf.apps.communities.models.validate_logo_size]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='title',
            field=models.CharField(max_length=255, validators=[django.core.validators.MinLengthValidator(1)]),
        ),
        migrations.AlterField(
            model_name='communitydetail',
            name='website_url',
            field=models.URLField(blank=True, null=True, validators=[django.core.validators.URLValidator]),
        ),
        migrations.AddConstraint(
            model_name='communitydetail',
            constraint=models.UniqueConstraint(fields=('language_code', 'community'), name='unique languages in community'),
        ),
    ]
