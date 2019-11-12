"""
This module contains implementation of models for materials app.
"""

import json
from datetime import datetime

from django.conf import settings
from django.db import models as django_models
from django.utils import timezone
from django_enumfield import enum

from surf.apps.core.models import UUIDModel
from surf.apps.filters.models import MpttFilterItem
from surf.apps.themes.models import Theme
from surf.statusenums import PublishStatus
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    DISCIPLINE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID
)


RESOURCE_TYPE_MATERIAL = "material"
RESOURCE_TYPE_COLLECTION = "collection"

_DISCIPLINE_FILTER = "{}:0".format(DISCIPLINE_FIELD_ID)


def add_material_themes(material, themes):
    ts = Theme.objects.filter(external_id__in=themes).all()
    material.themes.set(ts)


def add_material_disciplines(material, disciplines):
    ds = MpttFilterItem.objects.filter(external_id__in=disciplines).all()
    material.disciplines.set(ds)


def get_material_details_by_id(material_id, api_client=None):
    """
    Request from EduRep and return details of material by its EduRep id
    :param material_id: id of material in EduRep
    :param api_client: EduRep API client (optional)
    :return: list of requested materials
    """

    if not api_client:
        api_client = XmlEndpointApiClient(
            api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

    res = api_client.get_materials_by_id(['"{}"'.format(material_id)],
                                         drilldown_names=[_DISCIPLINE_FILTER])

    # define themes and disciplines for requested material
    themes = []
    disciplines = []
    for f in res.get("drilldowns", []):
        if f["external_id"] == CUSTOM_THEME_FIELD_ID:
            themes = [item["external_id"] for item in f["items"]]
        elif f["external_id"] == DISCIPLINE_FIELD_ID:
            disciplines = [item["external_id"] for item in f["items"]]

    # set extra details for requested material
    rv = res.get("records", [])
    for material in rv:
        material["themes"] = themes
        material["disciplines"] = disciplines

    return rv


class Material(UUIDModel):
    """
    Implementation of EduRep Material model.
    """

    # identifier of material in EduRep
    external_id = django_models.CharField(max_length=255,
                                          verbose_name="EduRep material id")

    # list of related themes
    themes = django_models.ManyToManyField(Theme,
                                           blank=True,
                                           related_name="materials")

    # list of related disciplines
    disciplines = django_models.ManyToManyField(MpttFilterItem,
                                                blank=True,
                                                related_name="materials")

    material_url = django_models.URLField(blank=True, null=True)
    title = django_models.TextField(blank=True, null=True)
    description = django_models.TextField(blank=True, null=True)
    keywords = django_models.TextField(blank=True, null=True)
    deleted_at = django_models.DateTimeField(null=True)

    star_1 = django_models.PositiveIntegerField(default=0)
    star_2 = django_models.PositiveIntegerField(default=0)
    star_3 = django_models.PositiveIntegerField(default=0)
    star_4 = django_models.PositiveIntegerField(default=0)
    star_5 = django_models.PositiveIntegerField(default=0)
    # a user can applaud a material many times more than he can star rate it
    applaud_count = django_models.BigIntegerField(default=0)
    view_count = django_models.BigIntegerField(default=0)

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def sync_info(self):
        assert self.external_id, "Can't sync info if instance doesn't have an external id"

        details = get_material_details_by_id(self.external_id)
        m = details[0]
        self.material_url = m.get("url")
        self.title = m.get("title")
        self.description = m.get("description")
        keywords = m.get("keywords")
        if keywords:
            keywords = json.dumps(keywords)
            self.keywords = keywords

        # always save info before adding themes & disciplines
        self.save()
        add_material_themes(self, m.get("themes", []))
        add_material_disciplines(self, m.get("disciplines", []))

    def __str__(self):
        return self.external_id


class Collection(UUIDModel):
    """
    Implementation of Collection model.
    """

    title = django_models.CharField(max_length=255)

    # the list of collection materials
    materials = django_models.ManyToManyField(Material,
                                              blank=True,
                                              related_name="collections",
                                              through='CollectionMaterial')

    is_shared = django_models.BooleanField(default=False)
    publish_status = enum.EnumField(PublishStatus, default=PublishStatus.DRAFT)
    deleted_at = django_models.DateTimeField(null=True)

    def restore(self):
        self.deleted_at = None
        self.save()

    def delete(self, using=None, keep_parents=False):
        if not self.deleted_at:
            self.deleted_at = timezone.now()
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.title


class CollectionMaterial(django_models.Model):
    collection = django_models.ForeignKey(Collection, on_delete=django_models.CASCADE)
    material = django_models.ForeignKey(Material, on_delete=django_models.CASCADE)
    featured = django_models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Material'


class SharedResourceCounter(UUIDModel):
    """
    Implementation of model for counter of shared resource.
    This model is used to store counter values for different shared objects.
    """

    counter_key = django_models.CharField(max_length=255)
    counter_value = django_models.IntegerField(default=0)
    extra = django_models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def increase_counter(counter_key, extra=None):
        """
        Increases the counter value by its key
        :param counter_key: key of counter
        :param extra: extra data for counter
        """

        if not counter_key:
            return

        c, _ = SharedResourceCounter.objects.get_or_create(
            counter_key=counter_key,
            defaults=dict(extra=extra))

        c.counter_value += 1
        c.save()

    @staticmethod
    def create_counter_key(resource_type, resource_id, share_type=None):
        """
        Creates counter key by resource type, id and sharing type
        :param resource_type: the type of resource
        :param resource_id: the identifier of resource
        :param share_type: sharing type of resource (optional)
        :return: created counter key
        """
        if share_type:
            return "{}__{}__{}__".format(resource_type, resource_id,
                                         share_type)
        else:
            return "{}__{}__".format(resource_type, resource_id)

    def __str__(self):
        return "{} - {}".format(self.counter_key, self.extra)
