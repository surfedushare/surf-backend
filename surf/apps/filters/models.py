"""
This module contains implementation of models for filters app.
"""

import json

from django.db import models as django_models
from mptt.models import MPTTModel, TreeForeignKey

from surf.apps.core.models import UUIDModel
from surf.apps.locale.models import Locale


class FilterItem(MPTTModel):
    name = django_models.CharField(max_length=255)
    parent = TreeForeignKey('self', on_delete=django_models.CASCADE, null=True, blank=True, related_name='children')

    created_at = django_models.DateTimeField(auto_now_add=True)
    updated_at = django_models.DateTimeField(auto_now=True)
    deleted_from_edurep_at = django_models.DateTimeField(default=None, null=True, blank=True)

    title_translations = django_models.OneToOneField(to=Locale, on_delete=django_models.CASCADE, null=True, blank=False)
    external_id = django_models.CharField(max_length=255, verbose_name="Field id in EduRep", blank=True, unique=True)
    enabled_by_default = django_models.BooleanField(default=False)
    is_hidden = django_models.BooleanField(default=False)

    item_count = 0

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "name": self.name,
            "created_at": self.created_at.strftime('%c'),
            "updated_at": self.updated_at.strftime('%c'),
            "title_translations": self.title_translations.toJSON() if self.title_translations else None,
            "external_id": self.external_id,
            "enabled_by_default": self.enabled_by_default,
            "is_hidden": self.is_hidden,
        }

    def toJSON(self):
        return json.dumps(self.to_dict())

    class MPTTMeta:
        order_insertion_by = ['name']
