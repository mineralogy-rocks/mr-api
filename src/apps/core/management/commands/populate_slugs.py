# -*- coding: UTF-8 -*-
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from ...models.mineral import Mineral
from ...utils import unique_slugify


class Command(BaseCommand):

    def _slugify(self, cls, field):
        for obj in cls.objects.all():
            unique_slugify(obj, getattr(obj, field))
            obj.save()
        return

    def handle(self, *args, **options):
        try:
            self._slugify(Mineral, 'name')
        except Exception as e:
            raise CommandError(e)
