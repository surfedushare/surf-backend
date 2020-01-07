from collections import defaultdict

from django.conf import settings
from elasticsearch import Elasticsearch

from surf.apps.querylog.models import QueryLog
from surf.vendor.search.choices import DISCIPLINE_CUSTOM_THEME
from surf.vendor.edurep.xml_endpoint.v1_2.xml_parser import _parse_vcard


index_nl = 'latest-nl'
index_en = 'latest-en'
_VCARD_FORMATED_NAME_KEY = "FN"


class ElasticSearchApiClient:

    def __init__(self, elastic_url=settings.ELASTICSEARCH_URL):
        self.elastic = Elasticsearch(
            [elastic_url],
            http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
            scheme="https",
            port=443,
        )

    @staticmethod
    def parse_elastic_result(search_result):

        hits = search_result["hits"]
        aggregations = search_result.get("aggregations", {})
        result = dict()
        result['recordcount'] = hits['total']

        # Transform aggregations into drilldowns
        drilldowns = []
        for aggregation_name, aggregation in aggregations.items():
            items = [
                {
                    "external_id": bucket["key"],
                    "count": bucket["doc_count"]
                }
                for bucket in aggregation["buckets"]
            ]
            drilldowns.append({
                "external_id": aggregation_name,
                "items": items
            })
        result['drilldowns'] = drilldowns

        # Transform hits into records
        result['records'] = [
            ElasticSearchApiClient.parse_elastic_hit(hit)
            for hit in hits['hits']
        ]

        return result

    @staticmethod
    def parse_elastic_hit(hit):
        record = dict()
        record['external_id'] = hit['_source']['external_id']
        record['url'] = hit['_source']['url']
        record['title'] = hit['_source']['title']
        record['description'] = hit['_source']['description']
        record['keywords'] = hit['_source']['keywords']
        record['language'] = hit['_source']['language']
        record['publish_datetime'] = hit['_source']['publisher_date']
        author = hit['_source']['author']
        if author and isinstance(author, list):
            author = _parse_vcard(author[0]).get(_VCARD_FORMATED_NAME_KEY)
        if not author:
            author = None
        record['author'] = author
        record['format'] = hit['_source']['file_type']
        record['disciplines'] = hit['_source']['disciplines']
        record['educationallevels'] = hit['_source']['educational_levels']
        record['copyright'] = hit['_source']['copyright']
        themes = set()
        for discipline in hit['_source']['disciplines']:
            if discipline in DISCIPLINE_CUSTOM_THEME:
                themes.update(DISCIPLINE_CUSTOM_THEME[discipline])
        record['themes'] = list(themes)
        record['source'] = hit['_source']['arrangement_collection_name']
        return record

    def autocomplete(self, query):
        query_dictionary = {
            'suggest': {
                "autocomplete": {
                    'text': query,
                    "completion": {
                        "field": "suggest"
                    }
                }
            }
        }

        result = self.elastic.search(
            index=[index_nl, index_en],
            doc_type='entity',
            body=query_dictionary,
            _source_include='suggest'
        )

        autocomplete = result['suggest']['autocomplete']
        options = autocomplete[0]['options']
        flat_options = list(set([item for option in options for item in option['_source']['suggest']]))
        options_with_prefix = [option for option in flat_options if option.startswith(query)]
        options_with_prefix.sort(key=lambda option: len(option))
        return options_with_prefix

    def drilldowns(self, drilldown_names, search_text=None, filters=None):
        search_results = self.search(search_text=search_text, filters=filters, drilldown_names=drilldown_names)
        search_results["records"] = []
        return search_results

    def search(self, search_text: list, drilldown_names=None, filters=None, ordering=None, page=1, page_size=5):
        search_text = search_text or []
        assert isinstance(search_text, list), "A search needs to be specified as a list of terms"
        # build basic query
        start_record = page_size * (page - 1) + 1
        body = {
            'query': {
                "bool": defaultdict(list)
            },
            'from': start_record,
            'size': page_size,
        }
        # add a search query if any
        if len(search_text):
            query_string = {
                "query_string": {
                    "fields": ["text", "title"],
                    "query": ' AND '.join(search_text)
                }
            }
            body["query"]["bool"]["must"] += [query_string]
        indices = self.parse_index_language(filters)
        # apply filters
        filters = self.parse_filters(filters)
        if filters:
            body["query"]["bool"]["must"] += filters
        # add aggregations
        if drilldown_names:
            body["aggs"] = self.parse_aggregations(drilldown_names)
        # add ordering
        if ordering:
            body["sort"] = [
                self.parse_ordering(ordering),
                "_score"
            ]
        # make query and parse
        result = self.elastic.search(
            index=indices,
            body=body
        )
        parsed_result = self.parse_elastic_result(result)
        if start_record == 1 and search_text:
            url = f"es.search(index={indices}, body={body})"
            QueryLog(search_text=" AND ".join(search_text), filters=filters, query_url=url,
                     result_size=parsed_result['recordcount'], result=parsed_result).save()
        return parsed_result

    def get_materials_by_id(self, external_ids, **kwargs):
        result = self.elastic.search(
            index=[index_nl, index_en],
            body={
                "query": {
                    "bool": {
                        "must": [{"terms": {"external_id": external_ids}}]
                    }
                },
            },
        )
        materials = self.parse_elastic_result(result)
        return materials

    @staticmethod
    def parse_filters(filters):
        filter_items = []
        if not filters:
            return {}
        date_filter = None
        for filter_item in filters:
            if not filter_item['items'] or 'lom.general.language' in filter_item['external_id']:
                continue
            elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(filter_item['external_id'])
            if elastic_type == "publisher_date":
                date_filter = filter_item
                continue
            filter_items.append({
                "terms": {
                    elastic_type: filter_item["items"]
                }
            })
        if date_filter:
            lower_bound, upper_bound = date_filter["items"]
            if lower_bound is not None or upper_bound is not None:
                filter_items.append({
                    "range": {
                        "publisher_date": {
                            "gte": lower_bound,
                            "lte": upper_bound
                        }
                    }
                })
        return filter_items

    @staticmethod
    def parse_aggregations(aggregation_names):
        aggregation_items = {}
        for aggregation_name in aggregation_names:
            elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(aggregation_name)
            aggregation_items[aggregation_name] = {
                "terms": {
                    "field": elastic_type,
                    # Raise the default limit of 10 items for aggregation
                    "size": 500,
                }
            }
        return aggregation_items

    @staticmethod
    def parse_ordering(ordering):
        order = "asc"
        if ordering.startswith("-"):
            order = "desc"
            ordering = ordering[1:]
        elastic_type = ElasticSearchApiClient.translate_external_id_to_elastic_type(ordering)
        return {elastic_type: {"order": order}}

    @staticmethod
    def parse_index_language(filters):
        indices = [index_nl, index_en]
        if not filters:
            return indices
        language_item = [filter_item for filter_item in filters if filter_item['external_id'] == 'lom.general.language']
        if not language_item:
            return indices
        language_indices = [f"latest-{language}" for language in language_item[0]['items']]
        return language_indices if len(language_indices) else indices

    @staticmethod
    def translate_external_id_to_elastic_type(external_id):
        """ The external id's used in edurep need to be parsed to fields in elasticsearch. """
        if external_id == 'lom.technical.format':
            return 'file_type'
        elif external_id == 'about.repository':
            return 'arrangement_collection_name'
        elif external_id == 'lom.rights.copyrightandotherrestrictions':
            return 'copyright.keyword'
        elif external_id == 'lom.classification.obk.educationallevel.id':
            return 'educational_levels'
        elif external_id == "lom.lifecycle.contribute.publisherdate":
            return 'publisher_date'
        elif external_id == "lom.classification.obk.discipline.id":
            return 'disciplines'
        return external_id
