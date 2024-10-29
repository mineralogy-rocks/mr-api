# -*- coding: UTF-8 -*-
from django.db import models

from .base import BaseModel
from .base import Nameable


class GoldschmidtClass(BaseModel, Nameable):
    class Meta:
        db_table = "goldschmidt_class_list"

        verbose_name = "Goldschmidt Class"
        verbose_name_plural = "Goldschmidt Classes"

    def __str__(self):
        return self.name


class BondingType(BaseModel, Nameable):
    class Meta:
        db_table = "bonding_type_list"

        verbose_name = "Bonding Type"
        verbose_name_plural = "Bonding Types"

    def __str__(self):
        return self.name


class PhaseState(BaseModel, Nameable):
    class Meta:
        db_table = "phase_state_list"

        verbose_name = "Phase State"
        verbose_name_plural = "Phase States"

    def __str__(self):
        return self.name


class ChemicalGroup(BaseModel, Nameable):
    class Meta:
        db_table = "chemical_group_list"

        verbose_name = "Chemical Group"
        verbose_name_plural = "Chemical Groups"

    def __str__(self):
        return self.name


class Element(BaseModel):
    element = models.CharField(max_length=2, null=False)
    name = models.CharField(max_length=20, null=False)
    atomic_number = models.IntegerField(null=False)
    name_alternative = models.CharField(max_length=20, null=True)

    atomic_mass = models.DecimalField(max_digits=15, decimal_places=12, null=False)
    atomic_mass_standard_uncertainty = models.IntegerField(null=True)
    electronic_configuration = models.CharField(max_length=30, null=False)
    cpk_hex_color = models.CharField(max_length=6, null=True)
    electronegativity = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    empirical_atomic_radius = models.IntegerField(null=True)
    calculated_atomic_radius = models.IntegerField(null=True)
    van_der_waals_radius = models.IntegerField(null=True)
    covalent_single_bond_atomic_radius = models.IntegerField(null=True)
    covalent_triple_bond_atomic_radius = models.IntegerField(null=True)
    metallic_atomic_radius = models.IntegerField(null=True)
    ion_radius = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    ion_radius_charge = models.CharField(max_length=5, null=True)
    ionization_energy = models.IntegerField(null=True)
    electron_affinity = models.IntegerField(null=True)
    oxidation_states = models.CharField(max_length=50, null=True)
    melting_point = models.IntegerField(null=True)
    boiling_point = models.IntegerField(null=True)
    density = models.DecimalField(max_digits=8, decimal_places=6, null=True)

    crust_crc_handbook = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    crust_kaye_laby = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    crust_greenwood = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    crust_ahrens_taylor = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    crust_ahrens_wanke = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    crust_ahrens_waver = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    upper_crust_ahrens_taylor = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    upper_crust_ahrens_shaw = models.DecimalField(max_digits=11, decimal_places=10, null=True)
    sea_water_crc_handbook = models.DecimalField(max_digits=11, decimal_places=11, null=True)
    sea_water_kaye_laby = models.DecimalField(max_digits=11, decimal_places=11, null=True)
    sun_kaye_laby = models.DecimalField(max_digits=16, decimal_places=11, null=True)
    solar_system_kaye_laby = models.DecimalField(max_digits=16, decimal_places=11, null=True)
    solar_system_ahrens = models.DecimalField(max_digits=16, decimal_places=11, null=True)
    solar_system_ahrens_with_uncertainty = models.DecimalField(max_digits=4, decimal_places=2, null=True)

    natural_isotopes = models.TextField(null=True)
    name_meaning = models.TextField(null=True)
    discovery_year = models.IntegerField(null=True)
    discoverer = models.TextField(null=True)
    application = models.TextField(null=True)
    safety = models.TextField(null=True)
    biological_role = models.TextField(null=True)

    goldschmidt_class = models.ForeignKey(
        GoldschmidtClass,
        models.CASCADE,
        db_column="goldschmidt_class_id",
        to_field="id",
        related_name="elements",
        default=None,
    )
    phase_state = models.ForeignKey(
        PhaseState,
        models.CASCADE,
        db_column="phase_state_id",
        to_field="id",
        related_name="elements",
        default=None,
    )
    bonding_type = models.ForeignKey(
        BondingType,
        models.CASCADE,
        db_column="bonding_type_id",
        to_field="id",
        related_name="elements",
        default=None,
    )
    chemical_group = models.ForeignKey(
        ChemicalGroup,
        models.CASCADE,
        db_column="chemical_group_id",
        to_field="id",
        related_name="elements",
        default=None,
    )

    class Meta:
        db_table = "element_list"

        verbose_name = "ELement"
        verbose_name_plural = "Elements"

    def __str__(self):
        return self.element
