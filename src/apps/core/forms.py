# -*- coding: UTF-8 -*-
from dal import autocomplete
from django.forms import BaseInlineFormSet
from django.forms import BooleanField
from django.forms import CharField
from django.forms import ModelChoiceField
from django.forms import ModelForm
from django.forms import Textarea

from .models.core import Status
from .models.mineral import MineralFormula
from .models.mineral import MineralRelation
from .models.mineral import MineralRelationSuggestion
from .models.mineral import MineralStatus


class MineralFormulaForm(ModelForm):
    class Meta:
        model = MineralFormula
        fields = [
            "formula",
            "note",
            "source",
            "show_on_site",
        ]
        widgets = {
            "note": Textarea(attrs={"rows": 2}),
        }


class MineralRelationSuggestionForm(ModelForm):

    status = ModelChoiceField(
        queryset=None,
        label="Status",
        help_text="Select the status of the related mineral.",
        blank=True,
        required=False,
        # empty_label="",
    )

    note = CharField(widget=Textarea(attrs={"rows": 1}), required=False)
    is_processed = BooleanField(
        initial=False,
        label="Accept relation suggestion",
        help_text="Check this box if the suggestion is accepted.",
        required=False,
    )

    class Meta:
        model = MineralRelationSuggestion
        fields = [
            "mineral",
            "relation",
            "relation_type",
            "is_processed",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        self.direct_relation = kwargs.pop("direct_relation")
        statuses = kwargs.pop("statuses")
        super().__init__(*args, **kwargs)

        self.fields["status"].choices = list(statuses)

    def save(self, commit=True):

        if self.has_changed():
            status = self.cleaned_data.pop("status")

            if status and self.cleaned_data["is_processed"]:
                if self.direct_relation:
                    status, exists = MineralStatus.objects.get_or_create(
                        mineral=self.instance.mineral,
                        status=status,
                        direct_status=self.direct_relation,
                        defaults={
                            "author": self.user,
                        },
                    )
                    MineralRelation.objects.get_or_create(
                        mineral=self.instance.mineral,
                        status=status,
                        relation=self.instance.relation,
                        defaults={
                            "note": self.cleaned_data.get("note"),
                        },
                    )
                else:
                    status, exists = MineralStatus.objects.get_or_create(
                        mineral=self.instance.relation,
                        status=status,
                        direct_status=self.direct_relation,
                        defaults={
                            "author": self.user,
                        },
                    )
                    MineralRelation.objects.get_or_create(
                        mineral=self.instance.relation,
                        status=status,
                        relation=self.instance.mineral,
                        defaults={
                            "note": self.cleaned_data.get("note"),
                        },
                    )

        return super().save(commit)


class MineralRelationForm(ModelForm):
    class Meta:
        model = MineralRelation
        fields = [
            "mineral",
            "relation",
        ]
        widgets = {
            "relation": autocomplete.ModelSelect2(
                url="core:mineral-search",
                attrs={
                    "data-placeholder": "Select mineral ...",
                    "data-minimum-input-length": 3,
                },
            ),
            "note": Textarea(attrs={"rows": 2}),
        }


class MineralStatusForm(ModelForm):

    status = ModelChoiceField(queryset=Status.objects.all(), initial=Status.objects.filter(status_id=0))

    class Meta:
        model = MineralStatus
        fields = [
            "status",
            "needs_revision",
            "author",
            "direct_status",
        ]
        labels = {
            "status": "Status of Species",
            "needs_revision": "Needs to be revised?",
        }
        widgets = {"note": Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        return super().__init__(*args, **kwargs)

    def save(self, commit):
        instance = super().save(commit)

        if self.has_changed():
            instance.author = self.user
            instance.save()

        return instance


class MineralRelationFormset(BaseInlineFormSet):

    model = MineralRelation


class MineralRelationSuggestionFormset(BaseInlineFormSet):

    model = MineralRelationSuggestion


class MineralStatusFormset(BaseInlineFormSet):

    model = MineralStatus
