# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...tasks import calculate_inherited_props

CHUNK_SIZE = 1000


class Command(BaseCommand):
    help = "Populate props inherited from parent minerals"

    def add_arguments(self, parser):
        parser.add_argument(
            "--chunk-size",
            type=int,
            dest="chunk_size",
            default=CHUNK_SIZE,
            help="Chunk size for calculating inheritance chain",
        )

    def handle(self, *args, **options):
        try:
            calculate_inherited_props(chunk_size=CHUNK_SIZE)
        except Exception as e:
            raise CommandError(e)
