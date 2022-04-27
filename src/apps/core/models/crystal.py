from django.db import models

from .base import BaseModel, Nameable


class CrystalSystemList(BaseModel, Nameable):

    class Meta:
        managed = False
        db_table = 'crystal_system_list'
        ordering = ['name',]

        verbose_name = 'Crystal System'
        verbose_name_plural = 'Crystal Systems'

    def __str__(self):
        return self.name



class CrystalClassList(BaseModel, Nameable):

    h_m_symbol = models.CharField(max_length=50, blank=True, null=True)
    crystal_system = models.ForeignKey(CrystalSystemList, models.CASCADE, db_column='crystal_system_id', to_field='id', related_name='classes')

    class Meta:
        managed = False
        db_table = 'crystal_class_list'
        ordering = ['crystal_system', 'name',]

        verbose_name = 'Crystal Class'
        verbose_name_plural = 'Crystal Classes'

    def __str__(self):
        return self.name
