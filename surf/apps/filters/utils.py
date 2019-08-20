"""
This module contains some common functions for filters app.
"""

import datetime
import re

from django.conf import settings

from surf.apps.filters.models import (
    FilterItem
)
from surf.apps.locale.models import Locale
from surf.apps.themes.models import Theme
from surf.vendor.edurep.widget_endpoint.v3.api import WidgetEndpointApiClient
from surf.vendor.edurep.xml_endpoint.v1_2.api import (
    XmlEndpointApiClient,
    PUBLISHER_DATE_FIELD_ID,
    CUSTOM_THEME_FIELD_ID,
    DISCIPLINE_FIELD_ID,
    COPYRIGHT_FIELD_ID,
    EDUCATIONAL_LEVEL_FIELD_ID,
    LANGUAGE_FIELD_ID,
)
from surf.vendor.edurep.xml_endpoint.v1_2.choices import (
    CUSTOM_THEME_DISCIPLINES,
    CUSTOM_COPYRIGHTS,
    DISCIPLINE_ENTRIES
)

IGNORED_FIELDS = {PUBLISHER_DATE_FIELD_ID,
                  CUSTOM_THEME_FIELD_ID,
                  LANGUAGE_FIELD_ID}

_MBO_HBO_WO_REGEX = re.compile(r"^(MBO|HBO|WO)(.*)$", re.IGNORECASE)
_HBO_WO_REGEX = re.compile(r"^(HBO|WO)(.*)$", re.IGNORECASE)

_DISCIPLINE_FILTER = "{}:0".format(DISCIPLINE_FIELD_ID)

_MAX_DISCIPLINES_IN_FILTER = 20


def get_material_count_by_disciplines(discipline_ids):
    """
    Returns the number of materials for each discipline
    :param discipline_ids: identifiers if disciplines in EduRep
    :return: dictionary with number of materials in EduRep for each discipline
    """

    rv = dict()

    # add default filters to search materials
    filters = get_all_materials_filters()

    ac = XmlEndpointApiClient(
        api_endpoint=settings.EDUREP_XML_API_ENDPOINT)

    discipline_ids = list(discipline_ids)
    while discipline_ids:
        # request drilldowns only for part of disciplines
        if len(discipline_ids) > _MAX_DISCIPLINES_IN_FILTER:
            ds = discipline_ids[:_MAX_DISCIPLINES_IN_FILTER:]
            discipline_ids = discipline_ids[_MAX_DISCIPLINES_IN_FILTER::]
        else:
            ds, discipline_ids = discipline_ids, []

        fs = [dict(external_id=DISCIPLINE_FIELD_ID, items=ds)]
        fs.extend(filters)

        drilldowns = ac.drilldowns([_DISCIPLINE_FILTER], filters=fs)
        if drilldowns:
            drilldowns = drilldowns.get("drilldowns", [])
            for f in drilldowns:
                if f["external_id"] == DISCIPLINE_FIELD_ID:
                    drilldowns = {item["external_id"]: item["count"]
                                  for item in f["items"]}
                    break
            else:
                drilldowns = None

        if drilldowns:
            rv.update({k: drilldowns[k] for k in ds if k in drilldowns})

    return rv

# # I don't think we'll need this function later on...
# def add_default_filters(filters):
#     """
#     Adds default filters to search materials in EduRep
#     :param filters: current filters
#     :return: updated list of filters
#     """
#
#     filter_categories = {f.get("external_id"): f.get("items", [])
#                          for f in filters}
#
#     # add default filters for Educational Level if needed
#     if not filter_categories.get(EDUCATIONAL_LEVEL_FIELD_ID):
#         items = FilterItem.objects.filter(
#             category__external_id=EDUCATIONAL_LEVEL_FIELD_ID).all()
#         items = [it.external_id for it in items
#                  if _HBO_WO_REGEX.match(it.title)]
#
#         filters.append(
#             dict(external_id=EDUCATIONAL_LEVEL_FIELD_ID, items=items))
#
#     # add default filters for Copyrights if needed
#     if not filter_categories.get(COPYRIGHT_FIELD_ID):
#         items = FilterItem.objects.filter(
#             category__edurep_field_id=COPYRIGHT_FIELD_ID).all()
#         items = [it.external_id for it in items]
#         filters.append(dict(external_id=COPYRIGHT_FIELD_ID, items=items))
#
#     return filters


def get_all_materials_filters():
    """
    Returns filters to get all available materials from EduRep
    :return: list of filters
    """

    rv = []
    for filter_id in {EDUCATIONAL_LEVEL_FIELD_ID, COPYRIGHT_FIELD_ID}:
        items = FilterItem.objects.filter(external_id=filter_id).all()

        items = [it.external_id for it in items]
        rv.append(dict(external_id=filter_id, items=items))

    return rv


def check_and_update_filters():
    """
    Updates filter categories and their items in database
    """

    ac = None
    qs = FilterItem.objects

    for f_category in qs.all():
        if f_category.external_id in IGNORED_FIELDS:
            print(f"Skipping {f_category.external_id} because it's in ignored fields.")
            continue

        if not ac:
            ac = WidgetEndpointApiClient(api_endpoint=settings.EDUREP_JSON_API_ENDPOINT)
        try:
            print(f'Updating {f_category.external_id}')
        except UnicodeEncodeError as exc:
            print(exc)
        _update_mptt_filter_category(f_category, ac)
    print("Finished Update")


def update_filter_category(filter_category):
    """
    Updates filter category and its items
    :param filter_category: filter category DB instance
    """

    ac = WidgetEndpointApiClient(
        api_endpoint=settings.EDUREP_JSON_API_ENDPOINT)

    if filter_category.external_id == CUSTOM_THEME_FIELD_ID:
        _update_themes(filter_category)

    elif filter_category.external_id == COPYRIGHT_FIELD_ID:
        _update_copyrights(filter_category)

    elif filter_category.external_id == DISCIPLINE_FIELD_ID:
        _update_mptt_filter_category(filter_category, ac)
        _update_themes_disciplines(filter_category)

    elif filter_category.external_id not in IGNORED_FIELDS:
        _update_mptt_filter_category(filter_category, ac)


def _update_themes(theme_category):
    """
    Updates all themes and their disciplines in database
    :param theme_category: DB instance of Theme filter category
    """

    for theme_id, disciplines in CUSTOM_THEME_DISCIPLINES.items():
        # get or create Theme category item

        ci, _ = FilterItem.objects.get_or_create(
            category_id=theme_category.id,
            external_id=theme_id,
            defaults=dict(title=theme_id))

        # get or create theme
        t, _ = Theme.objects.get_or_create(external_id=theme_id)

        # relate theme with category item
        t.filter_category_item = ci
        t.save()

        # set theme disciplines
        ds = []
        for d in disciplines:
            d = FilterItem.objects.filter(
                category__external_id=DISCIPLINE_FIELD_ID,
                external_id=d).first()
            if d:
                ds.append(d)
        t.disciplines.set(ds)


def _update_themes_disciplines(discipline_category):
    """
    Updates all disciplines related to themes in database
    :param discipline_category: DB instance of Discipline filter category
    """

    for d in DISCIPLINE_ENTRIES:
        # get or create Discipline category item
        FilterItem.objects.get_or_create(
            category_id=discipline_category.id,
            external_id=d["id"],
            defaults=dict(title=d["name"]))


def _update_copyrights(copyrights_category):
    """
    Updates all copyrights in database
    :param copyrights_category: DB instance of Copyrights filter category
    """

    for copyright_id, copyright_data in CUSTOM_COPYRIGHTS.items():
        FilterItem.objects.get_or_create(
            category_id=copyrights_category.id,
            external_id=copyright_id,
            defaults=dict(title=copyright_data["title"]))


def _update_mptt_filter_category(filter_category, api_client):
    """
    Updates filter category according to data received from EduRep
    :param filter_category: filter category DB instance
    :param api_client: api client to EduRep
    """

    category_id = filter_category.external_id
    drilldown_name = "{}:{}".format(category_id, 0)
    res = api_client.drilldowns([drilldown_name], filters=None)
    items = res.get(category_id)
    if not items:
        return
    if category_id.endswith(".id"):
        _update_nested_mptt_items(filter_category, items)

    else:
        for k, v in items.items():
            if isinstance(v, dict):
                _update_mptt_category_item(filter_category, k, v["human"])
            else:
                _update_mptt_category_item(filter_category, k, k)


def _update_nested_mptt_items(filter_category, items):
    for item in items:
        _update_mptt_category_item(filter_category,
                              item["identifier"],
                              item["caption"])
        children = item.get("children")
        if children:
            _update_nested_mptt_items(filter_category, children)


def _update_mptt_category_item(filter_category, item_id, item_title):
    if not _is_valid_mptt_category_item(filter_category, item_id, item_title):
        return
    # print(filter_category.id)
    # print(item_id)
    # print(item_title)
    # print(f"Parent node {filter_category.name}")
    # print(f"I want to create category_id {filter_category.id}, external_id {item_id}, item_title {item_title}")
    # normally we'd do this with a get_or_create, however since we want to leave the manually adjusted tree intact
    # we're doing it manually.
    if not FilterItem.objects.filter(name=item_title).exists():
        translation = Locale.objects.create(
            asset=f"{item_title}_auto_generated_at_{datetime.datetime.now().strftime('%c')}",
            en=item_title, nl=item_title, is_fuzzy=True)

        FilterItem.objects.create(name=item_title, parent=filter_category,
                                  title_translations=translation, external_id=item_id)
    else:
        FilterItem.objects.get_or_create(name=item_title, external_id=item_id)


def _is_valid_mptt_category_item(filter_category, item_id, item_title):
    if filter_category.external_id != EDUCATIONAL_LEVEL_FIELD_ID:
        return True

    return _MBO_HBO_WO_REGEX.match(item_title) is not None
