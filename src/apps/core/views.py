# -*- coding: UTF-8 -*-
import subprocess

from dal import autocomplete
from django.db.models import Case
from django.db.models import CharField
from django.db.models import Count
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import F
from django.db.models import Value
from django.db.models import FilteredRelation
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from django.db.models.functions import Right
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
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_simplejwt.authentication import JWTAuthentication

from .filters import MineralFilter
from .filters import NickelStrunzFilter
from .filters import StatusFilter
from .models.core import NsClass
from .models.core import NsFamily
from .models.core import NsSubclass
from .models.core import Status
from .models.mineral import Mineral
from .models.mineral import MineralStatus
from .models.mineral import MineralRelation
from .models.mineral import HierarchyView
from .pagination import CustomCursorPagination
from .serializers.core import NsClassSubclassFamilyListSerializer
from .serializers.core import NsFamilyListSerializer
from .serializers.core import NsSubclassListSerializer
from .serializers.core import StatusListSerializer
from .serializers.mineral import MineralListSerializer
from .serializers.mineral import MineralRetrieveSerializer
from .serializers.mineral import MineralRelationsSerializer
from .serializers.mineral import BaseMineralRelationsSerializer
from .serializers.mineral import MineralListSecondarySerializer
from .queries import LIST_VIEW_QUERY


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
        "-name",
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
        if self.action in ['list',]:
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
        _is_grouping = MineralStatus.objects.filter(Q(mineral=OuterRef("id")) & Q(status__group=1))

        queryset = queryset.annotate(
            is_grouping=Exists(_is_grouping),
            ns_index_=Case(
                When(
                    ns_class__isnull=False,
                    then=Concat(
                        "ns_class__id",
                        Value("."),
                        Coalesce(Right("ns_subclass__ns_subclass", 1), Value("0")),
                        Coalesce(Right("ns_family__ns_family", 1), Value("0")),
                        Value("."),
                        Coalesce("ns_mineral", Value("0")),
                        output_field=CharField(),
                    ),
                ),
                default=None,
            ),
        )

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
            for x in data:
                for y in _data:
                    if x["id"] == y["id"]:
                        x.update(y)
                        output.append(x)
                        break
            return self.get_paginated_response(output)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        if "q" in self.request.query_params:

            query = self.request.query_params.get("q", "")
            queryset = queryset.extra(
                select={"ordering": """ROW_NUMBER() OVER (ORDER BY ts_rank(mineral_log.search_vector,
                                       (plainto_tsquery('mrdict'::regconfig, %s) || plainto_tsquery('english'::regconfig, %s)), 0) DESC)"""},
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
            return MineralRetrieveSerializer
        elif self.action in ["varieties", "synonyms", "approved_minerals",]:
            return MineralRelationsSerializer

        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.seen += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _get_raw_object(self):
        """
        Returns the raw object without filtering queryset initially.
        """
        queryset = self.queryset

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def _is_grouping(self, instance):
        _is_grouping = MineralStatus.objects.filter(mineral=instance, status__group=1).exists()
        return _is_grouping

    def _get_related_objects(self, instance, group):
        """
        Returns related objects for a given instance.
        """
        _is_grouping = self._is_grouping(instance)
        annotate = { "name": F("relation__name"), "slug": F("relation__slug") }

        if _is_grouping:
            queryset = HierarchyView.objects.all()
            queryset = queryset.filter(relation__statuses__group=group)
        else:
            queryset = MineralRelation.objects.all()
            queryset = queryset.filter(status__direct_status=False, status__status__group=group)

        queryset = queryset.filter(mineral=instance).distinct('relation__name')
        queryset = queryset.annotate(**annotate)
        queryset = queryset.order_by("relation__name")
        queryset = queryset.only("relation__name", "relation__slug")

        return queryset

    @action(detail=True, methods=["get"], url_path="varieties")
    def varieties(self, request, *args, **kwargs):
        instance = self._get_raw_object()

        queryset = self._get_related_objects(instance, 3)

        serializer_cls = self.get_serializer_class()
        queryset = serializer_cls.setup_eager_loading(queryset=queryset, request=request)

        return Response(serializer_cls(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="synonyms")
    def synonyms(self, request, *args, **kwargs):
        instance = self._get_raw_object()

        queryset = self._get_related_objects(instance, 2)

        serializer_cls = self.get_serializer_class()
        queryset = serializer_cls.setup_eager_loading(queryset=queryset, request=request)

        return Response(serializer_cls(queryset, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="approved-minerals")
    def approved_minerals(self, request, *args, **options):
        instance = self._get_raw_object()

        _is_grouping = self._is_grouping(instance)

        if _is_grouping:
            # retrieving all approved minerals for a given grouping
            queryset = HierarchyView.objects.all()
            queryset = queryset.filter(mineral=instance, relation__statuses__group=11).distinct('relation__name')
            queryset = queryset.annotate(name=F("relation__name"), slug=F("relation__slug"))
            queryset = queryset.order_by("relation__name")
            queryset = queryset.only("relation__name", "relation__slug")
            serializer_cls = self.get_serializer_class()
        else:
            # here we are retrieving all isostructural minerals
            queryset = Mineral.objects.all()
            queryset = queryset.filter(Q(statuses__group=11) & Q(ns_family=instance.ns_family) & ~Q(id=instance.id)).distinct()
            queryset = queryset.order_by("name")
            queryset = queryset.only("name", "slug")
            serializer_cls = BaseMineralRelationsSerializer

        queryset = serializer_cls.setup_eager_loading(queryset=queryset, request=request)
        return Response(serializer_cls(queryset, many=True).data, status=status.HTTP_200_OK)


class SyncView(APIView):
    """
    This view is used to sync the database with the mindat.org database.
    """

    http_method_names = ["get",]
    authentication_classes = [
        JWTAuthentication,
    ]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            command = "python manage.py sync_mindat"
            subprocess.Popen(command, shell=True)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)
