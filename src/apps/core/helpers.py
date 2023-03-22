# -*- coding: UTF-8 -*-
from .models.mineral import MineralRelation, MineralStatus


def get_or_create_relation(mineral, relation, status, status_group_id, direct_status=True):

    _match_status = MineralStatus.objects.filter(
        status__group=status_group_id,
        mineral=mineral,
        direct_status=direct_status,
    )
    _status_exists = _match_status.exists()

    # If mineral status with a status group exists, check if relation exists,
    # create relation with status="uncertain .." if not
    if not _status_exists or (_status_exists and not _match_status.filter(relations=relation).exists()):
        _status, _ = MineralStatus.objects.get_or_create(status=status,
                                                        mineral=mineral,
                                                        direct_status=direct_status,
                                                        defaults={
                                                            'needs_revision': True,
                                                        })
        MineralRelation.objects.create(mineral=mineral, status=_status, relation=relation)
        return True
    return False
