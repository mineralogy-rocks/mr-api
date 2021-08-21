from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_TERMS,
    LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_IN,
    LOOKUP_QUERY_GT,
    LOOKUP_QUERY_GTE,
    LOOKUP_QUERY_LT,
    LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_EXCLUDE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
    SimpleQueryStringSearchFilterBackend,
    NestedFilteringFilterBackend,
    HighlightBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination

from .documents import MineralLogDocument
from .serializers import MineralLogDocumentSerializer

class MineralLogDocumentView(BaseDocumentViewSet):
    """The MineralLogDocument view."""

    document = MineralLogDocument
    serializer_class = MineralLogDocumentSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'id'
    filter_backends = [
        HighlightBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
        NestedFilteringFilterBackend,
        
    ]
    # Define search fields
    search_fields = (
        'mineral_name',
    )

    simple_query_string_search_fields = {
        'mineral_name': {
            'field': 'mineral_name'
        },
    }

    # Define highlight tags
    highlight_fields = {
        'mineral_name': {
            'enabled': True,
            'options': {
                'pre_tags': ["<b>"],
                'post_tags': ["</b>"],
            },
        },
    }

    # Define filter fields
    filter_fields = {
        'mineral_name': {
            'field': 'mineral_name',
            # Note, that we limit the lookups of id field in this example,
            # to `range`, `in`, `gt`, `gte`, `lt` and `lte` filters.
            'lookups': [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_RANGE,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_GT,
                LOOKUP_QUERY_GTE,
                LOOKUP_QUERY_LT,
                LOOKUP_QUERY_LTE,
            ],
        },
        'status': {
            'field': 'status.status_id.raw',
            'lookups': [
                LOOKUP_FILTER_TERMS,
            ]
        }
    }

    # Nested filtering fields
    nested_filter_fields = {
        'status': {
            'field': 'status.status_id.raw',
            'path': 'status',
        }
    }

    # Define ordering fields
    ordering_fields = {
        'mineral_name': 'mineral_name',
    }
    # Specify default ordering
    ordering = ('_score', 'mineral_name', 'formula',)