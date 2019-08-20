"""
This module provides django admin functionality for filters app.
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from surf.apps.filters import models


@admin.register(models.FilterItem)
class MpttFilterItemAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title')
    list_display_links = ('indented_title', )
