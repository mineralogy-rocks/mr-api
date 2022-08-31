# -*- coding: UTF-8 -*-
from django.contrib.admin import TabularInline

from .models.mineral import MineralFormula
from .models.mineral import MineralStatus


class MineralFormulaInline(TabularInline):
    model = MineralFormula

    fields = [
        "formula",
        "note",
        "source",
        "show_on_site",
    ]
    ordering = ["source", "created_at"]
    readonly_fields = [
        "created_at",
    ]

    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("source")
        return queryset


class MineralStatusInline(TabularInline):
    model = MineralStatus
    fields = ["status"]
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("status")
        return qs
