from django.db import connection
from django.db.models import Q, OuterRef, F, Subquery, Min, Max, Value, Case, When, Count, Exists, CharField
from django.db.models.functions import JSONObject, Concat, Right, Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import  AllowAny

from .models.core import Status, StatusGroup, NsFamily
from .models.mineral import Mineral, MineralHistory, MineralRelation, MineralHierarchy, MineralCountry, MineralStatus
from .serializers.core import StatusListSerializer
from .serializers.mineral import MineralListSerializer
from .filters import StatusFilter, MineralFilter


class StatusViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):

    http_method_names = ['get', 'options', 'head',]

    queryset = Status.objects.all()
    serializer_class = StatusListSerializer

    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, ]
    permission_classes = [AllowAny,]
    authentication_classes = []

    ordering_fields = ['status_id', 'status_group', ]
    ordering = ['status_id',]

    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend,]
    search_fields = ['description_short', 'description_long', 'status_group__name',]
    filterset_class = StatusFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, 'setup_eager_loading'):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        return queryset



class MineralViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):

    http_method_names = ['get', 'options', 'head',]

    queryset = Mineral.objects.all()
    serializer_class = MineralListSerializer

    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, ]
    
    permission_classes = [AllowAny,]
    authentication_classes = []
    
    ordering_fields = ['name',]
    ordering = ['name',]

    filter_backends = [filters.OrderingFilter, DjangoFilterBackend, filters.SearchFilter]
    filterset_class = MineralFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, 'setup_eager_loading'):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        isostructural_minerals = NsFamily.objects.values('ns_family') \
                                                 .annotate(count=Count('minerals')) \
                                                 .filter(ns_family=OuterRef('ns_family'))
        
        relations_count = MineralRelation.objects.values('relation') \
                                                 .filter(Q(direct_relation=True)) \
                                                 .annotate(
                                                     varieties_count=Case(
                                                         When(status__status__status_group__name='varieties', then=Count('relation')),
                                                         default=Value(None)
                                                     ),
                                                     polytypes_count=Case(
                                                        When(status__status__status_group__name='polytypes', then=Count('relation')),
                                                        default=Value(None)
                                                     )
                                                 ) \
                                                 .filter(mineral=OuterRef('id'))
                  
                  
        history_ = MineralHierarchy.objects.values('parent').filter(Q(parent=OuterRef('id'))) \
                                                 .annotate(
                                                     discovery_year_min=Min('mineral__history__discovery_year_min'),
                                                     discovery_year_max=Max('mineral__history__discovery_year_max')
                                                 )                                                                                                         
                            
        is_grouping_ = MineralStatus.objects.filter(Q(mineral=OuterRef('id')) & Q(status__status_group=1))

        queryset = queryset.annotate(is_grouping=Exists(is_grouping_))

        sql, params = queryset.query.sql_with_params()
        queryset_ = Mineral.objects.raw('''
            SELECT * FROM ({ sql }) AS ml;
        ''', params)

        # with connection.cursor() as cursor:
        #     cursor.execute('''
        #         SELECT ml.*,
        #             JSONB_BUILD_OBJECT(
        #             'discovery_year_min', 
        #             CASE WHEN ml.is_grouping
        #                     THEN (
        #                         SELECT MIN(U3."discovery_year_min") AS "discovery_year_min" 
        #                         FROM "mineral_hierarchy" U0 
        #                         INNER JOIN "mineral_log" U2 ON (U0."mineral_id" = U2."id") AND U0."parent_id" = ("ml"."id")
        #                         LEFT OUTER JOIN "mineral_history" U3 ON (U2."id" = U3."mineral_id") 
        #                         GROUP BY U0."parent_id"
        #                         ) 
        #                     ELSE "ml"."discovery_year_min"
        #                 END,
        #                 'discovery_year_max', 
        #                 CASE WHEN ml.is_grouping
        #                     THEN (
        #                         SELECT MAX(U3."discovery_year_max") AS "discovery_year_max" 
        #                         FROM "mineral_hierarchy" U0 
        #                         INNER JOIN "mineral_log" U2 ON (U0."mineral_id" = U2."id") AND U0."parent_id" = ("ml"."id")
        #                         LEFT OUTER JOIN "mineral_history" U3 ON (U2."id" = U3."mineral_id") 
        #                         GROUP BY U0."parent_id"
        #                         ) 
        #                     ELSE "ml"."discovery_year_max" 
        #                 END
        #             ) AS history_
        #         FROM (
        #             ''' + str(queryset.query) +
        #             '''
        #         ) ml;
        #     ''')

        #     rows = cursor.fetch_all()
        #     print(rows)

        queryset = queryset.annotate(
            ns_index_=Case(
                When(
                    ns_class__isnull=False, 
                    then=Concat(
                        'ns_class__id',
                        Value('.'),
                        Coalesce(Right('ns_subclass', 1), Value('0')),
                        Coalesce(Right('ns_family', 1), Value('0')),
                        Value('.'),
                        Coalesce('ns_mineral', Value('0')),
                        output_field=CharField()
                    ),
                ),
                default=None
            ),
            relations_=JSONObject(
                isostructural_minerals=Subquery(isostructural_minerals.values('count')),
                varieties=Subquery(relations_count.values('varieties_count')),
                polytypes=Subquery(relations_count.values('polytypes_count')),
            ),
            history_=JSONObject(
                discovery_year_min=Case(
                    When(is_grouping=True, then=Subquery(history_.values('discovery_year_min'))),
                    default=F('history__discovery_year_min')
                ),
                discovery_year_max=Case(
                        When(is_grouping=True, then=Subquery(history_.values('discovery_year_max'))),
                        default=F('history__discovery_year_max')
                ),
            )
        )
        
        queryset = queryset.defer(
            'history__mineral_id', 'history__discovery_year_min', 'history__discovery_year_max', 'history__discovery_year_note',
            'history__certain', 'history__first_usage_date', 'history__first_known_use', 
            )
        
        return queryset


    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if 'q' in self.request.query_params:
            query = self.request.query_params.get('q', '')
            queryset = queryset.filter(name__unaccent__trigram_word_similar=query)

        return queryset


    def get_serializer_class(self):
        
        if self.action in ['list']:
            return MineralListSerializer

        return super().get_serializer_class()


    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
