# Generated by Django 2.0.6 on 2018-12-10 10:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0002_community_collections'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurfTeam',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('external_id', models.CharField(max_length=255, verbose_name='SURFconext group id')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('admins', models.ManyToManyField(blank=True, related_name='admin_teams', to=settings.AUTH_USER_MODEL, verbose_name='Administrators')),
                ('members', models.ManyToManyField(blank=True, related_name='teams', to=settings.AUTH_USER_MODEL, verbose_name='Members')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='community',
            name='surf_team',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community', to='communities.SurfTeam'),
        ),
    ]