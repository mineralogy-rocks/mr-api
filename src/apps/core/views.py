# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
from dal import autocomplete
from django.db.models import Count
from django.db.models import F
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.authentication import JWTAuthentication

from .annotations import _annotate__is_grouping
from .annotations import _annotate__ns_index
from .choices import INHERIT_CRYSTAL_SYSTEM
from .filters import MineralFilter
from .filters import NickelStrunzFilter
from .filters import StatusFilter
from .models.core import NsClass
from .models.core import NsFamily
from .models.core import NsSubclass
from .models.core import Status
from .models.mineral import HierarchyView
from .models.mineral import Mineral
from .models.mineral import MineralInheritance
from .models.mineral import MineralRelation
from .models.mineral import MineralStatus
from .models.mineral import MineralStructure
from .pagination import CustomCursorPagination
from .queries import LIST_VIEW_QUERY
from .serializers.core import NsClassSubclassFamilyListSerializer
from .serializers.core import NsFamilyListSerializer
from .serializers.core import NsSubclassListSerializer
from .serializers.core import StatusListSerializer
from .serializers.mineral import BaseMineralRelationsSerializer
from .serializers.mineral import MineralAnalyticalDataSerializer
from .serializers.mineral import MineralListSecondarySerializer
from .serializers.mineral import MineralListSerializer
from .serializers.mineral import MineralRelationsSerializer
from .serializers.mineral import RetrieveController


class MineralSearch(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Mineral.objects.none()

        qs = Mineral.objects.all()

        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q))

        return qs


class StatusViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = Status.objects.all()
    serializer_class = StatusListSerializer

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    ordering_fields = [
        "status_id",
        "group",
    ]
    ordering = [
        "status_id",
    ]

    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "description_short",
        "description_long",
        "group__name",
    ]
    filterset_class = StatusFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        return queryset


class NickelStrunzViewSet(ListModelMixin, GenericViewSet):
    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = NsClass.objects.all()
    serializer_class = NsClassSubclassFamilyListSerializer

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    pagination_class = LimitOffsetPagination

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        "id",
        "description",
        "subclasses__description",
        "families__description",
        "subclasses__ns_subclass",
        "families__ns_family",
    ]
    filterset_class = NickelStrunzFilter

    def _get_paginated_response(self, queryset, serializer):
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(serializer(page, many=True).data)

        return Response(serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def _filter_queryset(self, queryset):
        if "q" in self.request.query_params:
            queryset = queryset.filter(description__icontains=self.request.query_params.get("q", ""))

        if "class" in self.request.query_params:
            queryset = queryset.filter(ns_class=self.request.query_params.get("class", ""))

        if "subclass" in self.request.query_params:
            if self.action in ["subclasses"]:
                queryset = queryset.filter(ns_subclass=self.request.query_params.get("subclass", ""))
            elif self.action in ["families"]:
                queryset = queryset.filter(ns_subclass__ns_subclass=self.request.query_params.get("subclass", ""))
            else:
                pass

        if "family" in self.request.query_params:
            if self.action in ["subclasses"]:
                queryset = queryset.filter(families__ns_family=self.request.query_params.get("family", ""))
            elif self.action in ["families"]:
                queryset = queryset.filter(ns_family=self.request.query_params.get("family", ""))
            else:
                pass
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)

        return queryset

    @action(methods=["get"], detail=False, url_path="classes")
    def classes(self, request, *args, **kwargs):
        queryset = NsClass.objects.annotate(counts=Count("minerals", distinct=True))
        queryset = self.filter_queryset(queryset)
        return Response(queryset.values("id", "description", "counts"), status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_path="subclasses")
    def subclasses(self, request, *args, **kwargs):
        serializer_class = NsSubclassListSerializer
        queryset = (
            NsSubclass.objects.select_related("ns_class")
            .annotate(counts=Count("minerals", distinct=True))
            .order_by("ns_class__id", "ns_subclass")
        )
        queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)
        queryset = self._filter_queryset(queryset)

        return self._get_paginated_response(queryset, serializer_class)

    @action(methods=["get"], detail=False, url_path="families")
    def families(self, request, *args, **kwargs):
        serializer_class = NsFamilyListSerializer
        queryset = NsFamily.objects.annotate(counts=Count("minerals", distinct=True))

        queryset = serializer_class.setup_eager_loading(queryset=queryset, request=self.request)
        queryset = self._filter_queryset(queryset)

        return self._get_paginated_response(queryset, serializer_class)


class MineralViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    http_method_names = [
        "get",
        "options",
        "head",
    ]

    queryset = Mineral.objects.all()
    serializer_class = MineralListSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    renderer_classes = [
        JSONRenderer,
        BrowsableAPIRenderer,
    ]
    pagination_class = CustomCursorPagination

    permission_classes = [HasAPIKey | IsAuthenticated]
    authentication_classes = [
        SessionAuthentication,
        JWTAuthentication,
    ]

    ordering_fields = [
        "name",
    ]
    ordering = [
        "id",
    ]

    filter_backends = [
        filters.OrderingFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = MineralFilter

    @staticmethod
    def _setup_eager_loading(serializer_class, queryset, request):
        if hasattr(serializer_class, "setup_eager_loading"):
            queryset = serializer_class.setup_eager_loading(queryset=queryset, request=request)

        return queryset

    def _get_secondary_queryset(self):
        # secondary queryset is a mirror of the primary queryset with id only
        # used for prefetching related objects
        queryset = super().get_queryset()
        queryset = queryset.only("id")

        serializer_class = self.get_serializer_class(is_secondary=True)
        queryset = self._setup_eager_loading(serializer_class, queryset, self.request)

        return queryset

    def paginate_queryset(self, queryset, query=None):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        if self.action in ["list"]:
            return self.paginator.paginate_raw_queryset(queryset, self.request, view=self, query=query)
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer_class = self.get_serializer_class()
        queryset = self._setup_eager_loading(serializer_class, queryset, self.request)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset, _queryset = self.get_queryset(), self._get_secondary_queryset()
        queryset = self.filter_queryset(queryset)

        queryset = _annotate__is_grouping(queryset)
        queryset = _annotate__ns_index(queryset, key="ns_index_")

        queryset = queryset.defer(
            "ns_class",
            "ns_subclass",
            "ns_mineral",
            "note",
            "created_at",
        )

        page = self.paginate_queryset(queryset, query=LIST_VIEW_QUERY)
        if page is not None:
            _queryset = _queryset.filter(id__in=[x.id for x in page])

            _serializer_class = self.get_serializer_class(is_secondary=True)
            _serializer = _serializer_class(_queryset, many=True)
            serializer = self.get_serializer(page, many=True)

            _data = _serializer.data
            data = serializer.data
            output = []

            if len(_data) and len(data):
                _merge = pd.merge(pd.DataFrame(data), pd.DataFrame(_data), on="id", how="left")
                _merge = _merge.replace({np.nan: None})
                output = _merge.to_dict("records")

            return self.get_paginated_response(output)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if "q" in self.request.query_params:
            query = self.request.query_params.get("q", "")
            queryset = queryset.extra(
                select={
                    "ordering": """ROW_NUMBER() OVER (ORDER BY ts_rank(mineral_log.search_vector,
                                       (plainto_tsquery('mrdict'::regconfig, %s) || plainto_tsquery('english'::regconfig, %s)), 0) DESC)"""
                },
                select_params=(query, query),
                where=[
                    "mineral_log.search_vector @@ (plainto_tsquery('english', %s) || plainto_tsquery('mrdict', %s))",
                ],
                params=(query, query),
            )

        discovery_countries = self.request.query_params.get("discovery_countries")

        if self.request.query_params.get("filter_related", False) == "true":
            if discovery_countries:
                queryset = queryset.filter(
                    Q(is_grouping=True)
                    & Q(children_hierarchy__mineral__discovery_countries__in=discovery_countries.split(","))
                )

        else:
            if discovery_countries:
                queryset = queryset.filter(Q(discovery_countries__in=discovery_countries.split(",")))

        return queryset

    def get_serializer_class(self, is_secondary=False):
        if is_secondary:
            return MineralListSecondarySerializer

        if self.action in ["list"]:
            return MineralListSerializer
        elif self.action in ["retrieve"]:
            return RetrieveController
        elif self.action in [
            "grouping_members",
            "relations",
            "related_minerals",
        ]:
            return MineralRelationsSerializer
        elif self.action in ["analytical_data"]:
            return MineralAnalyticalDataSerializer

        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        # instance.seen += 1
        # instance.save(update_fields=["seen"])
        queryset = self.queryset.all()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        _instance = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, _instance)

        _is_grouping = _instance.is_grouping
        serializer_cls = self.get_serializer_class()
        queryset = serializer_cls.setup_eager_loading(queryset=queryset, request=request, is_grouping=_is_grouping)
        instance = queryset.get(id=_instance.id)
        serializer = serializer_cls(instance, context={"request": request})

        data = serializer.data
        return Response(data)

    def _get_raw_object(self):
        """
        Returns the raw object without filtering queryset initially.
        """
        queryset = self.queryset.only("id")

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly." % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def _get_related_objects(self, instance, group):
        """
        Returns related objects for a given instance.
        """
        annotate = {"name": F("relation__name"), "slug": F("relation__slug")}

        if instance.is_grouping:
            queryset = HierarchyView.objects.all()
            queryset = queryset.filter(relation__statuses__group=group, relation__direct_relations__direct_status=True)
        else:
            queryset = MineralRelation.objects.all()
            queryset = queryset.filter(status__direct_status=False, status__status__group=group)

        queryset = queryset.filter(mineral=instance).distinct("relation__name")
        queryset = queryset.annotate(**annotate)
        queryset = queryset.order_by("relation__name")
        queryset = queryset.only("relation__name", "relation__slug")

        return queryset

    def _get_grouping_objects(self, instance, status=None):
        """
        Returns grouping objects for a given instance.
        """
        _annotate = {"name": F("relation__name"), "slug": F("relation__slug")}
        _filter = {}

        if status:
            _filter.update({"relation__statuses": status, "relation__direct_relations__direct_status": True})

        queryset = HierarchyView.objects.filter(mineral=instance, **_filter)
        queryset = queryset.distinct("relation__name")
        queryset = queryset.annotate(**_annotate)
        queryset = queryset.order_by("relation__name")
        queryset = queryset.only("relation__name", "relation__slug")

        return queryset

    def _get_approved_objects(self, instance):
        if instance.is_grouping:
            queryset = HierarchyView.objects.all()
            queryset = queryset.filter(mineral=instance, relation__statuses__group=11).distinct("relation__name")
            queryset = queryset.annotate(name=F("relation__name"), slug=F("relation__slug"))
            queryset = queryset.order_by("relation__name")
            queryset = queryset.only("relation__name", "relation__slug")
            serializer_cls = self.get_serializer_class()
        else:
            queryset = Mineral.objects.all()
            queryset = queryset.filter(
                Q(statuses__group=11) & Q(ns_family=instance.ns_family) & ~Q(id=instance.id)
            ).distinct()
            queryset = queryset.order_by("name")
            queryset = queryset.only("name", "slug")
            serializer_cls = BaseMineralRelationsSerializer

        return queryset, serializer_cls

    @action(detail=True, methods=["get"], url_path="grouping-members")
    def grouping_members(self, request, *args, **kwargs):
        instance = self._get_raw_object()
        _status = request.query_params.get("status", None)
        _crystal_system = request.query_params.get("crystal_system", None)
        _discovery_country = request.query_params.get("discovery_country", None)

        queryset = self._get_grouping_objects(instance, _status)

        if instance.is_grouping:
            _filter = {"relation__direct_relations__direct_status": True}
            if _crystal_system:
                queryset = queryset.filter(relation__crystallography__crystal_system=_crystal_system, **_filter)
            if _discovery_country:
                queryset = queryset.filter(relation__discovery_countries__in=_discovery_country.split(","), **_filter)

        serializer_cls = self.get_serializer_class()
        queryset = serializer_cls.setup_eager_loading(queryset=queryset, request=request)
        return Response(serializer_cls(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="relations")
    def relations(self, request, *args, **options):
        instance = self._get_raw_object()
        serializer_cls = self.get_serializer_class()
        _group = request.query_params.get("group", None)
        _group = int(_group) if _group else None

        if _group is None:
            return Response(data={"error": "Missing 'group' parameter."}, status=status.HTTP_400_BAD_REQUEST)

        if _group == 11:
            queryset, serializer_cls = self._get_approved_objects(instance)
        else:
            queryset = self._get_related_objects(instance, _group)

        queryset = serializer_cls.setup_eager_loading(queryset=queryset, request=request)
        return Response(serializer_cls(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def structures(self, request, *args, **options):
        instance = self.get_object()
        _is_grouping = instance.is_grouping
        _relations = [instance.id, *instance.synonyms]

        if _is_grouping:
            _members = instance.members
            _members_synonyms = MineralStatus.get_synonyms(_members)
            _relations += [*(_members + _members_synonyms)]

            _inheritance_chain = MineralInheritance.get_redirect_ids(_relations, INHERIT_CRYSTAL_SYSTEM)
            _inheritance_ids = [x["mineral"] for x in _inheritance_chain]

            for _relation in _relations:
                if _relation in _inheritance_ids:
                    _index = _inheritance_ids.index(_relation)
                    _inherit_from = _inheritance_chain[_index].get("inherit_from")
                    _relations[_relations.index(_relation)] = _inherit_from
                else:
                    pass

        # cache the relations of mineral
        # caches['mineral-relations'].set(, _relations)

        return Response(MineralStructure.aggregate_by_system(_relations), status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def elements(self, request, *args, **options):
        instance = self.get_object()
        _is_grouping = instance.is_grouping
        _relations = [instance.id, *instance.synonyms]

        if _is_grouping:
            _members = instance.members
            _members_synonyms = MineralStatus.get_synonyms(_members)
            _relations += [*(_members + _members_synonyms)]

            _inheritance_chain = MineralInheritance.get_redirect_ids(_relations, INHERIT_CRYSTAL_SYSTEM)
            _inheritance_ids = [x.get("mineral") for x in _inheritance_chain]
            _relations = [
                _inheritance_chain[_inheritance_ids.index(x)].get("inherit_from") if x in _inheritance_ids else x
                for x in _relations
            ]

        return Response(MineralStructure.aggregate_by_element(_relations), status=status.HTTP_200_OK)
