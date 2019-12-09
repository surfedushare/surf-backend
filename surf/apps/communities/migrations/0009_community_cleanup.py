# Generated by Django 2.2.7 on 2019-12-05 13:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('communities', '0008_auto_20191104_1008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='admins',
        ),
        migrations.RemoveField(
            model_name='community',
            name='is_available',
        ),
        migrations.RemoveField(
            model_name='community',
            name='members',
        ),
        migrations.RemoveField(
            model_name='community',
            name='surf_team',
        ),
        migrations.DeleteModel(
            name='SurfTeam',
        ),
        migrations.RenameField(
            model_name='community',
            old_name='new_members',
            new_name='members',
        ),
    ]
