# -*- coding: UTF-8 -*-
from django.db import models
from django.db.models import Count
from django.db.models import F
from rest_framework import serializers

from ..models.core import Status
from ..models.crystal import CrystalSystem
from ..models.mineral import Mineral
from ..models.mineral import MineralFormula
from ..models.mineral import MineralHierarchy
from ..models.mineral import MineralHistory
from ..models.mineral import MineralIonPosition
from .core import FormulaSourceSerializer
from .crystal import CrystalSystemSerializer
from .ion import MineralIonPositionSerializer


class MineralHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MineralHistory
        fields = [
            "id",
            "discovery_year",
            "discovery_year_note",
            "first_usage_date",
            "first_known_use",
        ]


class HierarchyParentsHyperlinkSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(source="parent", read_only=True)

    name = serializers.StringRelatedField(source="parent")
    url = serializers.HyperlinkedRelatedField(
        source="parent", read_only=True, view_name="core:mineral-detail"
    )

    class Meta:
        model = MineralHierarchy
        fields = [
            "id",
            "name",
            "url",
        ]


class HierarchyChildrenHyperlinkSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(source="mineral", read_only=True)

    name = serializers.StringRelatedField(source="mineral")
    url = serializers.HyperlinkedRelatedField(
        source="mineral", read_only=True, view_name="core:mineral-detail"
    )

    class Meta:
        model = MineralHierarchy
        fields = [
            "id",
            "name",
            "url",
        ]


class MineralFormulaSerializer(serializers.ModelSerializer):

    formula = serializers.CharField()
    note = serializers.CharField()
    source = FormulaSourceSerializer()
    created_at = serializers.DjangoModelField()

    class Meta:
        model = MineralFormula
        fields = [
            "formula",
            "note",
            "source",
            "created_at",
        ]


class MineralRetrieveSerializer(serializers.ModelSerializer):

    ns_index = serializers.CharField(source="ns_index_")
    formula = serializers.CharField(source="formula_html")
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()

    hierarchy = serializers.SerializerMethodField()
    # hierarchy = HierarchyChildrenHyperlinkSerializer(source='children_hierarchy', many=True)

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "ns_index",
            "formula",
            "is_grouping",
            "seen",
            "hierarchy",
            # 'ions',
            # 'crystal_systems',
            # 'colors',
            # 'statuses',
            # 'relations',
            # 'discovery_countries',
            # 'history',
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
            "history",
        ]

        prefetch_related = [
            models.Prefetch("statuses", Status.objects.select_related("status_group")),
            models.Prefetch("crystal_systems", CrystalSystem.objects.all().distinct()),
            # models.Prefetch('crystal_systems', CrystalSystem.objects.filter(Q(minerals__mineral__parents_hierarchy__parent__in=queryset.values('id'))),
            #                 to_attr='crystal_system_counts'
            #                 ),
            # models.Prefetch('crystallography', MineralCrystallography.objects.filter(Q(mineral__parents_hierarchy__parent__in=queryset.values('id')) |
            #                                                                          Q(mineral__in=queryset.values('id'))) \
            #                                                                  .select_related('crystal_system') \
            #                                                                  .defer('crystal_class', 'space_group', 'a', 'b', 'c', 'alpha', 'gamma', 'z'),
            #                                                                  to_attr='crystal_system_counts'
            #                                                                  ),
            models.Prefetch(
                "parents_hierarchy",
                MineralHierarchy.objects.select_related("parent", "mineral"),
            ),
            models.Prefetch(
                "ions",
                MineralIonPosition.objects.select_related("ion", "position").order_by(
                    "position", "ion__formula"
                ),
                to_attr="positions",
            ),
            "discovery_countries",
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_hierarchy(self, instance):
        if instance.is_grouping:
            return HierarchyChildrenHyperlinkSerializer(
                instance.children_hierarchy, context=self.context, many=True
            ).data
        return HierarchyParentsHyperlinkSerializer(
            instance.parents_hierarchy, context=self.context, many=True
        ).data


class MineralListSerializer(serializers.ModelSerializer):

    url = serializers.URLField(source="get_absolute_url")
    ns_index = serializers.CharField(source="ns_index_")
    formulas = MineralFormulaSerializer(many=True)
    description = serializers.CharField()
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()

    hierarchy = serializers.JSONField(source="hierarchy_")
    ions = serializers.JSONField(source="ions_")
    crystal_systems = serializers.JSONField(source="crystal_systems_")
    statuses = serializers.JSONField(source="statuses_")
    relations = serializers.JSONField(source="relations_")
    discovery_countries = serializers.JSONField(source="discovery_countries_")
    history = serializers.JSONField(source="history_")

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "url",
            "ns_index",
            "formulas",
            "description",
            "is_grouping",
            "seen",
            "hierarchy",
            "ions",
            "crystal_systems",
            "statuses",
            "relations",
            "discovery_countries",
            "history",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = ["formulas__source"]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_ions(self, instance):
        output = MineralIonPositionSerializer(instance.positions, many=True).data

        output_ = []
        positions_ = []

        for ion in output:
            position_ = ion["position"]
            if position_["id"] not in positions_:
                positions_.append(position_["id"])
                output_.append(
                    {
                        "position": position_,
                        "ions": [
                            ion_["ion"]
                            for ion_ in output
                            if ion_["position"]["id"] == position_["id"]
                        ],
                    }
                )

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
            crystal_systems = (
                instance.children_hierarchy.select_related("mineral")
                .values("mineral__crystal_systems")
                .annotate(
                    id=F("mineral__crystal_systems__id"),
                    name=F("mineral__crystal_systems__name"),
                    counts=Count("mineral", distinct=True),
                )
            )
            # crystal_systems = MineralHierarchy.objects.values('mineral__crystal_systems') \
            #                                     .filter(parent=instance.id) \
            #                                     .annotate(
            #                                         id=F('mineral__crystal_systems__id'),
            #                                         name=F('mineral__crystal_systems__name'),
            #                                         counts=Count('mineral', distinct=True)
            #                                     )

            return crystal_systems.values("id", "name", "counts")
        return CrystalSystemSerializer(instance.crystal_systems, many=True).data
