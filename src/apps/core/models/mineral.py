# -*- coding: UTF-8 -*-
import uuid

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.urls import reverse

from ..utils import formula_to_html
from .base import BaseModel
from .base import Creatable
from .base import Nameable
from .base import Updatable
from .core import Country
from .core import FormulaSource
from .core import NsClass
from .core import NsFamily
from .core import NsSubclass
from .core import Status
from .crystal import CrystalClass
from .crystal import CrystalSystem
from .crystal import SpaceGroup
from .ion import Ion
from .ion import IonPosition


class Mineral(Nameable, Creatable, Updatable):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    note = models.TextField(
        blank=True,
        null=True,
        help_text="Please, leave your notes about the specie here.",
    )
    ns_class = models.ForeignKey(
        NsClass,
        models.CASCADE,
        db_column="ns_class",
        to_field="id",
        blank=True,
        null=True,
        related_name="minerals",
    )
    ns_subclass = models.ForeignKey(
        NsSubclass,
        models.CASCADE,
        db_column="ns_subclass",
        to_field="id",
        blank=True,
        null=True,
        related_name="minerals",
    )
    ns_family = models.ForeignKey(
        NsFamily,
        models.CASCADE,
        db_column="ns_family",
        to_field="id",
        blank=True,
        null=True,
        related_name="minerals",
    )
    ns_mineral = models.CharField(max_length=10, blank=True, null=True)
    seen = models.IntegerField(
        default=0,
        help_text="Number of times this specie was retrieved by API and clients.",
    )
    description = models.TextField(null=True, blank=True, help_text="Description from mindat.org")
    mindat_id = models.IntegerField(blank=True, null=True)
    ima_symbol = models.CharField(max_length=12, null=True, blank=True, help_text="Official IMA symbol.")

    discovery_countries = models.ManyToManyField(Country, through="MineralCountry")
    statuses = models.ManyToManyField(
        Status,
        through="MineralStatus",
        through_fields=(
            "mineral",
            "status",
        ),
    )
    impurities = models.ManyToManyField(Ion, through="MineralImpurity", related_name="impurities")
    ion_positions = models.ManyToManyField(IonPosition, through="MineralIonPosition")
    crystal_systems = models.ManyToManyField(CrystalSystem, through="MineralCrystallography")

    relations = models.ManyToManyField(
        "self",
        through="MineralRelation",
    )

    class Meta:
        managed = False
        db_table = "mineral_log"
        ordering = [
            "name",
        ]

        verbose_name = "Mineral"
        verbose_name_plural = "Minerals"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:mineral-detail", kwargs={"pk": self.id})

    def get_admin_url(self):
        return reverse("admin:core_mineral_change", args=(self.id,))

    @admin.display(description="Nickel-Strunz Index")
    def ns_index(self):
        if self.ns_class:
            return "{ns_class}.{ns_subclass}{ns_family}.{ns_mineral}".format(
                ns_class=str(self.ns_class.id),
                ns_subclass=str(self.ns_subclass.ns_subclass)[-1] if self.ns_subclass is not None else "0",
                ns_family=str(self.ns_family.ns_family)[-1] if self.ns_family is not None else "0",
                ns_mineral=str(self.ns_mineral) if self.ns_mineral is not None else "0",
            )
        else:
            return None

    def _statuses(self):
        if self.statuses:
            return "; ".join([str(status.status.status_id) for status in self.statuses.all()])


class MineralStatus(BaseModel, Creatable, Updatable):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id", related_name="direct_relations")
    status = models.ForeignKey(
        Status,
        models.CASCADE,
        db_column="status_id",
        related_name="minerals",
        help_text="A classification status of species.",
    )
    needs_revision = models.BooleanField(default=False, null=False, help_text="Does the entry need a revision?")
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Please, leave your notes about the status here.",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column="author_id",
        null=True,
        help_text="Author of the last update.",
    )
    direct_status = models.BooleanField(
        default=True,
        null=False,
        help_text="If checked, means the current species is a synonym/variety/polytype of related species.\n"
        "Otherwise, means the related species are synonyms/varieties/polytypes of current species.",
    )

    relations = models.ManyToManyField(
        Mineral,
        through="MineralRelation",
        through_fields=(
            "status",
            "relation",
        ),
    )

    class Meta:
        managed = False
        db_table = "mineral_status"
        unique_together = (("mineral", "status"),)

        verbose_name = "Status"
        verbose_name_plural = "Statuses"

    def __str__(self):
        return self.mineral.name + " " + self.status.description_short


class MineralRelation(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id")
    status = models.ForeignKey(
        MineralStatus,
        models.CASCADE,
        null=True,
        db_column="mineral_status_id",
    )
    relation = models.ForeignKey(
        Mineral,
        models.CASCADE,
        db_column="relation_id",
        related_name="inverse_relations",
    )
    note = models.TextField(
        null=True,
        blank=True,
        help_text="Please, leave your notes about the relation here.",
    )

    class Meta:
        managed = False
        db_table = "mineral_relation"
        unique_together = (
            "mineral",
            "status",
            "relation",
        )

        verbose_name = "Relation"
        verbose_name_plural = "Relations"

    def __str__(self):
        return self.relation.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        status = None

        if self.status:
            opposite_status = not self.status.direct_status
            status, exists = MineralStatus.objects.get_or_create(
                mineral=self.relation,
                status=self.status.status,
                direct_status=opposite_status,
                defaults={
                    "needs_revision": self.status.needs_revision,
                    "author": self.status.author,
                },
            )

        MineralRelation.objects.get_or_create(
            mineral=self.relation,
            status=status,
            relation=self.mineral,
        )

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        all_opposite_relations = MineralRelation.objects.filter(
            Q(mineral=self.relation) & Q(status__status=self.status.status)
        )

        adjacent_relations = all_opposite_relations.filter(Q(relation=self.mineral))

        if all_opposite_relations.count() == adjacent_relations.count():
            for relation in all_opposite_relations:
                if not relation.status.direct_status:
                    relation.status.delete()

        adjacent_relations.delete()


class MineralRelationSuggestion(BaseModel):

    mineral = models.ForeignKey(
        Mineral,
        models.CASCADE,
        db_column="mineral_id",
        related_name="suggested_relations",
    )
    relation = models.ForeignKey(
        Mineral,
        models.CASCADE,
        db_column="relation_id",
        related_name="suggested_inverse_relations",
    )
    relation_type = models.IntegerField(
        null=True,
        db_column="relation_type_id",
        help_text="Relation type according to mindat.",
    )
    is_processed = models.BooleanField(null=False, default=False, help_text="Is the suggestion processed?")

    class Meta:
        managed = False
        db_table = "mineral_relation_suggestion"
        unique_together = (
            "mineral",
            "relation",
            "relation_type",
        )

        verbose_name = "Relation Suggestion"
        verbose_name_plural = "Relation Syggestions"

    def __str__(self):
        return self.mineral.name


class MineralFormula(BaseModel, Creatable):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id", related_name="formulas")
    formula = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="Mineral formula in different formats.",
    )
    note = models.TextField(null=True, blank=True)
    source = models.ForeignKey(FormulaSource, models.CASCADE, db_column="source_id", related_name="minerals")
    show_on_site = models.BooleanField(
        default=False,
        help_text="Whether a specific formula has a priority over the others and thefore should be shown on site.",
    )

    class Meta:
        managed = False
        db_table = "mineral_formula"

        verbose_name = "Formula"
        verbose_name_plural = "Formulas"

    def __str__(self):
        if self.source == 1:
            return formula_to_html(self.formula)
        return self.formula or self.note


class MineralImpurity(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id")
    ion = models.ForeignKey(Ion, models.CASCADE, db_column="ion_id")
    ion_quantity = models.CharField(max_length=30, null=True, blank=True)
    rich_poor = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "mineral_impurity"

        verbose_name = "Impurity"
        verbose_name_plural = "Impurities"

    def __str__(self):
        return "{} - {}".format(self.ion, self.ion_quantity)


class MineralIonTheoretical(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id", related_name="ions_theoretical")
    ion = models.ForeignKey(Ion, models.CASCADE, db_column="ion_id", related_name="minerals_theoretical")

    class Meta:
        managed = False
        db_table = "mineral_ion_theoretical"
        unique_together = (("mineral", "ion"),)

        verbose_name = "Theoretical Ion"
        verbose_name_plural = "Theoretical Ions"

    def __str__(self):
        return self.ion.formula


class MineralCrystallography(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id", related_name="crystallography")
    crystal_system = models.ForeignKey(
        CrystalSystem,
        models.CASCADE,
        db_column="crystal_system_id",
        related_name="minerals",
    )
    crystal_class = models.ForeignKey(
        CrystalClass,
        models.CASCADE,
        db_column="crystal_class_id",
        null=True,
        default=None,
    )
    space_group = models.ForeignKey(SpaceGroup, models.CASCADE, db_column="space_group_id", null=True, default=None)
    a = models.FloatField(blank=True, null=True, default=None)
    b = models.FloatField(blank=True, null=True, default=None)
    c = models.FloatField(blank=True, null=True, default=None)
    alpha = models.FloatField(blank=True, null=True, default=None)
    gamma = models.FloatField(blank=True, null=True, default=None)
    z = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        managed = False
        db_table = "mineral_crystallography"

        verbose_name = "Crystallography"
        verbose_name_plural = "Crystallographies"

    def __str__(self):
        return self.crystal_system.name


class MineralCountry(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id")
    country = models.ForeignKey(Country, models.CASCADE, db_column="country_id", related_name="minerals")

    note = models.TextField(db_column="note", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mineral_country"
        unique_together = (("mineral", "country"),)

        verbose_name = "Discovery Country"
        verbose_name_plural = "Discovery Countries"

    def __str__(self):
        note = f" ({self.note})" if self.note else ""
        return f"{self.country.name}{note}"


class MineralHistory(BaseModel):

    mineral = models.OneToOneField(Mineral, models.CASCADE, db_column="mineral_id", related_name="history")
    discovery_year_min = models.IntegerField(blank=True, null=True)
    discovery_year_max = models.IntegerField(blank=True, null=True)
    discovery_year_note = models.TextField(blank=True, null=True)

    discovery_year = models.SmallIntegerField(blank=True, null=True)
    ima_year = models.SmallIntegerField(blank=True, null=True)
    publication_year = models.SmallIntegerField(blank=True, null=True)
    approval_year = models.SmallIntegerField(blank=True, null=True)

    certain = models.BooleanField(null=False, default=True)
    first_usage_date = models.TextField(blank=True, null=True)
    first_known_use = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mineral_history"
        verbose_name = "Discovery Context"
        verbose_name_plural = "Discovery contexts"


class MineralHierarchy(BaseModel):

    mineral = models.ForeignKey(
        Mineral,
        models.CASCADE,
        db_column="mineral_id",
        related_name="parents_hierarchy",
    )
    parent = models.ForeignKey(
        Mineral,
        models.CASCADE,
        db_column="parent_id",
        null=True,
        related_name="children_hierarchy",
    )

    class Meta:
        managed = False
        db_table = "mineral_hierarchy"
        unique_together = (("mineral", "parent"),)

        verbose_name = "Hierarchy"
        verbose_name_plural = "Hierarchies"

    def __str__(self):
        return self.mineral.name


class MineralIonPosition(BaseModel):

    mineral = models.ForeignKey(
        Mineral,
        models.CASCADE,
        db_column="mineral_id",
        to_field="id",
        related_name="ions",
    )
    position = models.ForeignKey(IonPosition, models.CASCADE, db_column="ion_position_id", to_field="id")
    ion = models.ForeignKey(
        Ion,
        models.CASCADE,
        db_column="ion_id",
        to_field="id",
        related_name="mineral_positions",
    )
    quantity = models.TextField(blank=True, null=True, db_column="ion_quantity")

    class Meta:
        managed = False
        db_table = "mineral_ion_position"
        ordering = [
            "mineral",
        ]

        verbose_name = "Mineral Ions"
        verbose_name_plural = "Minerals Ions"

    def __str__(self):
        return self.mineral.name


class MindatSync(BaseModel, Creatable):

    values = models.JSONField(blank=True, null=True)
    is_successful = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "mindat_sync_log"

        verbose_name = "Mindat Sync History"
        verbose_name_plural = "Mindat Syncs"

    def __str__(self):
        return str(self.id)

    def get_absolute_url(self):
        return reverse("core:sync-log", kwargs={"pk": self.id})
