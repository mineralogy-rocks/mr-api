# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...tasks import calculate_inherited_props

BATCH_SIZE = 100


class Command(BaseCommand):
    help = "Populate props inherited from parent minerals"

    def handle(self, *args, **options):
        try:
            calculate_inherited_props(batch_size=BATCH_SIZE)
        except Exception as e:
            raise CommandError(e)
