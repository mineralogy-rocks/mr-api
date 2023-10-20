# -*- coding: UTF-8 -*-
from django.db.models import Case
from django.db.models import CharField
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Coalesce
from django.db.models.functions import Concat
from django.db.models.functions import Right

from .models.mineral import MineralStatus


def _annotate__ns_index(queryset, key="ns_index"):
    _annotation = {
        key: Case(
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
    }
    queryset = queryset.annotate(**_annotation)
    return queryset


def _annotate__is_grouping(queryset, key="_is_grouping"):
    """Here we are using `_is_grouping` so that the cached property `is_grouping` can be used in the model."""
    _annotation = {key: Exists(MineralStatus.objects.filter(Q(mineral=OuterRef("id")) & Q(status__group=1)))}
    queryset = queryset.annotate(**_annotation)
    return queryset
