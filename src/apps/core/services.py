
from django.db.models import Q, F, Case, When, BooleanField, Subquery, Value, Min, Exists, Count
from django.db.models.query import QuerySet

from core.models import models as api_models
from core import statuses as statuses

def get_statuses_and_relations(instance: QuerySet) -> list:
    """ 
    The function is used to create a list of descriptive mineral statuses spanning the relations data.
    It proceeds as follows:
        1. Get all statuses assigned to instance, specifically get description_group, description_short and status_id.
        2. Get related minerals if instance status belongs to synonyms, varieties, polytypes or mixtures.
            a. Filter the related minerals by direct_relation=True or None and relation_type_id=1 or None.
        3. Group output by status_group 

    Args:
        instance (Queryset): RelatedManager from MineralLog instance to mineral_status

    Returns:
        list: list of dicts containing the status_id, status_group, status_description, mineral_id and mineral_name
    """
    
    instance_statuses = instance.all() \
        .filter((Q(mineral_id__related_minerals__relation_type_id__in=[1, None]) &
                Q(mineral_id__related_minerals__direct_relation__in=[True, None]))) \
        .values('status_id') \
        .annotate(
            status_count=Count('status_id'),
            status_group=F('status_id__description_group'),
            status_description=F('status_id__description_short'),
            mineral_id=Case(
                When((Q(status_id__gte=statuses.CHEMICAL_SYNONYM) & Q(status_id__lt=statuses.ANTHROPOTYPE_MINERAL)) | (Q(status_id=statuses.MIXTURE_SPECIE)), 
                     then=F('mineral_id__related_minerals__relation_id')),
                default=None,
            ),
            mineral_name=Case(
                When(Q(mineral_id__isnull=False), then=F('mineral_id__related_minerals__relation_id__mineral_name')),
                default=None,
            ),
        ).values('status_id', 'status_group', 'status_description', 'mineral_id', 'mineral_name').distinct()
        
    statuses_descriptions = []
    
    if len(instance_statuses):
        
        for status in instance_statuses:
            print(status)

            local = {}
            local.update({
                'status_id': status['status_id'],
                'group': status['status_group'],
                'description': []
            })
            
            if status['mineral_id']:
                relations = {
                    'mineral_id': status['mineral_id'],
                    'mineral_name': status['mineral_name'],
                    }
                local['relations'] = [relations]
                
            if len(statuses_descriptions) > 0 and status['status_group'] not in set([status['group'] for status in statuses_descriptions]):
                local['description'].append(status['status_description'])
                statuses_descriptions.append(local)
                
            elif len(statuses_descriptions) == 0:
                local['description'].append(status['status_description'])
                statuses_descriptions.append(local)
                
            else:
                query_status = [loc_status for loc_status in statuses_descriptions if loc_status['group'] == status['status_group']][0]
                if status['status_description'] not in query_status['description']:
                    query_status['description'].append(status['status_description'])
                if relations:
                    if 'relations' in query_status.keys() and status['mineral_id'] not in [relation['mineral_id'] for relation in query_status['relations']]:
                        query_status['relations'].append(relations)
                    else:
                        query_status['relations'] = relations
                    
    return statuses_descriptions
