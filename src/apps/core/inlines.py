# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db.models import CharField
from django.db.models import Q
from django.db.models import TextField
from django.forms import Textarea
from django.utils.safestring import mark_safe
from nested_admin import NestedStackedInline
from nested_admin import NestedTabularInline

from .forms import MineralFormulaForm
from .forms import MineralHistoryForm
from .forms import MineralRelationForm
from .forms import MineralRelationFormset
from .forms import MineralRelationSuggestionForm
from .forms import MineralStatusForm
from .forms import MineralStatusFormset
from .forms import ModelChoiceField
from .models.core import Status
from .models.mineral import MineralFormula
from .models.mineral import MineralHistory
from .models.mineral import MineralRelation
from .models.mineral import MineralRelationSuggestion
from .models.mineral import MineralStatus
from .models.mineral import MineralStructure
from .utils import get_relation_note


class MineralHistoryInline(NestedStackedInline):
    model = MineralHistory
    form = MineralHistoryForm

    fields = [
        "discovery_year_min",
        "discovery_year_max",
        "discovery_year_note",
        "certain",
        "discovery_year",
        "ima_year",
        "publication_year",
        "approval_year",
        "first_usage_date",
        "first_known_use",
    ]

    readonly_fields = [
        "discovery_year",
        "ima_year",
        "publication_year",
        "approval_year",
    ]

    extra = 0
    classes = ["collapse"]

    verbose_name = "Historical data"
    verbose_name_plural = "Historical data"


class MineralFormulaInline(NestedStackedInline):
    model = MineralFormula
    form = MineralFormulaForm

    fields = [
        "formula",
        "note",
        "source",
        "show_on_site",
        "created_at",
    ]
    ordering = ["source", "created_at"]
    readonly_fields = [
        "created_at",
    ]

    extra = 0
    classes = ["collapse"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("source")
        return queryset


class MineralStructureInline(NestedStackedInline):
    model = MineralStructure
    fields = [
        "structure",
        "formula",
        "calculated_formula",
        "reference",
        "_links",
        "note",
        "created_at",
    ]
    readonly_fields = [
        "structure",
        "_links",
        "created_at",
    ]

    ordering = ["source", "created_at"]

    classes = ["collapse"]
    extra = 0

    formfield_overrides = {
        CharField: {"widget": Textarea(attrs={"rows": 1, "cols": 80})},
        TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 80})},
        ArrayField: {"widget": Textarea(attrs={"rows": 3, "cols": 80})},
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("source")
        return queryset

    @admin.display(description="Structure definition")
    def structure(self, instance):
        return mark_safe(
            f"<b>a:</b> {instance.a} <b>b:</b> {instance.b} <b>c:</b> {instance.c} <b>alpha:</b> {instance.alpha} \
              <b>beta:</b> {instance.beta} <b>gamma:</b> {instance.gamma} <b>volume:</b> {instance.volume}"
        )

    @admin.display(description="Links")
    def _links(self, instance):
        _links = instance.links or []
        return mark_safe(
            "<br>".join(
                [
                    "<a href=" + _link + ' target="_blank" rel="noopener noreferrer">' + _link + "</a>"
                    for _link in _links
                ]
            )
        )


class MineralRelationInline(NestedStackedInline):
    model = MineralRelation
    form = MineralRelationForm
    formset = MineralRelationFormset

    verbose_name = "Related entry"
    verbose_name_plural = "Status-related species"

    fields = [
        "relation",
        "note",
    ]

    fk_name = "status"
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("status", "mineral", "relation")
        return queryset


class MineralDirectRelationSuggestionInline(NestedTabularInline):
    model = MineralRelationSuggestion
    form = MineralRelationSuggestionForm
    classes = ["collapse"]

    verbose_name = "Suggested direct relation"
    verbose_name_plural = "Suggested direct relations from mindat.org"

    max_num = 0
    can_delete = False

    fields = [
        "relation",
        "mindat_link",
        "description",
        "relation_note",
        "status",
        "note",
        "is_processed",
    ]
    readonly_fields = [
        "relation",
        "relation_note",
        "description",
        "mindat_link",
    ]
    ordering = [
        "relation_type",
        "mineral__name",
    ]

    fk_name = "mineral"
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("relation", "mineral")
        queryset = queryset.filter(~Q(relation_type=5))
        return queryset

    @admin.display(description="Description")
    def description(self, instance):
        return mark_safe(instance.relation.description) if instance.relation.description else ""

    @admin.display(description="Mindat Ref")
    def mindat_link(self, instance):
        if instance.relation.mindat_id:
            return mark_safe(
                '<a href="https://www.mindat.org/min-'
                + str(instance.relation.mindat_id)
                + '.html" target="_blank" rel="nofollow">see on mindat</a>'
            )

    @admin.display(description="Relation note.")
    def relation_note(self, instance):
        return get_relation_note(instance.relation_type)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class UserProvidingInlineFormSet(formset):
            def __new__(cls, *args, **kwargs):
                kwargs["form_kwargs"] = {
                    "user": request.user,
                    "direct_relation": True,
                    "statuses": [*ModelChoiceField(queryset=Status.objects.all()).choices],
                }
                return formset(*args, **kwargs)

        return UserProvidingInlineFormSet


class MineralReverseRelationSuggestionInline(NestedTabularInline):
    model = MineralRelationSuggestion
    form = MineralRelationSuggestionForm
    classes = ["collapse"]

    verbose_name = "Suggested reverse relation"
    verbose_name_plural = "Suggested reverse relations from mindat.org"

    max_num = 0
    can_delete = False

    fields = [
        "mineral",
        "mindat_link",
        "description",
        "relation_note",
        "status",
        "note",
        "is_processed",
    ]
    readonly_fields = [
        "mineral",
        "relation_note",
        "mindat_link",
        "description",
    ]
    ordering = [
        "relation_type",
        "mineral__name",
    ]

    fk_name = "relation"
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("relation", "mineral")
        queryset = queryset.filter(~Q(relation_type=5))
        return queryset

    @admin.display(description="Description")
    def description(self, instance):
        return mark_safe(instance.mineral.description) if instance.mineral.description else ""

    @admin.display(description="Mindat Ref")
    def mindat_link(self, instance):
        if instance.mineral.mindat_id:
            return mark_safe(
                '<a href="https://www.mindat.org/min-'
                + str(instance.mineral.mindat_id)
                + '.html" target="_blank" rel="nofollow">see on mindat</a>'
            )

    @admin.display(description="Relation note.")
    def relation_note(self, instance):
        return get_relation_note(instance.relation_type)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class UserProvidingInlineFormSet(formset):
            def __new__(cls, *args, **kwargs):
                kwargs["form_kwargs"] = {
                    "user": request.user,
                    "direct_relation": False,
                    "statuses": [*ModelChoiceField(queryset=Status.objects.all()).choices],
                }
                return formset(*args, **kwargs)

        return UserProvidingInlineFormSet


class MineralStatusInline(NestedTabularInline):
    model = MineralStatus
    fk_name = "mineral"
    form = MineralStatusForm
    formset = MineralStatusFormset

    inlines = [MineralRelationInline]

    fields = [
        "status",
        "needs_revision",
        "author_",
        "direct_status",
        "note",
        "created_at",
        "updated_at",
    ]
    ordering = [
        "status__status_id",
    ]
    readonly_fields = [
        "author_",
        "created_at",
        "updated_at",
    ]

    extra = 0
    classes = ["collapse"]

    @admin.display(description="Author")
    def author_(self, instance):
        return instance.author.first_name + " " + instance.author.last_name if instance.author else instance.author

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("status", "author")
        return queryset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class UserProvidingInlineFormSet(formset):
            def __new__(cls, *args, **kwargs):
                kwargs["form_kwargs"] = {"user": request.user}
                return formset(*args, **kwargs)

        return UserProvidingInlineFormSet
