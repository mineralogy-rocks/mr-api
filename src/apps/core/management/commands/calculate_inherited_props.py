# -*- coding: UTF-8 -*-
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import connection
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q

from ...choices import INHERIT_CHOICES
from ...models.mineral import Mineral
from ...models.mineral import MineralInheritance
from ...models.mineral import MineralCrystallography
from ...queries import GET_INHERITANCE_CHAIN_LIST_QUERY

BATCH_SIZE = 100


class Command(BaseCommand):
    help = "Populate props inherited from parent minerals"

    def calculate_inherited_props(self):
        # 1. Get objects without crystallography or with the inherited one.
        objects = (
            Mineral.objects.only("id", "name")
            .filter(statuses__group__in=[2, 3])
            .distinct()
            .filter(
                Exists(MineralInheritance.objects.filter(mineral=OuterRef("pk"), inherited_from__isnull=False))
                | Q(crystallography__isnull=True)
            )
        )
        objects = objects.values_list("id", flat=True)[:1000]

        # 2. Calculate inheritance chain in batches of BATCH_SIZE
        inheritance_chain = pd.DataFrame()
        for batch in range(0, len(objects), BATCH_SIZE):
            print("Calculating inheritance chain for batch {} to {}".format(batch, batch + BATCH_SIZE))
            _objects = objects[batch : batch + BATCH_SIZE]

            # TODO: currently, retrieving parents non-approved by admin and without direct statuses
            with connection.cursor() as cursor:
                cursor.execute(GET_INHERITANCE_CHAIN_LIST_QUERY, [tuple(_objects)])
                _related_objects = cursor.fetchall()
                _fields = [x[0] for x in cursor.description]
                _related_objects = pd.DataFrame([dict(zip(_fields, x)) for x in _related_objects])
                inheritance_chain = pd.concat([inheritance_chain, _related_objects])

        print(inheritance_chain)

    def handle(self, *args, **options):
        try:
            self.calculate_inherited_props()
        except Exception as e:
            raise CommandError(e)
