# Generated by Django 2.0.13 on 2019-08-06 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locale', '0004_improved_translations'),
        ('filters', '0005_filtercategoryitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='filtercategory',
            name='title_translations',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='locale.Locale'),
        ),
    ]
