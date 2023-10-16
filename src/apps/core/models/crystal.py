# -*- coding: UTF-8 -*-
from django.db import models

from .base import BaseModel
from .base import Nameable


class CrystalSystem(BaseModel):
    name = models.CharField(max_length=30, null=False, unique=True)

    class Meta:
        db_table = "crystal_system_list"
        ordering = [
            "name",
        ]

        verbose_name = "Crystal System"
        verbose_name_plural = "Crystal Systems"

    def __str__(self):
        return self.name


class CrystalClass(BaseModel, Nameable):
    h_m_symbol = models.CharField(max_length=50, blank=True, null=True)
    crystal_system = models.ForeignKey(
        CrystalSystem,
        models.CASCADE,
        db_column="crystal_system_id",
        to_field="id",
        related_name="classes",
        null=True,
        default=None,
    )

    class Meta:
        db_table = "crystal_class_list"
        ordering = [
            "crystal_system",
            "name",
        ]

        verbose_name = "Crystal Class"
        verbose_name_plural = "Crystal Classes"

    def __str__(self):
        return self.name


class SpaceGroup(BaseModel, Nameable):
    crystal_class = models.ForeignKey(
        CrystalClass,
        models.CASCADE,
        db_column="crystal_class_id",
        to_field="id",
        related_name="space_groups",
    )

    class Meta:
        db_table = "space_group_list"
        ordering = [
            "name",
        ]

        verbose_name = "Space Group"
        verbose_name_plural = "Space Groups"

    def __str__(self):
        return self.name
