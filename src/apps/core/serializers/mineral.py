# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Q, Count, F
from django.contrib.postgres.aggregates import ArrayAgg
from rest_framework import serializers

from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral, MineralStatus, MineralHistory, MineralCrystallography, MineralHierarchy, MineralIonPosition
from .core import StatusListSerializer, CountryListSerializer
from .crystal import CrystalSystemSerializer, CrystalSystemsStatsSerializer
from .base import BaseSerializer


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



class MineralListSerializer(serializers.ModelSerializer):

    ns_index = serializers.CharField(source='ns_index_')
    formula = serializers.CharField(source='formula_html')
    ions = serializers.JSONField(source='ions_')
    # crystal_systems = serializers.SerializerMethodField()

    statuses = serializers.JSONField(source='statuses_')
    # relations = serializers.JSONField(source='relations_')
    discovery_countries = serializers.JSONField(source='discovery_countries_')
    history = serializers.JSONField(source='history_')

    class Meta:
        model = Mineral
        fields = [
            'id',
            
            'name',
            'ns_index',
            'formula',
            'ions',
            # 'crystal_systems',
            
            'statuses',
            # 'relations',
            'discovery_countries',
            'history'
            ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get('queryset')
        request = kwargs.get('request')

        select_related = [
            'history',
        ]

        prefetch_related = [
            # models.Prefetch('statuses', Status.objects.select_related('status_group')),
            # models.Prefetch('crystal_systems', CrystalSystem.objects.all().distinct()),
            # 'discovery_countries',
        ]
        
        for query_param in request.query_params.keys():
            
            if query_param in ['anions', 'cations', 'silicates', 'other_compounds']:
                prefetch_related.append('ions_theoretical')

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


    def get_crystal_systems(self, instance):
        if instance.is_grouping:
            return instance.crystal_systems_
        return CrystalSystemSerializer(instance.crystal_systems, many=True).data