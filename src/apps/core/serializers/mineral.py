# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q, Count, F, OuterRef, Subquery, Value, Case, When
from django.db.models.functions import JSONObject
from rest_framework import serializers

from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral, MineralStatus, MineralHistory, MineralCrystallography, MineralHierarchy, MineralIonPosition
from ..models.ion import IonPosition, Ion
from .core import StatusListSerializer, CountryListSerializer
from .crystal import CrystalSystemSerializer, CrystalSystemsStatsSerializer
from .base import BaseSerializer
from .ion import MineralIonPositionSerializer, IonPrimitiveSerializer


class MineralHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = MineralHistory
        fields = [
            'id',
            
            'discovery_year',
            'discovery_year_note',
            'first_usage_date',
            'first_known_use',
            ]    



class HierarchyHyperlinkSerializer(serializers.ModelSerializer):

    name = serializers.StringRelatedField(source='parent')
    url = serializers.HyperlinkedRelatedField(
        source='parent',
        read_only=True,
        view_name='core:mineral-detail'
        )

    class Meta:
        model = MineralHierarchy
        fields = [
            'name',
            'url',
        ]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        return output



class MineralRawListSerializer(serializers.ModelSerializer):

    url = serializers.URLField(source='get_absolute_url')
    ns_index = serializers.CharField(source='ns_index_')
    formula = serializers.CharField(source='formula_html')
    is_grouping = serializers.BooleanField()

    hierarchy = serializers.JSONField(source='hierarchy_')
    
    crystal_systems = serializers.JSONField(source='crystal_systems_')
    ions = serializers.JSONField(source='ions_')

    statuses = serializers.JSONField(source='statuses_')
    colors = serializers.JSONField(source='colors_')
    relations = serializers.JSONField(source='relations_')
    discovery_countries = serializers.JSONField(source='discovery_countries_')
    history = serializers.JSONField(source='history_')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'url',
            'ns_index',
            'formula',
            'is_grouping',

            'hierarchy',
            
            'ions',
            'crystal_systems',
            'colors',
            
            'statuses',
            'relations',
            'discovery_countries',
            'history'
            ]



class MineralListSerializer(serializers.ModelSerializer):

    ns_index = serializers.CharField(source='ns_index_')
    formula = serializers.CharField(source='formula_html')
    statuses = StatusListSerializer(many=True)
    ions = serializers.SerializerMethodField()
    crystal_systems = serializers.SerializerMethodField()

    groups = HierarchyHyperlinkSerializer(source='parents_hierarchy', many=True)

    # statuses = serializers.JSONField(source='statuses_')
    # crystal_systems = serializers.JSONField(source='crystal_systems_')
    # colors = serializers.JSONField(source='colors_')
    # relations = serializers.JSONField(source='relations_')
    # discovery_countries = serializers.JSONField(source='discovery_countries_')
    # history = serializers.JSONField(source='history_')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'ns_index',
            'formula',
            'statuses',
            'ions',
            'crystal_systems',
            'groups',
            # 'colors',
            
            # 'relations',
            # 'discovery_countries',
            # 'history'
            ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get('queryset')
        request = kwargs.get('request')

        select_related = [
            'history',
        ]

        prefetch_related = [
            models.Prefetch('statuses', Status.objects.select_related('status_group')),
            models.Prefetch('crystal_systems', CrystalSystem.objects.all().distinct()),
            # models.Prefetch('crystal_systems', CrystalSystem.objects.filter(Q(minerals__mineral__parents_hierarchy__parent__in=queryset.values('id'))),
            #                 to_attr='crystal_system_counts'
            #                 ),
            # models.Prefetch('crystallography', MineralCrystallography.objects.filter(Q(mineral__parents_hierarchy__parent__in=queryset.values('id')) | 
            #                                                                          Q(mineral__in=queryset.values('id'))) \
            #                                                                  .select_related('crystal_system') \
            #                                                                  .defer('crystal_class', 'space_group', 'a', 'b', 'c', 'alpha', 'gamma', 'z'),
            #                                                                  to_attr='crystal_system_counts'
            #                                                                  ),

            models.Prefetch('parents_hierarchy', MineralHierarchy.objects.select_related('parent', 'mineral')),

            models.Prefetch('ions', MineralIonPosition.objects.select_related('ion', 'position').order_by('position', 'ion__formula'), to_attr='positions'),
            'discovery_countries',
        ]
        
        for query_param in request.query_params.keys(): 
            
            if query_param in ['anions', 'cations', 'silicates', 'other_compounds']:
                prefetch_related.append('ions_theoretical')

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


    def get_ions(self, instance):
        output = MineralIonPositionSerializer(instance.positions, many=True).data
        
        output_ = []
        positions_ = []
        
        for ion in output:
            position_ = ion['position']
            if position_['id'] not in positions_:
                positions_.append(position_['id'])
                output_.append({
                    'position': position_,
                    'ions': [ion_['ion'] for ion_ in output if ion_['position']['id'] == position_['id']]
                })

        return output_


    def get_crystal_systems(self, instance):
        if instance.is_grouping:
            # crystal_systems = MineralCrystallography.objects.all().values('crystal_system') \
            #                                                       .filter(Q(mineral__parents_hierarchy__parent=instance.id)) \
            #                                                       .annotate(
            #                                                         id=F('crystal_system__id'),
            #                                                         name=F('crystal_system__name'),
            #                                                         counts=Count('mineral', distinct=True)
            #                                                       )
            crystal_systems = instance.children_hierarchy.select_related('mineral').values('mineral__crystal_systems') \
                                                                  .annotate(
                                                                    id=F('mineral__crystal_systems__id'),
                                                                    name=F('mineral__crystal_systems__name'),
                                                                    counts=Count('mineral', distinct=True)
                                                                  )
            # crystal_systems = MineralHierarchy.objects.values('mineral__crystal_systems') \
            #                                     .filter(parent=instance.id) \
            #                                     .annotate(
            #                                         id=F('mineral__crystal_systems__id'),
            #                                         name=F('mineral__crystal_systems__name'),
            #                                         counts=Count('mineral', distinct=True)
            #                                     )
            
            return crystal_systems.values('id', 'name', 'counts')
        return CrystalSystemSerializer(instance.crystal_systems, many=True).data
