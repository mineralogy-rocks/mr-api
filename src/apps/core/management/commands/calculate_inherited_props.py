# -*- coding: UTF-8 -*-
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import connection

from ...models.mineral import Mineral
from ...queries import GET_INHERITANCE_CHAIN_LIST_QUERY

# from core.models.mineral import Mineral


class Command(BaseCommand):
    help = "Populate props inherited from parent minerals"

    def calculate_inherited_props(self):
        varieties = Mineral.objects.filter(statuses__group=3).distinct()

        with connection.cursor() as cursor:
            cursor.execute(GET_INHERITANCE_CHAIN_LIST_QUERY, [tuple(varieties.values_list("id", flat=True))])
            _related_objects = cursor.fetchall()
            _fields = [x[0] for x in cursor.description]
            _related_objects = pd.DataFrame([dict(zip(_fields, x)) for x in _related_objects])

    def handle(self, *args, **options):
        try:
            self.calculate_inherited_props()
        except Exception as e:
            raise CommandError(e)
