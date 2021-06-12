from django.db.models import Q, Count, F
from api.models import *

def status_counts(queryset, count_type, view_type='default'):
    """
    A function to grab status_id counts
    Args:
        queryset: MineralStatus.objects
        count_type: 'basic' or 'descriptive'
        view_type: 'default' or 'nested'
    Returns: 
        JSON {
            status_id: ...,
            mineral_counts: ...,
            description_group: ...,
            description_short: ....
        }
    """
    if count_type == 'basic':
        kwargs = {
            'status_id__in': [0, 1.0, 1.1, 1.2, 1.3, 1.4]
        }
    else:
        kwargs = {
            'status_id__isnull': False
        }

    status_filter = Q(**kwargs)
    counts = queryset.select_related('status_id').filter(status_filter).values('status_id').annotate(
            mineral_counts=Count('mineral_id'), 
            description_short=F('status_id__description_short'),
            description_group=F('status_id__description_group')).order_by('status_id').values('status_id', 'mineral_counts', 'description_group', 'description_short')

    if view_type == 'nested':
        groups = list(set([item['description_group'] for item in counts]))
        groups.sort()
        output = []
        for group in groups:
            statuses = [item for item in counts if item['description_group'] == group]
            output.append({ 'group': group, 'statuses': statuses })
        counts = output
        
    return counts


def discovery_year_counts(queryset, min=1800, max=None):
    """
    A function to grab mineral discovery counts
    Args: 
        min: int, min discovery_year
        max: int, max discovery_year
    Returns:
        JSON {
                mineral_counts: ...,
                discovery_year: ...
             }
    """
    kwargs = {
        'discovery_year_min__gte': min
    }
    if max is not None:
        kwargs['discovery_year_min__lte'] = max

    filters = Q(**kwargs)
    counts = queryset.values('discovery_year_min').annotate(mineral_counts=Count('mineral_id'), discovery_year=F('discovery_year_min'))\
                                    .filter(filters).order_by('discovery_year')\
                                    .values('mineral_counts', 'discovery_year')

    return counts

def discovery_country_counts(queryset):
    """
    A function to grab discovery_country counts
    Args:
        queryset: MineralCountry.objects
    Returns: 
        JSON {
            country_id: ...,
            country_name: ...,
            country_iso: ...,
            mineral_count: ....
        }
    """

    counts = queryset.select_related('country_id').values('country_id').annotate(
            country_name=F('country_id__country_name'),
            country_iso=F('country_id__alpha_3'),
            mineral_count=Count('country_id')).order_by('country_name').values('country_id', 'country_name', 'country_iso', 'mineral_count')
        
    return counts
