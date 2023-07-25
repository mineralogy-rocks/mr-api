# -*- coding: UTF-8 -*-
from django.db.models import Prefetch
from rest_framework import serializers

from ..models.core import Country
from ..models.core import FormulaSource
from ..models.core import NsClass
from ..models.core import NsFamily
from ..models.core import NsSubclass
from ..models.core import RelationType
from ..models.core import Status
from ..models.core import StatusGroup


class StatusGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusGroup
        fields = [
            "id",
            "name",
        ]


class StatusListSerializer(serializers.ModelSerializer):
    group = StatusGroupSerializer()

    class Meta:
        model = Status
        fields = [
            "status_id",
            "group",
            "description_short",
            "description_long",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
            "group",
        ]

        queryset = queryset.select_related(*select_related)
        return queryset



class CountryListSerializer(serializers.ModelSerializer):
    iso_code = serializers.CharField(source="alpha_2")

    class Meta:
        model = Country
        fields = [
            "id",
            "name",
            "region",
            "iso_code",
        ]


class CountsFieldMixin(object):
    def get_counts(self, obj):
        if hasattr(obj, "minerals"):
            return obj.minerals.count()
        else:
            return None


class NsFamilyListSerializer(CountsFieldMixin, serializers.ModelSerializer):
    counts = serializers.SerializerMethodField()

    class Meta:
        model = NsFamily
        fields = [
            "id",
            "ns_family",
            "description",
            "counts",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = [
            "minerals",
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class NsSubclassListSerializer(CountsFieldMixin, serializers.ModelSerializer):
    counts = serializers.SerializerMethodField()

    class Meta:
        model = NsSubclass
        fields = [
            "id",
            "ns_subclass",
            "description",
            "counts",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = [
            "minerals",
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class NsSubclassFamilyListSerializer(NsSubclassListSerializer):
    families = NsFamilyListSerializer(many=True)

    class Meta:
        model = NsSubclass
        fields = NsSubclassListSerializer.Meta.fields + ["families"]


class NsClassSubclassFamilyListSerializer(CountsFieldMixin, serializers.ModelSerializer):
    counts = serializers.SerializerMethodField()
    subclasses = NsSubclassFamilyListSerializer(many=True)

    class Meta:
        model = NsClass
        fields = ["id", "description", "counts", "subclasses"]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = [
            "minerals",
            Prefetch(
                "subclasses",
                NsSubclass.objects.prefetch_related("minerals", "families__minerals"),
            ),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class RelationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationType
        fields = ["type", "note"]


class FormulaSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormulaSource
        fields = [
            "id",
            "name",
            "url",
        ]
