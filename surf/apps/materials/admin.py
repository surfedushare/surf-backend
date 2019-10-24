"""
This module provides django admin functionality for materials app.
"""

from django.contrib import admin

from surf.apps.materials import models
from surf.apps.materials.utils import BooleanDateFieldListFilter

def trash_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.delete()


trash_nodes.short_description = "Trash selected %(verbose_name_plural)s"


def restore_nodes(modeladmin, request, queryset):
    for obj in queryset:
        obj.restore()


restore_nodes.short_description = "Restore selected %(verbose_name_plural)s"


@admin.register(models.Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Material model.
    """

    list_display = ("title", "external_id", "deleted",)
    list_filter = (("deleted_at", BooleanDateFieldListFilter),)
    readonly_fields = (
        'external_id', 'themes', 'disciplines', 'material_url', 'title',
        'description', 'keywords', "deleted_at",
    )
    actions = [restore_nodes, trash_nodes]

    def deleted(self, instance):
        return instance.deleted_at is not None
    deleted.boolean = True
    deleted.short_description = 'Has been deleted'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            # remove "only for admin" actions
            actions.pop('fill_material_data', None)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            del actions["trash_nodes"]
        else:
            del actions["delete_selected"]
            del actions["restore_nodes"]
        return actions


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Provides admin options and functionality for Collection model.
    """

    list_display = ("title", "owner", "publish_status", "deleted",)
    list_filter = ("owner", "publish_status", ("deleted_at", BooleanDateFieldListFilter),)
    readonly_fields = ('title', 'owner', "deleted_at",)
    ordering = ("title",)
    actions = [restore_nodes, trash_nodes]

    def deleted(self, instance):
        return instance.deleted_at is not None
    deleted.boolean = True
    deleted.short_description = 'Has been deleted'

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            filter_trash = bool(int(request.GET.get('trash', '0')))
        except ValueError:
            filter_trash = False
        if filter_trash:
            del actions["trash_nodes"]
        else:
            del actions["delete_selected"]
            del actions["restore_nodes"]
        return actions
