# -*- coding: UTF-8 -*-
from django.db import connection
from django.db.models import Q, OuterRef, F, Subquery, Min, Max, Value, Case, When, Count, Exists, CharField, JSONField
from django.db.models.functions import JSONObject, Concat, Right, Coalesce
from django.contrib.postgres.aggregates import JSONBAgg, ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import  AllowAny

from .pagination import CustomLimitOffsetPagination
from .models.core import Status, NsFamily
from .models.crystal import CrystalSystem
from .models.mineral import Mineral, MineralRelation, MineralHierarchy, MineralCrystallography, MineralStatus, MineralIonPosition
from .serializers.core import StatusListSerializer
from .serializers.mineral import MineralListSerializer
from .filters import StatusFilter, MineralFilter
from .utils import dictfetchall


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
    pagination_class = CustomLimitOffsetPagination
    
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

        isostructural_minerals_ = NsFamily.objects.values('ns_family') \
                                                  .annotate(count=Count('minerals')) \
                                                  .filter(ns_family=OuterRef('ns_family'))
        
        relations_count_ = MineralRelation.objects.values('relation') \
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
                  
                  
        history_ = MineralHierarchy.objects.values('parent') \
                                           .filter(Q(parent=OuterRef('id'))) \
                                           .annotate(
                                             discovery_year_min=Min('mineral__history__discovery_year_min'),
                                             discovery_year_max=Max('mineral__history__discovery_year_max')
                                           )                                                                                                         
                      
        ions_ = MineralIonPosition.objects.all().values('position') \
                                                .filter(Q(mineral=OuterRef('id'))) \
                                                .annotate(
                                                    ions_= JSONObject(
                                                        id=F('position__id'),
                                                        name=F('position__name'),
                                                        ions=ArrayAgg('ion__formula')
                                                    )
                                                ).order_by('position__name')
                                                          
        crystal_systems_ = MineralCrystallography.objects.all().values('crystal_system') \
                                                               .filter(Q(mineral__parents_hierarchy__parent=OuterRef('id'))) \
                                                               .annotate(
                                                                   crystal_systems_=JSONObject(
                                                                        id=F('crystal_system__id'),
                                                                        name=F('crystal_system__name'),
                                                                        count=Count('mineral', distinct=True)
                                                                   )
                                                               )
                    
        is_grouping_ = MineralStatus.objects.filter(Q(mineral=OuterRef('id')) & Q(status__status_group=1))   
        
        queryset = queryset.annotate(
            is_grouping=Exists(is_grouping_),
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
            id_=F('id'),
        )

        # queryset = queryset.annotate(
        #                         ions_=Case(
        #                             When(is_grouping=True, then=ArraySubquery(ions_.values('ions_'))),
        #                             default=[]
        #                         ),
        #                         crystal_systems_=ArraySubquery(crystal_systems_.values('crystal_systems_')),
        #                         relations_=JSONObject(
        #                             isostructural_minerals=Subquery(isostructural_minerals_.values('count')),
        #                             varieties=Subquery(relations_count_.values('varieties_count')),
        #                             polytypes=Subquery(relations_count_.values('polytypes_count')),
        #                         ),
        #                         history_=JSONObject(
        #                             discovery_year_min=Case(
        #                                 When(is_grouping=True, then=Subquery(history_.values('discovery_year_min'))),
        #                                 default=F('history__discovery_year_min')
        #                             ),
        #                             discovery_year_max=Case(
        #                                 When(is_grouping=True, then=Subquery(history_.values('discovery_year_max'))),
        #                                 default=F('history__discovery_year_max')
        #                             ),
        #                         )
        #                     )
        
        queryset = queryset.defer(
            'ns_class', 'ns_subclass', 'ns_family', 'ns_mineral', 'note', 'created_at', 'updated_at',
            
            'history__mineral_id', 'history__discovery_year_note', 'history__certain', 'history__first_usage_date', 
            'history__first_known_use', 
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
