import uuid
import re
from decimal import *

from django.db import models
from django.utils.safestring import mark_safe

########## LIST TABLES ##########

class NuxtTabs(models.Model):
    tab_id = models.AutoField(primary_key=True)
    tab_short_name = models.CharField(max_length=50, null=False, unique=True)
    tab_long_name = models.TextField(null=False)

    class Meta:
        managed = False
        db_table = 'nuxt_tabs'
    
    def __str__(self):
        return self.tab_short_name

class NsClass(models.Model):
    id_class = models.SmallIntegerField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_class'
        verbose_name_plural = 'NsClasses'
    
    def __str__(self):
        return '{id_class} - {description}'.format(
                id_class=str(self.id_class),
                description=self.description
            )

class NsSubclass(models.Model):
    id = models.AutoField(primary_key=True)
    id_class = models.ForeignKey(NsClass, models.CASCADE, db_column='id_class', to_field='id_class')
    id_subclass = models.CharField(max_length=4, unique=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_subclass'
        unique_together = (('id_class', 'id_subclass'),)
        verbose_name_plural = 'NsSubclasses'

    def __str__(self):
        return '{id_subclass} - {description}'.format(
                id_subclass=self.id_subclass,
                description=self.description
            )
        
class NsFamily(models.Model):
    id = models.AutoField(primary_key=True)
    id_class = models.ForeignKey(NsClass, models.CASCADE, db_column='id_class', to_field='id_class')
    id_subclass = models.ForeignKey(NsSubclass, models.CASCADE, db_column='id_subclass', to_field='id_subclass')
    id_family = models.CharField(max_length=5, unique=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_family'
        unique_together = (('id_class', 'id_subclass', 'id_family'),)
        verbose_name_plural = 'NsFamilies'

    def __str__(self):
        return '{id_family} - {description}'.format(
                id_family=self.id_family,
                description=self.description
            )


class StatusList(models.Model):
    status_id = models.FloatField(primary_key=True)
    description_group = models.CharField(max_length=100)
    description_long = models.TextField(blank=True, null=True)
    description_short = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'status_list'
        verbose_name_plural = 'StatusList'
    
    def __str__(self):
        return '{0} - {1}'.format(self.status_id, self.description_short)

class RelationList(models.Model):
    relation_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=200, null=False)
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relation_list'
        verbose_name_plural = 'RelationList'

    def __str__(self):
        return '{0}'.format(self.type)

class CountryList(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=200, null=False)
    alpha_2 = models.CharField(max_length=10, null=True)
    alpha_3 = models.CharField(max_length=10, null=True)
    country_code = models.IntegerField(null=True)
    region = models.CharField(max_length=100, null=True)
    sub_region = models.CharField(max_length=100, null=True)
    intermediate_region = models.CharField(max_length=100, null=True)

    class Meta:
        managed = False
        db_table = 'country_list'
        verbose_name_plural = 'CountryList'

    def __str__(self):
        return self.country_name

class NationalityList(models.Model):
    nationality_id = models.AutoField(primary_key=True)
    nationality_name = models.CharField(max_length=200, null=False)
    note = models.TextField(null=True)

    class Meta: 
        managed = False
        db_table = 'nationality_list'
        verbose_name_plural = 'NationalityList'

    def __str__(self):
        return self.nationality_name


###### ELEMENT TABLES #######


class goldschmidtClassList(models.Model):
    goldschmidt_class_id = models.AutoField(primary_key=True)
    goldschmidt_class_name = models.CharField(max_length=20, null=False, unique=True)

    class Meta:
        managed = False
        db_table = 'goldschmidt_class_list'
        verbose_name_plural = 'goldschmidtClassList'

    def __str__(self):
        return self.goldschmidt_class_name

class BondingTypeList(models.Model):
    bonding_type_id = models.AutoField(primary_key=True)
    bonding_type_name = models.CharField(max_length=50, null=False, unique=True)

    class Meta:
        managed = False
        db_table = 'bonding_type_list'
        verbose_name_plural = 'BondingTypeList'

    def __str__(self):
        return self.bonding_type_name

class PhaseStateList(models.Model):
    phase_state_id = models.AutoField(primary_key=True)
    phase_state_name = models.CharField(max_length=20, null=False, unique=True)

    class Meta:
        managed = False
        db_table = 'phase_state_list'
        verbose_name_plural = 'PhaseStateList'

    def __str__(self):
        return self.phase_state_name

class ChemicalGroupList(models.Model):
    chemical_group_id = models.AutoField(primary_key=True)
    chemical_group_name = models.CharField(max_length=50, null=False, unique=True)

    class Meta:
        managed = False
        db_table = 'chemical_group_list'
        verbose_name_plural = 'ChemicalGroupList'

    def __str__(self):
        return self.chemical_group_name


class ElementList(models.Model):
    element_id = models.AutoField(primary_key=True)
    element = models.CharField(max_length=2, null=False)
    name = models.CharField(max_length=20, null=False)
    atomic_number = models.IntegerField(null=False)
    name_alternative = models.CharField(max_length=20, null=True)
    atomic_mass = models.DecimalField(max_digits=15, decimal_places=12, null=False)
    atomic_mass_standard_uncertainty = models.IntegerField(null=True)
    electronic_configuration = models.CharField(max_length=30, null=False)
    cpk_hex_color = models.CharField(max_length=6, null=True)
    goldschmidt_class_id = models.ForeignKey(goldschmidtClassList, models.CASCADE, db_column='goldschmidt_class_id', to_field='goldschmidt_class_id', related_name='goldschmidt_class')
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
    phase_state_id = models.ForeignKey(PhaseStateList, models.CASCADE, db_column='phase_state_id', to_field='phase_state_id', related_name='phase_state')
    bonding_type_id = models.ForeignKey(BondingTypeList, models.CASCADE, db_column='bonding_type_id', to_field='bonding_type_id', related_name='bonding_type')
    melting_point = models.IntegerField(null=True)
    boiling_point = models.IntegerField(null=True)
    density = models.DecimalField(max_digits=8, decimal_places=6, null=True)
    chemical_group_id = models.ForeignKey(ChemicalGroupList, models.CASCADE, db_column='chemical_group_id', to_field='chemical_group_id', related_name='chemical_group')
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

    class Meta:
        managed = False
        db_table = 'element_list'
        verbose_name_plural = 'ElementList'

    def __str__(self):
        return self.element



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
        # statuses = MsSpecies.objects.all().prefetch_related(Prefetch('mineral_status', queryset=MineralStatus.objects.select_related('mineral_id','status_id')))
        # print(statuses)
        if self.statuses:
            return self.statuses #[status.status_id for status in self.status.all()]

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
    relation_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='relation_id', related_name='related_relations')
    direct_relation = models.BooleanField(null=False)
    relation_type_id = models.ForeignKey(RelationList, models.CASCADE, db_column='relation_type_id', related_name='related_type', null=False, blank=False)
    relation_note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mineral_relation'
        unique_together = (('mineral_id', 'relation_id', 'relation_type_id', 'direct_relation',))
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
    mineral_id = models.OneToOneField(MineralLog, models.CASCADE, db_column='mineral_id', primary_key=True, related_name='history')
    discovery_year_min = models.IntegerField(blank=True, null=True)
    discovery_year_max = models.IntegerField(blank=True, null=True)
    discovery_year_note = models.TextField(blank=True, null=True)
    first_usage_date = models.TextField(blank=True, null=True)
    first_known_use = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # @property
    def get_discovery_year(self):
        if (self.discovery_year_max == None):
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

class GrHierarchy(models.Model):
    id = models.AutoField(primary_key=True)
    supergroup_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='supergroup_id', related_name='supergroup')
    group_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='group_id', related_name='group')
    subgroup_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='subgroup_id', related_name='subgroup')
    root_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='root_id', related_name='root')
    serie_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='serie_id', related_name='serie')
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='mineral_test')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False,
        db_table = 'gr_hierarchy'
        verbose_name_plural = 'GrHierarchy'


####### Names db tables go here ###########

class MineralNamePerson(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='person')
    person = models.CharField(max_length=200, null=False)
    born = models.IntegerField(null=True)
    died = models.IntegerField(null=True)
    role = models.TextField(null=True)
    gender = models.CharField(max_length=1, choices=(
        ('M','Male',),
        ('F', 'Female',)
    ))
    nationality_id = models.ForeignKey(NationalityList, models.CASCADE, db_column='nationality_id')

    class Meta:
        managed = False
        db_table = 'mineral_name_person'
        unique_together = (('mineral_id', 'nationality_id'),)
        verbose_name_plural = 'MineralNamePerson'

    def __str__(self):
        return '{person} ({born}-{died}); {nationality}'.format(
            person=self.person,
            born=self.born,
            died=self.died,
            nationality=self.nationality_id
        )

class LanguageList(models.Model):
    language_id=models.AutoField(primary_key=True)
    language_name=models.CharField(max_length=200, unique=True, null=False)
    language_group=models.CharField(max_length=200,null=True)
    other_names=models.CharField(max_length=200,null=True)
    type=models.CharField(max_length=200,null=True)
    scope=models.CharField(max_length=200,null=True)
    standard_639_1=models.CharField(max_length=100,null=True)
    standard_639_2=models.CharField(max_length=100,null=True)
    standard_639_3=models.CharField(max_length=100,null=True)
    standard_639_5=models.CharField(max_length=100,null=True)

    class Meta:
        managed=False
        db_table='language_list'
        verbose_name_plural = 'LanguageList'
    
    def __str__(self):
        return self.language_name


class MineralNameLanguage(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='name_language')
    language_id = models.ForeignKey(LanguageList, models.CASCADE, db_column='language_id', related_name='language')
    meaning = models.TextField(null=True)
    stem_1 = models.TextField(null=True)
    stem_2 = models.TextField(null=True)
    stem_3 = models.TextField(null=True)

    class Meta:
        managed=False
        db_table = 'mineral_name_language'
        unique_together = (('mineral_id', 'language_id'),)
        verbose_name_plural = 'MineralNameLanguage'

    def __str__(self):
        return self.language_id

class MineralNameInstitution(models.Model):
    id = models.AutoField(primary_key=True)
    mineral_id = models.ForeignKey(MineralLog, models.CASCADE, db_column='mineral_id', related_name='name_institution')
    institution_name = models.TextField(null=False)
    note = models.TextField(null=True, blank=True)
    country_id = models.ForeignKey(CountryList, models.CASCADE, db_column='country_id')
    
    class Meta:
        managed = False
        db_table = 'mineral_name_institution'
        verbose_name_plural = 'MineralNameInstitution'

    def __str__(self):
        return '{} - {}'.format(self.country_id, self.institution_name)