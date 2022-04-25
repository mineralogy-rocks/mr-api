import uuid
import re

from django.db import models
from django.utils.safestring import mark_safe

from .base import BaseModel, Nameable, Creatable, Updatable


class NsClass(models.Model):
    
    id = models.SmallIntegerField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_class'
        
        verbose_name = 'Nickel-Strunz Class'
        verbose_name_plural = 'Nickel-Strunz Classes'
    
    def __str__(self):
        return '{} - {}'.format(str(self.id), self.description)



class NsSubclass(BaseModel):
    
    ns_class = models.ForeignKey(NsClass, models.CASCADE, db_column='ns_class', to_field='id')
    ns_subclass = models.CharField(max_length=4, unique=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_subclass'
        unique_together = (('ns_class', 'ns_subclass'),)
        
        verbose_name = 'Nickel-Strunz Subclass'
        verbose_name_plural = 'Nickel-Strunz Subclasses'

    def __str__(self):
        return '{} - {}'.format(self.ns_subclass, self.description)
        
        
        
class NsFamily(BaseModel):
    
    ns_class = models.ForeignKey(NsClass, models.CASCADE, db_column='ns_class', to_field='id')
    ns_subclass = models.ForeignKey(NsSubclass, models.CASCADE, db_column='ns_subclass', to_field='id')
    ns_family = models.CharField(max_length=5, unique=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_family'
        unique_together = (('ns_class', 'ns_subclass', 'ns_family'),)
        
        verbose_name = 'Nickel-Strunz Family'
        verbose_name_plural = 'Nickel-Strunz Families'

    def __str__(self):
        return '{} - {}'.format(self.ns_family, self.description)



class StatusList(BaseModel):
    
    status_id = models.FloatField(null=False)
    description_group = models.CharField(max_length=100)
    description_long = models.TextField(blank=True, null=True)
    description_short = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'status_list'
        
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
    
    def __str__(self):
        return '{} - {}'.format(self.status_id, self.description_short)



class RelationTypeList(BaseModel, Nameable):
    
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relation_type_list'
        
        verbose_name = 'Relation Type'
        verbose_name_plural = 'Relation Types'

    def __str__(self):
        return self.name



class CountryList(BaseModel, Nameable):
    
    alpha_2 = models.CharField(max_length=10, null=True)
    alpha_3 = models.CharField(max_length=10, null=True)
    country_code = models.IntegerField(null=True)
    region = models.CharField(max_length=100, null=True)
    sub_region = models.CharField(max_length=100, null=True)
    intermediate_region = models.CharField(max_length=100, null=True)

    class Meta:
        managed = False
        db_table = 'country_list'
        
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name



class NationalityList(BaseModel, Nameable):

    note = models.TextField(null=True)

    class Meta: 
        managed = False
        db_table = 'nationality_list'
        
        verbose_name = 'Nationality'
        verbose_name_plural = 'Nationalities'

    def __str__(self):
        return self.name



###### IONS TABLES #######



class IonClassList(models.Model):
    ion_class_id = models.AutoField(primary_key=True)
    ion_class_name = models.TextField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'ion_class_list'
        verbose_name_plural = 'IonClassList'

    def __str__(self):
        return self.ion_class_name

class IonSubclassList(models.Model):
    ion_subclass_id = models.AutoField(primary_key=True)
    ion_subclass_name = models.TextField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'ion_subclass_list'
        verbose_name_plural = 'IonSubclassList'

    def __str__(self):
        return self.ion_subclass_name

class IonGroupList(models.Model):
    ion_group_id = models.AutoField(primary_key=True)
    ion_group_name = models.TextField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'ion_group_list'
        verbose_name_plural = 'IonGroupList'

    def __str__(self):
        return self.ion_group_name

class IonSubgroupList(models.Model):
    ion_subgroup_id = models.AutoField(primary_key=True)
    ion_subgroup_name = models.TextField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'ion_subgroup_list'
        verbose_name_plural = 'IonSubgroupList'

    def __str__(self):
        return self.ion_subgroup_name

class IonTypeList(models.Model):
    ion_type_id = models.AutoField(primary_key=True)
    ion_type_name = models.TextField(blank=False, null=False)

    class Meta:
        managed = False
        db_table = 'ion_type_list'
        verbose_name_plural = 'IonTypeList'

    def __str__(self):
        return self.ion_type_name

class IonList(models.Model):
    ion_id = models.AutoField(primary_key=True)
    ion_type_id = models.ForeignKey(IonTypeList, models.CASCADE, db_column='ion_type_id', to_field='ion_type_id', related_name='type')
    ion_name = models.TextField(null=True, blank=True)
    element = models.ManyToManyField(ElementList, through='IonElement', related_name='ion_elements')
    subunit = models.ManyToManyField('self', through='IonSubunit', related_name='ion_subunits')
    formula = models.CharField(max_length=100, null=False)
    formula_with_oxidation = models.CharField(max_length=100, null=True)
    overall_charge = models.CharField(max_length=100, null=True)
    variety_of = models.ForeignKey('self', on_delete=models.CASCADE, db_column='variety_of', to_field='ion_id', null=True, blank=True)
    expressed_as = models.TextField(null=True, blank=True)
    element_or_sulfide = models.BooleanField(null=True, blank=True)
    ion_class_id = models.ForeignKey(IonClassList, models.CASCADE, db_column='ion_class_id', related_name='ion_class', blank=True, null=True)
    ion_subclass_id = models.ForeignKey(IonSubclassList, models.CASCADE, db_column='ion_subclass_id', related_name='ion_subclass', blank=True, null=True)
    ion_group_id = models.ForeignKey(IonGroupList, models.CASCADE, db_column='ion_group_id', related_name='ion_group', blank=True, null=True)
    ion_subgroup_id = models.ForeignKey(IonSubgroupList, models.CASCADE, db_column='ion_subgroup_id', to_field='ion_subgroup_id', related_name='ion_subgroup', blank=True, null=True)
    structure_description = models.TextField(null=True, blank=True)
    geometry = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ion_list'
        unique_together = (('ion_type_id', 'formula'),)
        verbose_name_plural = 'IonList'

    def __str__(self):
        return self.formula #'{}: {}'.format(self.ion_type_id, self.formula)

    def ion_type(self):
        return self.ion_type_id

    def ion_formula_html(self):
        replacements = [
            dict(to_replace=r'(_)(.*?_)', replacement=r'\1<sub>\2</sub>'),
            dict(to_replace=r'(\^)(.*?\^)', replacement=r'\1<sup>\2</sup>'),
            dict(to_replace=r'_', replacement=''),
            dict(to_replace=r'\^', replacement='')
        ]
        parsed = self.formula
        [parsed := re.sub(replacement['to_replace'], replacement['replacement'], parsed) for replacement in replacements]
        return mark_safe(parsed)
        
    ion_formula_html.short_description = 'Ion Formula'

    def variety_formula_html(self):
        replacements = [
            dict(to_replace=r'(_)(.*?_)', replacement=r'\1<sub>\2</sub>'),
            dict(to_replace=r'(\^)(.*?\^)', replacement=r'\1<sup>\2</sup>'),
            dict(to_replace=r'_', replacement=''),
            dict(to_replace=r'\^', replacement='')
        ]
        if self.variety_of:
            parsed = self.variety_of.formula
            [parsed := re.sub(replacement['to_replace'], replacement['replacement'], parsed) for replacement in replacements]
            return mark_safe(parsed)
        else:
            return None

    variety_formula_html.short_description = 'Variety Ion Formula'

class IonElement(models.Model):
    id = models.AutoField(primary_key=True)
    ion_id = models.ForeignKey(IonList, models.CASCADE, db_column='ion_id', related_name='ions')
    element_id = models.ForeignKey(ElementList, models.CASCADE, db_column='element_id', related_name='elements')

    class Meta:
        managed = False
        db_table = 'ion_element'
        unique_together = (('ion_id', 'element_id'),)
        verbose_name_plural = 'IonElement'

    def __str__(self):
        return self.element_id

class IonSubunit(models.Model):
    id = models.AutoField(primary_key=True)
    ion_id = models.ForeignKey(IonList, models.CASCADE, db_column='ion_id', related_name='ion')
    subunit_id = models.ForeignKey(IonList, models.CASCADE, db_column='subunit_id', to_field='ion_id', related_name='subunits')

    class Meta:
        managed = False
        db_table = 'ion_subunit'
        unique_together = (('ion_id', 'subunit_id'),)
        verbose_name_plural = 'IonSubunit'

    def __str__(self):
        return self.subunit_id

class MineralLog(models.Model):

    mineral_id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    mineral_name = models.CharField(unique=True, max_length=200)
    formula = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    id_class = models.ForeignKey(NsClass, models.CASCADE, db_column='id_class', to_field='id_class', related_name='ns_class', blank=True, null=True)
    id_subclass = models.ForeignKey(NsSubclass, models.CASCADE, db_column='id_subclass', to_field='id_subclass', related_name='ns_subclass', blank=True, null=True)
    id_family = models.ForeignKey(NsFamily, models.CASCADE, db_column='id_family', to_field='id_family', related_name='ns_family', blank=True, null=True)
    id_mineral = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    discovery_countries = models.ManyToManyField(CountryList, through='MineralCountry', related_name='mineral_countries')
    statuses = models.ManyToManyField(StatusList, through='MineralStatus', related_name='mineral_statuses')
    relations = models.ManyToManyField('self', through='MineralRelation', related_name='mineral_relations')
    hierarchy = models.ManyToManyField('self', through='MineralHierarchy', related_name='mineral_hierarchy')
    impurities = models.ManyToManyField(IonList, through='MineralImpurity', related_name='mineral_impurities')
    ions_theoretical = models.ManyToManyField(IonList, through='MineralIonTheoretical', related_name='mineral_ions_theoretical')
    name_person = models.ManyToManyField(NationalityList, through='MineralNamePerson', related_name='mineral_name_person')



    # @property
    def get_ns_index(self):
        if self.id_class:
            ns_index = "{id_class}.{id_subclass}{id_family}.{id_mineral}".format(
                id_class = str(self.id_class.id_class),
                id_subclass = str(self.id_subclass.id_subclass)[-1] if self.id_subclass != None else '0',
                id_family = str(self.id_family.id_family)[-1] if self.id_family != None else '0',
                id_mineral = str(self.id_mineral) if self.id_mineral != None else '0'
            )
        else:
            ns_index = None
        return ns_index
        
    get_ns_index.short_description = 'Nickel-Strunz Index'

    def get_statuses(self):
        if self.status:
            return '; '.join([str(status.status_id) for status in self.status.all()])

    get_statuses.short_description = 'Mineral Statuses'

    # @property
    def search_statuses(self):
        if self.statuses:
            return self.statuses

    def mineral_formula_html(self):
        replacements = [
            dict(to_replace=r'(_)(.*?_)', replacement=r'\1<sub>\2</sub>'),
            dict(to_replace=r'(\^)(.*?\^)', replacement=r'\1<sup>\2</sup>'),
            dict(to_replace=r'_', replacement=''),
            dict(to_replace=r'\^', replacement='')
        ]
        if self.formula is not None:
            parsed = self.formula
            [parsed := re.sub(replacement['to_replace'], replacement['replacement'], parsed) for replacement in replacements]
            return mark_safe(parsed)
        else:
            return None
            
    mineral_formula_html.short_description = 'Formula'

    class Meta:
        managed = False
        db_table = 'mineral_log'
        verbose_name_plural = 'MineralLog'

    def __str__(self):
        return self.mineral_name

class MineralStatus(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='mineral_status')
    status_id = models.ForeignKey(StatusList, models.CASCADE, db_column='status_id', related_name='status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'mineral_status'
        unique_together = (('mineral_id', 'status_id'),)
        verbose_name_plural = 'MineralStatus'

    def __str__(self):
        return str(self.mineral_id)


class MineralRelation(models.Model):
    
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='related_minerals')
    mineral_status_id = models.ForeignKey(MineralStatus, on_delete=models.CASCADE, db_column='mineral_status_id', to_field='id', related_name='relations')
    relation_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='relation_id', related_name='related_relations')
    relation_type_id = models.ForeignKey(RelationTypeList, models.CASCADE, db_column='relation_type_id', related_name='related_type', null=False, blank=False)
    relation_note = models.TextField(blank=True, null=True)
    direct_relation = models.BooleanField(null=False)

    class Meta:
        managed = False
        db_table = 'mineral_relation'
        unique_together = (('mineral_id', 'mineral_status_id', 'relation_id', 'relation_type_id', 'relation_note', 'direct_relation',))
        verbose_name_plural = 'MineralRelation'

    def __str__(self):
        return self.relation_id.mineral_name


class MineralImpurity(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='mineral_impurities')
    ion_id = models.ForeignKey(IonList, models.CASCADE, db_column='ion_id', related_name='impurities')
    ion_quantity = models.CharField(max_length=30, null=True, blank=True)
    rich_poor = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'mineral_impurity'
        verbose_name_plural = 'MineralImpurity'

    def __str__(self):
        return '{ion} - {quantity}'.format(ion=self.ion_id, quantity=self.ion_quantity)

class MineralIonTheoretical(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='mineral_ions_theoretical')
    ion_id = models.ForeignKey(IonList, models.CASCADE, db_column='ion_id', related_name='ion_theoretical')

    class Meta:
        managed = False
        db_table = 'mineral_ion_theoretical'
        verbose_name_plural = 'MineralIonTheoretical'

    def __str__(self):
        return '{ion_type}'.format(ion_type=self.ion_id.ion_type_id)

class MineralIonReal(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='mineral_ions_real')
    anion = models.TextField(null=True)
    cation = models.TextField(null=True)
    silicate = models.TextField(null=True)
    other = models.TextField(null=True)

    class Meta:
        managed = False
        db_table = 'mineral_ion_real'
        verbose_name_plural = 'MineralIonReal'

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.anion, self.cation, self.silicate, self.other)

class MineralCountry(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='country_mineral')
    country_id = models.ForeignKey(CountryList, models.CASCADE, db_column='country_id', related_name='country', null=False, blank=False)
    note = models.TextField(db_column='note', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        managed = False
        db_table = 'mineral_country'
        unique_together = (('mineral_id', 'country_id'),)
        verbose_name_plural = 'MineralCountry'

    def __str__(self):
        note = '' if self.note is None else f' ({self.note})'
        return f'{self.country_id.country_name}{note}'


class MineralHistory(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.OneToOneField(MineralLog, models.CASCADE, db_column='mineral_id', related_name='history')
    discovery_year_min = models.IntegerField(blank=True, null=True)
    discovery_year_max = models.IntegerField(blank=True, null=True)
    discovery_year_note = models.TextField(blank=True, null=True)
    certain = models.BooleanField(null=False, default=True)
    first_usage_date = models.TextField(blank=True, null=True)
    first_known_use = models.TextField(blank=True, null=True)

    # @property
    def get_discovery_year(self):
        if not (self.discovery_year_max is None):
            discovery_year = self.discovery_year_min
        else:
            discovery_year = "{discovery_year_min}-{discovery_year_max}".format(
                discovery_year_min=str(self.discovery_year_min),
                discovery_year_max=str(self.discovery_year_max)
        )
        return discovery_year

    class Meta:
        managed = False
        db_table = 'mineral_history'
        verbose_name_plural = 'MineralHistory'


class MineralHierarchy(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='mineral')
    parent_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='parent_id', related_name='parent', null=True)

    class Meta:
        managed = False
        db_table = 'mineral_hierarchy'
        verbose_name_plural = 'MineralHierarchy'

    def __str__(self):
        return self.mineral_id.mineral_name
