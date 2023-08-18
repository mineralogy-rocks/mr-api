from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max
from django.db.models import Min
from django.db.models.expressions import RawSQL
from django.db.models.functions import Round
from rest_framework import serializers

from ..models.mineral import MineralStructure


class MineralSerializerMixin(serializers.Serializer):
    def _get_stats(self, instance, relations):
        _structures_ids = list(
            MineralStructure.objects.filter(mineral__in=[instance.id, *relations])
            .only("id")
            .values_list("id", flat=True)
        )
        structures = None
        elements = None

        if _structures_ids:
            _aggregations = {}
            _fields = ["a", "b", "c", "alpha", "beta", "gamma", "volume"]
            for _field in _fields:
                _aggregations.update(
                    {f"min_{_field}": Min(_field), f"max_{_field}": Max(_field), f"avg_{_field}": Round(Avg(_field), 4)}
                )
            _summary_queryset = MineralStructure.objects.filter(id__in=_structures_ids).aggregate(**_aggregations)
            structures = {
                "count": len(_structures_ids),
            }
            for _field in ["a", "b", "c", "alpha", "beta", "gamma", "volume"]:
                structures[_field] = {
                    "min": _summary_queryset[f"min_{_field}"],
                    "max": _summary_queryset[f"max_{_field}"],
                    "avg": _summary_queryset[f"avg_{_field}"],
                }
            _elements = (
                MineralStructure.objects.filter(id__in=_structures_ids)
                .annotate(element=RawSQL("UNNEST(regexp_matches(formula, 'REE|[A-Z][a-z]?', 'g'))", []))
                .values("element")
                .annotate(count=Count("id", distinct=True))
                .order_by("element")
            )
            elements = _elements.values("element", "count")
        return structures, elements
