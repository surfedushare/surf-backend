# Generated by Django 2.0.6 on 2018-11-16 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0006_viewmaterial_viewed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='is_shared',
            field=models.BooleanField(default=False),
        ),
    ]