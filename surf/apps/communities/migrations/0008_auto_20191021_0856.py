# Generated by Django 2.0.13 on 2019-10-21 08:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0007_auto_20190806_1428'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'Member',
            },
        ),
        migrations.RemoveField(
            model_name='community',
            name='admins',
        ),
        migrations.RemoveField(
            model_name='community',
            name='surf_team',
        ),
        migrations.AddField(
            model_name='team',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community'),
        ),
        migrations.AddField(
            model_name='team',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='community',
            name='new_members',
            field=models.ManyToManyField(blank=True, through='communities.Team', to=settings.AUTH_USER_MODEL),
        ),
    ]