# Generated by Django 2.0.6 on 2018-11-04 08:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('materials', '0003_auto_20181026_0857'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplaudMaterial',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applauds', to='materials.Material')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applauds', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
