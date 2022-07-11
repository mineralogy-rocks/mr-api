# -*- coding: UTF-8 -*-
import uuid

from django.urls import reverse
from django.db import models
from django.db.models import F, Q, Count, OuterRef
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.functions import JSONObject

from ..utils import formula_to_html
from .base import BaseModel, Nameable, Creatable, Updatable
from .core import NsClass, NsSubclass, NsFamily, Status, Country, RelationType
from .ion import Ion, IonPosition
from .crystal import CrystalSystem, CrystalClass, SpaceGroup



class Mineral(Nameable, Creatable, Updatable):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    formula = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    ns_class = models.ForeignKey(NsClass, models.CASCADE, db_column='ns_class', to_field='id', blank=True, null=True)
    ns_subclass = models.ForeignKey(NsSubclass, models.CASCADE, db_column='ns_subclass', to_field='id', blank=True, null=True)
    ns_family = models.ForeignKey(NsFamily, models.CASCADE, db_column='ns_family', to_field='id', blank=True, null=True, related_name='minerals')
    ns_mineral = models.CharField(max_length=10, blank=True, null=True)

    discovery_countries = models.ManyToManyField(Country, through='MineralCountry')
    statuses = models.ManyToManyField(Status, through='MineralStatus')

    impurities = models.ManyToManyField(Ion, through='MineralImpurity', related_name='impurities')
    ion_positions = models.ManyToManyField(IonPosition, through='MineralIonPosition')
    crystal_systems = models.ManyToManyField(CrystalSystem, through='MineralCrystallography')

    class Meta:
        managed = False
        db_table = 'mineral_log'
        ordering = ['name',]

        verbose_name = 'Mineral'
        verbose_name_plural = 'Minerals'

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('core:mineral-detail', kwargs={'pk': self.id})


    def ns_index(self):
        if self.ns_class:
            return "{ns_class}.{ns_subclass}{ns_family}.{ns_mineral}".format(
                ns_class = str(self.ns_class.id),
                ns_subclass = str(self.ns_subclass.ns_subclass)[-1] if self.ns_subclass != None else '0',
                ns_family = str(self.ns_family.ns_family)[-1] if self.ns_family != None else '0',
                ns_mineral = str(self.ns_mineral) if self.ns_mineral != None else '0'
            )
        else:
            return None


    def formula_html(self):
        return formula_to_html(self.formula)


    def _statuses(self):
        if self.statuses:
            return '; '.join([str(status.status.status_id) for status in self.statuses.all()])

    ns_index.short_description = 'Nickel-Strunz Index'
    formula_html.short_description = 'Formula'
    _statuses.short_description = 'Mineral Statuses'



class MineralStatus(BaseModel, Creatable, Updatable):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id')
    status = models.ForeignKey(Status, models.CASCADE, db_column='status_id', related_name='minerals')

    class Meta:
        managed = False
        db_table = 'mineral_status'
        unique_together = (('mineral', 'status'),)

        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'

    def __str__(self):
        return '{} - {}'.format(self.mineral, self.status)



class MineralRelation(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id', related_name='relations')
    status = models.ForeignKey(MineralStatus, on_delete=models.CASCADE, db_column='mineral_status_id')
    relation = models.ForeignKey(Mineral, models.CASCADE, db_column='relation_id', related_name='inverse_relations')
    relation_type = models.ForeignKey(RelationType, models.CASCADE, db_column='relation_type_id', null=False, blank=False)

    relation_note = models.TextField(blank=True, null=True)
    direct_relation = models.BooleanField(null=False)

    class Meta:
        managed = False
        db_table = 'mineral_relation'
        unique_together = (('mineral', 'status', 'relation', 'relation_type', 'relation_note', 'direct_relation',))

        verbose_name = 'Relation'
        verbose_name_plural = 'Relations'

    def __str__(self):
        return self.relation.name



class MineralImpurity(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id')
    ion = models.ForeignKey(Ion, models.CASCADE, db_column='ion_id')
    ion_quantity = models.CharField(max_length=30, null=True, blank=True)
    rich_poor = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'mineral_impurity'

        verbose_name = 'Impurity'
        verbose_name_plural = 'Impurities'

    def __str__(self):
        return '{} - {}'.format(self.ion, self.ion_quantity)



class MineralIonTheoretical(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id', related_name='ions_theoretical')
    ion = models.ForeignKey(Ion, models.CASCADE, db_column='ion_id', related_name='minerals_theoretical')

    class Meta:
        managed = False
        db_table = 'mineral_ion_theoretical'
        unique_together = (('mineral', 'ion'),)

        verbose_name = 'Theoretical Ion'
        verbose_name_plural = 'Theoretical Ions'

    def __str__(self):
        return self.ion.formula



class MineralCrystallography(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id', related_name='crystallography')
    crystal_system = models.ForeignKey(CrystalSystem, models.CASCADE, db_column='crystal_system_id', related_name='minerals')
    crystal_class = models.ForeignKey(CrystalClass, models.CASCADE, db_column='crystal_class_id', null=True, default=None)
    space_group = models.ForeignKey(SpaceGroup, models.CASCADE, db_column='space_group_id', null=True, default=None)
    a = models.FloatField(blank=True, null=True, default=None)
    b = models.FloatField(blank=True, null=True, default=None)
    c = models.FloatField(blank=True, null=True, default=None)
    alpha = models.FloatField(blank=True, null=True, default=None)
    gamma = models.FloatField(blank=True, null=True, default=None)
    z = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        managed = False
        db_table = 'mineral_crystallography'

        verbose_name = 'Crystallography'
        verbose_name_plural = 'Crystallographies'

    def __str__(self):
        return self.crystal_system.name



class MineralCountry(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id')
    country = models.ForeignKey(Country, models.CASCADE, db_column='country_id', related_name='minerals')

    note = models.TextField(db_column='note', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mineral_country'
        unique_together = (('mineral', 'country'),)

        verbose_name = 'Discovery Country'
        verbose_name_plural = 'Discovery Countries'

    def __str__(self):
        note = f' ({self.note})' if self.note else ''
        return f'{self.country.name}{note}'



class MineralHistory(BaseModel):

    mineral = models.OneToOneField(Mineral, models.CASCADE, db_column='mineral_id', related_name='history')
    discovery_year_min = models.IntegerField(blank=True, null=True)
    discovery_year_max = models.IntegerField(blank=True, null=True)
    discovery_year_note = models.TextField(blank=True, null=True)

    certain = models.BooleanField(null=False, default=True)
    first_usage_date = models.TextField(blank=True, null=True)
    first_known_use = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mineral_history'
        verbose_name_plural = 'MineralHistory'

    @property
    def discovery_year(self):
        if self.discovery_year_min and self.discovery_year_max:
            return "{}-{}".format(str(self.discovery_year_min), str(self.discovery_year_max))
        return self.discovery_year_min



class MineralHierarchy(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id', related_name='parents_hierarchy')
    parent = models.ForeignKey(Mineral, models.CASCADE, db_column='parent_id', null=True, related_name='children_hierarchy')

    class Meta:
        managed = False
        db_table = 'mineral_hierarchy'
        unique_together = (('mineral', 'parent'),)

        verbose_name = 'Hierarchy'
        verbose_name_plural = 'Hierarchies'

    def __str__(self):
        return self.mineral.name



class MineralIonPosition(BaseModel):

    mineral = models.ForeignKey(Mineral, models.CASCADE, db_column='mineral_id', to_field='id', related_name='ions')
    position = models.ForeignKey(IonPosition, models.CASCADE, db_column='ion_position_id', to_field='id')
    ion = models.ForeignKey(Ion, models.CASCADE, db_column='ion_id', to_field='id', related_name='mineral_positions')
    quantity = models.TextField(blank=True, null=True, db_column='ion_quantity')

    class Meta:
        managed = False
        db_table = 'mineral_ion_position'
        ordering = ['mineral',]

        verbose_name = 'Mineral Ions'
        verbose_name_plural = 'Minerals Ions'

    def __str__(self):
        return self.mineral.name
