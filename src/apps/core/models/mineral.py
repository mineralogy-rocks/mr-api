# -*- coding: UTF-8 -*-
import urllib
import uuid

from django.conf import settings
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from ..utils import shorten_text
from ..utils import unique_slugify
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
    slug = models.SlugField(
        max_length=255, unique=True, null=True, blank=True, help_text="Slug used for retrieving through website."
    )

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

    def get_mindat_url(self):
        return "https://www.mindat.org/min-{}.html".format(self.mindat_id) if self.mindat_id else None

    def get_rruff_url(self):
        return "https://rruff.info/{}".format(urllib.parse.quote_plus(self.name))

    def get_cod_url(self):
        return "https://www.crystallography.net/cod/result?text={}".format(urllib.parse.quote_plus(self.name))

    def get_amcsd_url(self):
        return "http://rruff.geo.arizona.edu/AMS/result.php?mineral={}".format(urllib.parse.quote_plus(self.name))

    @admin.display(description="Nickel-Strunz Index")
    def ns_index(self):
        if self.ns_class:
            return "{ns_class}.{ns_subclass}{ns_family}.{ns_mineral}".format(
                ns_class=str(self.ns_class.id),
                ns_subclass=str(self.ns_subclass.ns_subclass)[-1] if self.ns_subclass else "0",
                ns_family=str(self.ns_family.ns_family)[-1] if self.ns_family else "0",
                ns_mineral=str(self.ns_mineral) if self.ns_mineral else "0",
            )
        else:
            return None

    def short_description(self):
        return shorten_text(self.description, limit=700) if self.description else None

    def save(self, *args, **kwargs):
        if not self.slug:
            unique_slugify(self, getattr(self, "name"))
        super().save(*args, **kwargs)


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

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        MineralStatus.objects.filter(
            mineral=self.mineral, status=self.status, direct_status=(not self.direct_status)
        ).delete()


class MineralRelation(BaseModel):
    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id")
    status = models.ForeignKey(
        MineralStatus,
        models.CASCADE,
        null=True,
        db_column="mineral_status_id",
        related_name="mineral_status",
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

        verbose_name = "Ideal Formula"
        verbose_name_plural = "Ideal Formulas"

    def __str__(self):
        return mark_safe(self.formula) or self.note

    @property
    def formula_escape(self):
        return mark_safe(self.formula)


class MineralStructure(BaseModel, Creatable, Updatable):
    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column="mineral_id", related_name="structures")
    cod = models.IntegerField(null=True, blank=True, db_column="cod_id", help_text="Open Crystallography Database id")
    amcsd = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column="amcsd_id",
        help_text="American Mineralogist Crystal Structure Database id",
    )

    source = models.ForeignKey(FormulaSource, models.CASCADE, db_column="source_id", related_name="structures")

    a = models.FloatField(null=True, blank=True, help_text="a parameter of the structure.")
    a_sigma = models.FloatField(null=True, blank=True, help_text="a parameter sigma of the structure.")
    b = models.FloatField(null=True, blank=True, help_text="b parameter of the structure.")
    b_sigma = models.FloatField(null=True, blank=True, help_text="b parameter sigma of the structure.")
    c = models.FloatField(null=True, blank=True, help_text="c parameter of the structure.")
    c_sigma = models.FloatField(null=True, blank=True, help_text="c parameter sigma of the structure.")
    alpha = models.FloatField(null=True, blank=True, help_text="alpha parameter of the structure.")
    alpha_sigma = models.FloatField(null=True, blank=True, help_text="alpha parameter sigma of the structure.")
    beta = models.FloatField(null=True, blank=True, help_text="beta parameter of the structure.")
    beta_sigma = models.FloatField(null=True, blank=True, help_text="beta parameter sigma of the structure.")
    gamma = models.FloatField(null=True, blank=True, help_text="gamma parameter of the structure.")
    gamma_sigma = models.FloatField(null=True, blank=True, help_text="gamma parameter sigma of the structure.")
    volume = models.FloatField(null=True, blank=True, help_text="Volume of the structure.")
    volume_sigma = models.FloatField(null=True, blank=True, help_text="Volume sigma of the structure.")
    space_group = models.CharField(max_length=100, null=True, blank=True, help_text="Space group")

    formula = models.CharField(max_length=1000, null=True, blank=True, help_text="Formula of the structure.")
    calculated_formula = models.CharField(
        max_length=1000, null=True, blank=True, help_text="Calculated formula of the structure."
    )

    reference = models.TextField(null=True, blank=True, help_text="Reference of the structure.")
    links = ArrayField(
        models.TextField(null=True, blank=True), null=True, blank=True, help_text="Links to other resources."
    )
    note = models.TextField(null=True, blank=True, help_text="Note of the structure.")

    class Meta:
        managed = False
        db_table = "mineral_structure"

        verbose_name = "Analytical Measurement"
        verbose_name_plural = "Analytical Measurements"

    def __str__(self):
        return mark_safe(self.formula) or self.note


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
    mineral = models.OneToOneField(Mineral, models.CASCADE, db_column="mineral_id", related_name="crystallography")
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
    discovery_year_min = models.IntegerField(blank=True, null=True, help_text="Discovery year min ")
    discovery_year_max = models.IntegerField(
        blank=True, null=True, help_text="Discovery year max (leave empty if not known)"
    )
    discovery_year_note = models.TextField(blank=True, null=True, help_text="Note about discovery year")

    discovery_year = models.SmallIntegerField(
        blank=True, null=True, help_text="Discovery year (fetched from mindat.org)"
    )
    ima_year = models.SmallIntegerField(
        blank=True, null=True, help_text="IMA submission year (fetched from mindat.org)"
    )
    publication_year = models.SmallIntegerField(
        blank=True, null=True, help_text="First publication year (fetched from mindat.org)"
    )
    approval_year = models.SmallIntegerField(
        blank=True, null=True, help_text="IMA approval year (fetched from mindat.org)"
    )

    certain = models.BooleanField(null=False, default=True, help_text="Has the discovery year been confirmed?")
    first_usage_date = models.TextField(
        blank=True, null=True, help_text="First usage date (e.g. century, year or approximate timespan)"
    )
    first_known_use = models.TextField(blank=True, null=True, help_text="First known use notation")

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


class HierarchyView(BaseModel):
    mineral = models.ForeignKey(Mineral, models.DO_NOTHING, db_column="mineral_id", related_name="hierarchy")
    relation = models.ForeignKey(Mineral, models.DO_NOTHING, db_column="relation_id", related_name="inverse_hierarchy")
    is_parent = models.BooleanField()

    class Meta:
        managed = False
        db_table = "mineral_hierarchy_view"
        ordering = [
            "id",
        ]

        verbose_name = "Hierarchy View"
        verbose_name_plural = "Hierarchy View"

    def __str__(self):
        return self.mineral.name

    @classmethod
    def refresh_view(cls):
        with connection.cursor() as cursor:
            cursor.execute("REFRESH MATERIALIZED VIEW mineral_hierarchy_view")
        return True


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
        return reverse("admin:core_mindatsync_change", kwargs={"object_id": self.id})
