from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import  AllowAny

from .models.core import Status, NsFamily
from .models.mineral import Mineral, MineralRelation
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

        varieties_count = MineralRelation.objects.values('relation') \
                                                 .filter(models.Q(direct_relation=True) & models.Q(status__status__status_group__name='varieties')) \
                                                 .annotate(count=models.Count('relation')) \
                                                 .filter(mineral=models.OuterRef('id'))
                                                
        polytypes_count = MineralRelation.objects.values('relation') \
                                                 .filter(models.Q(direct_relation=True) & models.Q(status__status__status_group__name='polytypes')) \
                                                 .annotate(count=models.Count('relation')) \
                                                 .filter(mineral=models.OuterRef('id'))

        queryset = queryset.annotate(
            isostructural_minerals_count=models.Subquery(isostructural_minerals.values('count')),
            varieties_count=models.Subquery(varieties_count.values('count')),
            polytypes_count=models.Subquery(polytypes_count.values('count'))
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
