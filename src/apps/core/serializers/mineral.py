# -*- coding: UTF-8 -*-
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import connection
from django.db import models
from django.db.models import Max
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import Value
from rest_framework import serializers

from ..models.core import Status
from ..models.mineral import Mineral
from ..models.mineral import MineralCrystallography
from ..models.mineral import MineralFormula
from ..models.mineral import MineralHierarchy
from ..models.mineral import MineralHistory
from ..models.mineral import MineralStructure
from ..queries import GET_INHERITANCE_CHAIN_RETRIEVE_QUERY
from ..serializers.core import StatusListSerializer
from ..utils import add_label
from .core import CountryListSerializer
from .core import FormulaSourceSerializer
from .crystal import CrystalClassSerializer
from .crystal import CrystalSystemSerializer
from .crystal import SpaceGroupSerializer


class MineralHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MineralHistory
        fields = [
            "id",
            "discovery_year",
            "ima_year",
            "publication_year",
            "approval_year",
            "discovery_year_note",
            "first_usage_date",
            "first_known_use",
        ]


class HierarchyParentsHyperlinkSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source="parent", read_only=True)

    name = serializers.StringRelatedField(source="parent")
    url = serializers.HyperlinkedRelatedField(source="parent", read_only=True, view_name="core:mineral-detail")

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
    url = serializers.HyperlinkedRelatedField(source="mineral", read_only=True, view_name="core:mineral-detail")

    class Meta:
        model = MineralHierarchy
        fields = [
            "id",
            "name",
            "url",
        ]


class MineralFormulaSerializer(serializers.ModelSerializer):
    mineral = serializers.PrimaryKeyRelatedField(read_only=True)
    formula = serializers.CharField(source="formula_escape")
    source = FormulaSourceSerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = MineralFormula
        fields = [
            "id",
            "mineral",
            "formula",
            "note",
            "source",
            "show_on_site",
            "created_at",
        ]

    def get_created_at(self, instance):
        return naturalday(instance.created_at)


class MineralFormulaRelatedSerializer(MineralFormulaSerializer):
    mineral = serializers.PrimaryKeyRelatedField(read_only=True)
    from_ = serializers.JSONField(source="from")

    class Meta:
        model = MineralFormula
        fields = MineralFormulaSerializer.Meta.fields + [
            "mineral",
            "from_",
        ]


class MineralCrystallographySerializer(serializers.ModelSerializer):
    mineral = serializers.PrimaryKeyRelatedField(read_only=True)
    crystal_system = CrystalSystemSerializer()
    crystal_class = CrystalClassSerializer()
    space_group = SpaceGroupSerializer()

    class Meta:
        model = MineralCrystallography
        fields = [
            "id",
            "mineral",
            "crystal_system",
            "crystal_class",
            "space_group",
        ]


class MineralCrystallographyRelatedSerializer(serializers.ModelSerializer):
    mineral = serializers.PrimaryKeyRelatedField(read_only=True)
    crystal_system = CrystalSystemSerializer()
    from_ = serializers.JSONField(source="from")

    class Meta:
        model = MineralCrystallography
        fields = [
            "mineral",
            "crystal_system",
            "from_",
        ]


class MineralSmallSerializer(serializers.ModelSerializer):
    status_group = serializers.IntegerField()
    formulas = MineralFormulaSerializer(many=True)
    description = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(lookup_field="slug", view_name="core:mineral-detail")

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "slug",
            "formulas",
            "description",
            "status_group",
            "url",
        ]

    def get_description(self, instance):
        return instance.short_description(100)


class MineralRetrieveSerializer(serializers.ModelSerializer):
    statuses = StatusListSerializer(many=True)
    crystallography = MineralCrystallographySerializer()
    history = MineralHistorySerializer()
    formulas = MineralFormulaSerializer(many=True)
    relations = MineralSmallSerializer(many=True)

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "slug",
            "mindat_id",
            "ns_index",
            "statuses",
            "crystallography",
            "description",
            "is_grouping",
            "seen",
            "history",
            "formulas",
            "relations",
            "created_at",
            "updated_at",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = [
            "history",
            "crystallography__crystal_system",
            "crystallography__crystal_class",
            "crystallography__space_group",
            "ns_class",
            "ns_subclass",
            "ns_family",
        ]

        prefetch_related = [
            models.Prefetch(
                "statuses", Status.objects.select_related("group").extra(where=["mineral_status.direct_status=True"])
            ),
            models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
            models.Prefetch(
                "relations",
                Mineral.objects.prefetch_related("direct_relations", "formulas__source")
                .filter(statuses__group__in=[2, 3], direct_relations__direct_status=True)
                .annotate(status_group=Max("statuses__group"))
                .distinct(),
            ),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def to_representation(self, instance):
        data = super().to_representation(instance)
        _relations = data.pop("relations")
        _ns_relations = []

        if instance.ns_family:
            _ns_related = (
                Mineral.objects.filter(Q(statuses__group=11) & Q(ns_family=instance.ns_family) & ~Q(id=instance.id))
                .prefetch_related("formulas__source")
                .annotate(status_group=Value(11))
                .distinct()
            )
            _ns_related = _ns_related.order_by("name")
            _ns_related = _ns_related.only("name", "slug", "description")
            _ns_relations = MineralSmallSerializer(_ns_related, many=True, context=self.context).data
        _relations = _relations + _ns_relations
        _relations = sorted(_relations, key=lambda x: x["status_group"])

        data["relations"] = _relations

        # calculate inheritance chain only for synonyms [2], varieties [3], and polytypes [4]
        inheritance_chain = []
        if any([status for status in data["statuses"] if status["group"]["id"] in [2, 3, 4]]):
            with connection.cursor() as cursor:
                cursor.execute(GET_INHERITANCE_CHAIN_RETRIEVE_QUERY, [(instance.id,)])
                _inheritance_chain = cursor.fetchall()
                fields = [x[0] for x in cursor.description]
                inheritance_chain = [dict(zip(fields, x)) for x in _inheritance_chain]

        _flat_ids = [x["id"] for x in inheritance_chain]
        _inherited_formulas_data = MineralFormula.objects.filter(mineral__in=_flat_ids).select_related("source")
        _inherited_crystalography_data = (
            MineralCrystallography.objects.filter(mineral__in=_flat_ids)
            .select_related("crystal_system", "crystal_class", "space_group")
            .only("id", "mineral", "crystal_system", "crystal_class", "space_group")
        )
        _inherited_formulas = MineralFormulaSerializer(_inherited_formulas_data, many=True, context=self.context).data
        _inherited_crystalography_data = MineralCrystallographySerializer(
            _inherited_crystalography_data, many=True, context=self.context
        ).data

        for _chain in inheritance_chain:
            _chain["formulas"] = [x for x in _inherited_formulas if x["mineral"] == _chain["id"]]
            _crystallography = [x for x in _inherited_crystalography_data if x["mineral"] == _chain["id"]]
            _chain["crystallography"] = None
            if _crystallography:
                _chain["crystallography"] = _crystallography[0]

        data["inheritance_chain"] = inheritance_chain
        return data


class MineralListSerializer(serializers.ModelSerializer):
    """
    The main serializer for the mineral list view. It serializes the
    data from raw sql query; therefore, it doesn't support prefetching.
    MineralListSecondarySerializer allows injecting prefetched data into this serializer.
    """

    ns_index = serializers.CharField(source="ns_index_")
    description = serializers.CharField(source="short_description")
    is_grouping = serializers.BooleanField()
    seen = serializers.IntegerField()
    updated_at = serializers.SerializerMethodField()

    crystal_systems = serializers.JSONField()
    statuses = serializers.JSONField(source="_statuses")
    relations = serializers.JSONField(source="_relations")
    discovery_countries = serializers.JSONField(source="_discovery_countries")
    history = serializers.JSONField(source="_history")
    links = serializers.SerializerMethodField()
    ordering = serializers.SerializerMethodField()

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "slug",
            "mindat_id",
            "ns_index",
            "ima_symbol",
            "description",
            "is_grouping",
            "seen",
            "updated_at",
            "crystal_systems",
            "statuses",
            "relations",
            "discovery_countries",
            "history",
            "links",
            "ordering",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = [
            # models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
            # models.Prefetch(
            #     "children_hierarchy",
            #     MineralHierarchy.objects.select_related("mineral", "parent").order_by("mineral__statuses__status_id"),
            # ),
            # models.Prefetch(
            #     "parents_hierarchy",
            #     MineralHierarchy.objects.select_related("mineral", "parent").order_by("parent__statuses__status_id"),
            # ),
            # models.Prefetch(
            #     "discovery_countries",
            #     Country.objects.filter(~Q(id=250)),
            # ),
            # models.Prefetch("statuses", Status.objects.select_related("group")),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset

    def get_updated_at(self, instance):
        return naturalday(instance.updated_at)

    def get_discovery_countries(self, instance):
        if instance.is_grouping:
            return instance.discovery_countries_
        return CountryListSerializer(instance.discovery_countries, many=True).data

    def get_links(self, instance):
        links = [
            {
                "name": "RRUFF",
                "display_name": "rruff.info",
                "link": instance.get_rruff_url(),
            },
            {
                "name": "COD",
                "display_name": "Open Crystallography Database",
                "link": instance.get_cod_url(),
            },
            {
                "name": "AMCSD",
                "display_name": "American Mineralogist Crystal Structure Database",
                "link": instance.get_amcsd_url(),
            },
        ]
        mindat_link = instance.get_mindat_url()
        if mindat_link:
            links.append(
                {
                    "name": "Mindat",
                    "display_name": "mindat.org",
                    "link": mindat_link,
                }
            )

        return links

    def get_ordering(self, instance):
        return hasattr(instance, "ordering") and instance.ordering or None


class MineralListSecondarySerializer(serializers.ModelSerializer):
    """
    We're using this serializer for injecting additional data into the
    main serializer of the list view
    """

    formulas = MineralFormulaSerializer(many=True)

    class Meta:
        model = Mineral
        fields = [
            "id",
            "formulas",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []

        prefetch_related = [
            models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
        ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class BaseMineralRelationsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    formula = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "id",
            "name",
            "slug",
            "formula",
        ]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset, request = kwargs.get("queryset"), kwargs.get("request")
        select_related = []
        prefetch_related = [
            Prefetch("formulas", MineralFormula.objects.select_related("source").filter(source=1), to_attr="_formulas"),
        ]
        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset

    def get_formula(self, instance):
        return instance._formulas[0].formula if instance._formulas else None


class MineralRelationsSerializer(BaseMineralRelationsSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = BaseMineralRelationsSerializer.Meta.fields

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset, request = kwargs.get("queryset"), kwargs.get("request")
        select_related = []
        prefetch_related = [
            Prefetch(
                "relation__formulas",
                MineralFormula.objects.select_related("source").filter(source=1),
                to_attr="_formulas",
            ),
        ]
        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)

        return queryset

    def get_formula(self, instance):
        return instance.relation._formulas[0].formula if instance.relation._formulas else None


class MineralAnalyticalDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MineralStructure
        fields = [
            "id",
            "a",
            "b",
            "c",
            "alpha",
            "beta",
            "gamma",
            "volume",
            "space_group",
            "formula",
            "calculated_formula",
            "note",
            "links",
            "reference",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["a"] = add_label(data["a"], instance.a_sigma, "Å")
        data["b"] = add_label(data["b"], instance.b_sigma, "Å")
        data["c"] = add_label(data["c"], instance.c_sigma, "Å")
        data["alpha"] = add_label(data["alpha"], instance.alpha_sigma, "°")
        data["beta"] = add_label(data["beta"], instance.beta_sigma, "°")
        data["gamma"] = add_label(data["gamma"], instance.gamma_sigma, "°")
        data["volume"] = add_label(data["volume"], instance.volume_sigma, "Å³")

        return data
