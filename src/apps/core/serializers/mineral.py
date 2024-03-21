# -*- coding: UTF-8 -*-
from django.contrib.humanize.templatetags.humanize import naturalday
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import connection
from django.db import models
from django.db.models import Prefetch
from rest_framework import serializers

from ..annotations import _annotate__statuses_array
from ..choices import INHERIT_CRYSTAL_SYSTEM
from ..models.core import Status
from ..models.mineral import Mineral
from ..models.mineral import MineralContext
from ..models.mineral import MineralCrystallography
from ..models.mineral import MineralFormula
from ..models.mineral import MineralHistory
from ..models.mineral import MineralInheritance
from ..models.mineral import MineralStatus
from ..models.mineral import MineralStructure
from ..queries import GET_DATA_CONTEXTS_QUERY
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


class FormulaSerializer(serializers.ModelSerializer):
    formula = serializers.CharField(source="formula_escape")
    source = FormulaSourceSerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = MineralFormula
        fields = [
            "id",
            "formula",
            "note",
            "source",
            "show_on_site",
            "created_at",
        ]

    def get_created_at(self, instance):
        return naturalday(instance.created_at)


class MineralContextSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()

    class Meta:
        model = MineralContext
        fields = [
            "context",
            "data",
        ]


class MineralListInheritanceSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source="inherit_from", read_only=True)
    mindat_id = serializers.IntegerField(source="inherit_from.mindat_id")
    name = serializers.StringRelatedField(source="inherit_from")
    slug = serializers.SlugRelatedField(source="inherit_from", read_only=True, slug_field="slug")
    statuses = serializers.JSONField()

    formulas = FormulaSerializer(source="inherit_from.formulas", many=True)
    crystallography = CrystalSystemSerializer(source="inherit_from.crystallography.crystal_system")

    class Meta:
        model = MineralInheritance
        fields = [
            "id",
            "mindat_id",
            "name",
            "slug",
            "statuses",
            "prop",
            "formulas",
            "crystallography",
        ]


class CrystallographySerializer(serializers.ModelSerializer):
    crystal_system = CrystalSystemSerializer()
    crystal_class = CrystalClassSerializer()
    space_group = SpaceGroupSerializer()

    class Meta:
        model = MineralCrystallography
        fields = [
            "id",
            "crystal_system",
            "crystal_class",
            "space_group",
        ]


class MineralRetrieveInheritanceSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source="inherit_from", read_only=True)
    mindat_id = serializers.IntegerField(source="inherit_from.mindat_id")
    name = serializers.StringRelatedField(source="inherit_from")
    slug = serializers.SlugRelatedField(source="inherit_from", read_only=True, slug_field="slug")
    statuses = serializers.JSONField()

    contexts = MineralContextSerializer(source="inherit_from.contexts", many=True)
    crystallography = CrystallographySerializer(source="inherit_from.crystallography")
    formulas = FormulaSerializer(source="inherit_from.formulas", many=True)

    class Meta:
        model = MineralInheritance
        fields = [
            "id",
            "mindat_id",
            "name",
            "slug",
            "statuses",
            "prop",
            "contexts",
            "crystallography",
            "formulas",
        ]


class RetrieveController(serializers.Serializer):
    """
    Controller, which redirects the request to the appropriate serializer - grouping or mineral
    """

    def to_representation(self, instance):
        if instance.is_grouping:
            return GroupingRetrieveSerializer(instance, context=self.context).data
        return MineralRetrieveSerializer(instance, context=self.context).data

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset, is_grouping = kwargs.get("queryset"), kwargs.get("is_grouping")

        select_related = []
        prefetch_related = [
            models.Prefetch(
                "statuses", Status.objects.select_related("group").extra(where=["mineral_status.direct_status = TRUE"])
            ),
            models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
        ]

        if not is_grouping:
            _iherited_ids = MineralInheritance.objects.filter(mineral__in=queryset).distinct("inherit_from")
            select_related += [
                "crystallography__crystal_system",
                "crystallography__crystal_class",
                "crystallography__space_group",
                "ns_class",
                "ns_subclass",
                "ns_family",
            ]
            prefetch_related += [
                "contexts",
                models.Prefetch(
                    "inheritance_chain",
                    MineralInheritance.objects.filter(id__in=_iherited_ids)
                    .annotate(statuses=ArrayAgg("inherit_from__statuses__status_id"))
                    .extra(where=["mineral_status.direct_status = TRUE"])
                    .select_related("inherit_from")
                    .prefetch_related(
                        "inherit_from__formulas__source",
                        "inherit_from__crystallography__crystal_system",
                        "inherit_from__crystallography__crystal_class",
                        "inherit_from__crystallography__space_group",
                        "inherit_from__contexts",
                    ),
                ),
            ]

        queryset = queryset.select_related(*select_related).prefetch_related(*prefetch_related)
        return queryset


class BaseRetrieveSerializer(serializers.ModelSerializer):
    is_grouping = serializers.BooleanField()
    statuses = StatusListSerializer(many=True)
    formulas = FormulaSerializer(many=True)

    structures = serializers.SerializerMethodField()
    elements = serializers.SerializerMethodField()

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "slug",
            "is_grouping",
            "description",
            "mindat_id",
            "statuses",
            "description",
            "seen",
            "formulas",
            "structures",
            "elements",
            "contexts",
            "created_at",
            "updated_at",
        ]

    @property
    def _relations(self):
        """
        This property should be set in the `to_representation` method of the serializer.
        """
        return getattr(self.instance, "_relations", None)

    def get_structures(self, instance):
        ids = self._relations
        if ids:
            return MineralStructure.aggregate_by_system(ids)
        return None

    def get_elements(self, instance):
        ids = self._relations
        if ids:
            return MineralStructure.aggregate_by_element(ids)
        return None


class GroupMemberSerializer(serializers.ModelSerializer):
    history = MineralHistorySerializer()
    statuses = serializers.JSONField(source="_statuses")
    crystal_system = serializers.IntegerField()
    description = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(lookup_field="slug", view_name="core:mineral-detail")

    class Meta:
        model = Mineral
        fields = [
            "id",
            "name",
            "slug",
            "statuses",
            "crystal_system",
            "history",
            "description",
            "url",
        ]

    @staticmethod
    def get_description(instance):
        return instance.short_description(100)


class GroupingRetrieveSerializer(BaseRetrieveSerializer):
    members = serializers.SerializerMethodField()
    contexts = serializers.SerializerMethodField()

    class Meta:
        model = Mineral
        fields = BaseRetrieveSerializer.Meta.fields + [
            "members",
        ]

    def get_members(self, instance):
        _members = instance.members
        _select_related = [
            "history",
        ]
        _prefetch_related = []
        _only = [
            "id",
            "name",
            "slug",
            "description",
        ]

        _minerals = (
            Mineral.objects.filter(id__in=_members)
            .annotate(
                crystal_system=models.Case(
                    models.When(
                        inheritance_chain__prop=INHERIT_CRYSTAL_SYSTEM,
                        then=models.F("inheritance_chain__inherit_from__crystallography__crystal_system"),
                    ),
                    models.When(crystallography__isnull=False, then=models.F("crystallography__crystal_system")),
                    default=None,
                    output_field=models.IntegerField(),
                )
            )
            .select_related(*_select_related)
            .prefetch_related(*_prefetch_related)
            .only(*_only)
        )
        _minerals = _annotate__statuses_array(_minerals)
        data = GroupMemberSerializer(_minerals, many=True, context=self.context).data
        return data

    @staticmethod
    def get_contexts(instance):
        _contexts = []
        with connection.cursor() as cursor:
            cursor.execute(GET_DATA_CONTEXTS_QUERY, [tuple(instance._relations)])
            _contexts = cursor.fetchall()
            _contexts = [x for y in _contexts for x in y]
        return _contexts

    def get_structures(self, instance):
        ids = self._relations
        if ids:
            # if item inherits crystal system, we substitute the ids with the inherited ones if present.
            # If it's not present, we just keep the original id.
            _inheritance_chain = MineralInheritance.get_redirect_ids(ids, INHERIT_CRYSTAL_SYSTEM)
            _inheritance_ids = [x["mineral"] for x in _inheritance_chain]
            ids = [
                x if x not in _inheritance_ids else _inheritance_chain[_inheritance_ids.index(x)]["inherit_from"]
                for x in ids
            ]
            return MineralStructure.aggregate_by_system(ids)
        return None

    def to_representation(self, instance):
        _members = instance.members
        _members_synonyms = MineralStatus.get_synonyms(_members)
        instance._relations = [instance.id, *(instance.synonyms + _members + _members_synonyms)]
        return super().to_representation(instance)


class MineralSmallSerializer(serializers.ModelSerializer):
    depth = serializers.IntegerField()
    statuses = serializers.JSONField(source="_statuses")
    formulas = FormulaSerializer(many=True)
    crystallography = CrystallographySerializer()
    contexts = MineralContextSerializer(many=True)

    class Meta:
        model = Mineral
        fields = [
            "id",
            "mindat_id",
            "name",
            "slug",
            "depth",
            "statuses",
            "formulas",
            "crystallography",
            "contexts",
        ]


class MineralRetrieveSerializer(BaseRetrieveSerializer):
    crystallography = CrystallographySerializer()
    history = MineralHistorySerializer()
    contexts = MineralContextSerializer(many=True)
    inheritance_chain = MineralRetrieveInheritanceSerializer(many=True)

    class Meta:
        model = Mineral
        fields = BaseRetrieveSerializer.Meta.fields + [
            "crystallography",
            "ns_index",
            "history",
            "inheritance_chain",
        ]

    def to_representation(self, instance):
        instance._relations = [instance.id, *instance.synonyms]
        return super().to_representation(instance)


class MineralListSerializer(serializers.ModelSerializer):
    """
    The main serializer for the mineral list view. It serializes the
    data from raw sql query; therefore, it doesn't support prefetching.
    MineralListSecondarySerializer allows injecting prefetched data into this serializer.
    """

    ns_index = serializers.CharField(source="ns_index_")
    description = serializers.CharField(source="short_description")
    is_grouping = serializers.BooleanField(source="_is_grouping")
    seen = serializers.IntegerField()
    updated_at = serializers.SerializerMethodField()

    crystallography = serializers.JSONField(source="crystal_systems")
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
            "crystallography",
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
        prefetch_related = []

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

    formulas = FormulaSerializer(many=True)
    inheritance_chain = MineralListInheritanceSerializer(many=True)
    ima_statuses = serializers.SerializerMethodField()
    ima_notes = serializers.SerializerMethodField()

    class Meta:
        model = Mineral
        fields = [
            "id",
            "formulas",
            "ima_statuses",
            "ima_notes",
            "inheritance_chain",
        ]

    def get_ima_statuses(self, instance):
        return [x.get_status_display() for x in instance.ima_statuses.all()]

    def get_ima_notes(self, instance):
        return [x.get_note_display() for x in instance.ima_notes.all()]

    @staticmethod
    def setup_eager_loading(**kwargs):
        queryset = kwargs.get("queryset")

        select_related = []
        prefetch_related = [
            models.Prefetch("formulas", MineralFormula.objects.select_related("source")),
            models.Prefetch(
                "inheritance_chain",
                MineralInheritance.objects.annotate(statuses=ArrayAgg("inherit_from__statuses__status_id"))
                .extra(where=["mineral_status.direct_status = TRUE"])
                .select_related("inherit_from")
                .prefetch_related(
                    "inherit_from__statuses",
                    "inherit_from__formulas__source",
                    "inherit_from__crystallography__crystal_system",
                ),
            ),
            "ima_statuses",
            "ima_notes",
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
