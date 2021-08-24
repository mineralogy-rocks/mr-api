
from django.db.models import Q, F, Case, When, BooleanField, Subquery, Value, Min, Exists, Count

from api.models import models as models

def get_relations(instance) -> list:
    """[summary]

    Args:
        instance ([type]): [description]

    Returns:
        list: list of dicts containing the status_id, status_group, status_description, mineral_id and mineral_name
    """
    relations = instance.all() \
        .filter((Q(mineral_id__related_minerals__relation_type_id=1) | Q(mineral_id__related_minerals__relation_type_id__isnull=True) &
                Q(mineral_id__related_minerals__direct_relation=True) | Q(mineral_id__related_minerals__direct_relation__isnull=True))) \
        .values('status_id') \
        .annotate(
            status_count=Count('status_id'),
            status_group=F('status_id__description_group'),
            status_description=F('status_id__description_short'),
            mineral_id=Case(
                When((Q(status_id__gte=2.0) & Q(status_id__lt=5.0)) | (Q(status_id__gte=8.0) & Q(status_id__lt=9.0)), then=F('mineral_id__related_minerals__relation_id')),
                default=None,
            ),
            mineral_name=Case(
                When(Q(mineral_id__isnull=False), then=F('mineral_id__related_minerals__relation_id__mineral_name')),
                default=None,
            ),
        ).values('status_id', 'status_group', 'status_description', 'mineral_id', 'mineral_name').distinct()
        
    return relations