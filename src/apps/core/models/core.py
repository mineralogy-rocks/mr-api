from django.db import models

from .base import BaseModel, Nameable


class NsClass(models.Model):

    id = models.SmallIntegerField(primary_key=True)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'ns_class'
        ordering = ['id',]

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
        ordering = ['ns_class', 'ns_subclass',]

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
        ordering = ['ns_class', 'ns_family',]

        verbose_name = 'Nickel-Strunz Family'
        verbose_name_plural = 'Nickel-Strunz Families'

    def __str__(self):
        return '{} - {}'.format(self.ns_family, self.description)



class StatusGroup(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'status_group_list'
        ordering = ['name',]

        verbose_name = 'Status Group'
        verbose_name_plural = 'Status Groups'

    def __str__(self):
        return self.name



class Status(BaseModel):

    status_id = models.FloatField(null=False)
    status_group = models.ForeignKey(StatusGroup, models.CASCADE, db_column='status_group_id', to_field='id')
    description_long = models.TextField(blank=True, null=True)
    description_short = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'status_list'
        ordering = ['status_id',]

        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'

    @property
    def group(self):
        return self.status_group.name


    def __str__(self):
        return '{} - {}'.format(self.status_id, self.description_short)



class RelationType(BaseModel, Nameable):

    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'relation_type_list'

        verbose_name = 'Relation Type'
        verbose_name_plural = 'Relation Types'

    def __str__(self):
        return self.name



class Country(BaseModel, Nameable):

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
