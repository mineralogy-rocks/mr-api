# -*- coding: UTF-8 -*-
from django.db import models

from ..utils import formula_to_html
from .base import BaseModel
from .base import Nameable
from .element import Element


class IonClass(BaseModel, Nameable):
    class Meta:
        managed = False
        db_table = "ion_class_list"

        verbose_name = "Ion Class"
        verbose_name_plural = "Ion Classes"

    def __str__(self):
        return self.name


class IonSubclass(BaseModel, Nameable):
    class Meta:
        managed = False
        db_table = "ion_subclass_list"

        verbose_name = "Ion Subclass"
        verbose_name_plural = "Ion Subclasses"

    def __str__(self):
        return self.name


class IonGroup(BaseModel, Nameable):
    class Meta:
        managed = False
        db_table = "ion_group_list"

        verbose_name = "Ion Group"
        verbose_name_plural = "Ion Groups"

    def __str__(self):
        return self.name


class IonSubgroup(BaseModel, Nameable):
    class Meta:
        managed = False
        db_table = "ion_subgroup_list"

        verbose_name = "Ion Subgroup"
        verbose_name_plural = "Ion Subgroups"

    def __str__(self):
        return self.name


class IonType(BaseModel, Nameable):
    class Meta:
        managed = False
        db_table = "ion_type_list"

        verbose_name = "Ion Type"
        verbose_name_plural = "Ion Types"

    def __str__(self):
        return self.name


class IonPosition(BaseModel, Nameable):

    ions = models.ManyToManyField("core.Ion", through="core.MineralIonPosition")

    class Meta:
        managed = False
        db_table = "ion_position_list"
        ordering = [
            "name",
        ]

        verbose_name = "Ion Position"
        verbose_name_plural = "Ion Positions"

    def __str__(self):
        return self.name


class Ion(BaseModel, Nameable):

    formula = models.CharField(max_length=100, null=False)
    formula_with_oxidation = models.CharField(max_length=100, null=True)
    overall_charge = models.CharField(max_length=100, null=True)
    expressed_as = models.TextField(null=True, blank=True)
    element_or_sulfide = models.BooleanField(null=True, blank=True)
    structure_description = models.TextField(null=True, blank=True)
    geometry = models.TextField(null=True, blank=True)

    ion_type = models.ForeignKey(
        IonType,
        models.CASCADE,
        db_column="ion_type_id",
        to_field="id",
        related_name="ions",
    )
    variety_of = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        db_column="variety_of",
        to_field="id",
        null=True,
        blank=True,
    )
    ion_class = models.ForeignKey(
        IonClass,
        models.CASCADE,
        db_column="ion_class_id",
        to_field="id",
        related_name="ions",
        blank=True,
        null=True,
    )
    ion_subclass = models.ForeignKey(
        IonSubclass,
        models.CASCADE,
        db_column="ion_subclass_id",
        to_field="id",
        related_name="ions",
        blank=True,
        null=True,
    )
    ion_group = models.ForeignKey(
        IonGroup,
        models.CASCADE,
        db_column="ion_group_id",
        to_field="id",
        related_name="ions",
        blank=True,
        null=True,
    )
    ion_subgroup = models.ForeignKey(
        IonSubgroup,
        models.CASCADE,
        db_column="ion_subgroup_id",
        to_field="id",
        related_name="ions",
        blank=True,
        null=True,
    )

    elements = models.ManyToManyField(Element, through="IonElement")
    subunits = models.ManyToManyField("self", through="IonSubunit")
    ion_positions = models.ManyToManyField(IonPosition, through="core.MineralIonPosition")

    class Meta:
        managed = False
        db_table = "ion_log"
        unique_together = (("ion_type_id", "formula"),)

        verbose_name = "Ion"
        verbose_name_plural = "Ions"

    def __str__(self):
        return self.formula

    def ion_formula_html(self):
        return formula_to_html(self.formula)

    def variety_formula_html(self):
        return formula_to_html(self.variety_of.formula)

    ion_formula_html.short_description = "Formula"
    variety_formula_html.short_description = "Variety Formula"


class IonElement(BaseModel):

    ion = models.ForeignKey(Ion, models.CASCADE, db_column="ion_id", to_field="id")
    element = models.ForeignKey(
        Element,
        models.CASCADE,
        db_column="element_id",
        to_field="id",
        related_name="ions",
    )

    class Meta:
        managed = False
        db_table = "ion_element"
        unique_together = (("ion", "element"),)

        verbose_name = "Ion Element"
        verbose_name_plural = "Ion Elements"

    def __str__(self):
        return self.ion


class IonSubunit(BaseModel):

    ion = models.ForeignKey(Ion, models.CASCADE, db_column="ion_id", to_field="id")
    subunit = models.ForeignKey(Ion, models.CASCADE, db_column="subunit_id", to_field="id", related_name="ions")

    class Meta:
        managed = False
        db_table = "ion_subunit"
        unique_together = (("ion", "subunit"),)

        verbose_name = "Ion Subunit"
        verbose_name_plural = "Ion Subunits"

    def __str__(self):
        return self.subunit
