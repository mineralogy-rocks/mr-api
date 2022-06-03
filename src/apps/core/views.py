from django.db import models
from django.db.models.functions import JSONObject, Concat, Right, Coalesce
from django.contrib.postgres.aggregates import ArrayAgg
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import  AllowAny

from .models.core import Status, StatusGroup, NsFamily
from .models.mineral import Mineral, MineralRelation, MineralHierarchy
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
                                                 .annotate(count=models.Count('minerals')) \
                                                 .filter(ns_family=models.OuterRef('ns_family'))
        
        relations_count = MineralRelation.objects.values('relation') \
                                                 .filter(models.Q(direct_relation=True)) \
                                                 .annotate(
                                                     varieties_count=models.Case(
                                                         models.When(status__status__status_group__name='varieties', then=models.Count('relation')),
                                                         default=models.Value(None)
                                                     ),
                                                     polytypes_count=models.Case(
                                                        models.When(status__status__status_group__name='polytypes', then=models.Count('relation')),
                                                        default=models.Value(None)
                                                     )
                                                 ) \
                                                 .filter(mineral=models.OuterRef('id'))

        groups_history = MineralHierarchy.objects.values('parent').filter(models.Q(parent=models.OuterRef('id'))) \
                                                 .annotate(
                                                     discovery_year_min=models.Min('mineral__history__discovery_year_min'),
                                                     discovery_year_max=models.Max('mineral__history__discovery_year_max')
                                                 )
                                                 
        status_groups_ = queryset.values('id').annotate(status_groups=ArrayAgg('statuses__status_group', default=models.Value([])))
        
        print(status_groups_)

        queryset = queryset.annotate(
            # status_groups_=models.Subquery(status_groups_.values('status_groups')),
            ns_index_=models.Case(
                models.When(
                    ns_class__isnull=False, 
                    then=Concat(
                        'ns_class__id',
                        models.Value('.'),
                        Coalesce(Right('ns_subclass', 1), models.Value('0')),
                        Coalesce(Right('ns_family', 1), models.Value('0')),
                        models.Value('.'),
                        Coalesce('ns_mineral', models.Value('0')),
                        output_field=models.CharField()
                    ),
                ),
                default=None
            ),
            relations_=JSONObject(
                isostructural_minerals=models.Subquery(isostructural_minerals.values('count')),
                varieties=models.Subquery(relations_count.values('varieties_count')),
                polytypes=models.Subquery(relations_count.values('polytypes_count')),
            ),
            history_=JSONObject(
                discovery_year_min=models.Case(
                    models.When(statuses__status_group__name='grouping', then=models.Subquery(groups_history.values('discovery_year_min'))),
                    default=models.F('history__discovery_year_min')
                ),
                discovery_year_max=models.Case(
                        models.When(statuses__status_group__name='grouping', then=models.Subquery(groups_history.values('discovery_year_max'))),
                        default=models.F('history__discovery_year_max')
                ),
            )
        )
        
        queryset = queryset.defer(
            'history__mineral_id', 'history__discovery_year_min', 'history__discovery_year_max', 'history__discovery_year_note',
            'history__certain', 'history__first_usage_date', 'history__first_known_use', 
            
            'crystal__crystal_class_id', 'crystal__space_group_id','crystal__a', 'crystal__b', 'crystal__c', 'crystal__alpha', 
            'crystal__gamma', 'crystal__z',
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
