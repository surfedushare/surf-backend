# Generated by Django 2.0.13 on 2019-10-24 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0011_auto_20191021_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
    ]
