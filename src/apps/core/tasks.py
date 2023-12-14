# -*- coding: UTF-8 -*-
import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import connection
from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Q

from .choices import INHERIT_CRYSTAL_SYSTEM
from .models.mineral import Mineral
from .models.mineral import MineralInheritance
from .models.mineral import MineralCrystallography
from .queries import GET_INHERITANCE_PROPS_QUERY

BATCH_SIZE = 100

def calculate_inherited_props(batch_size=100):
    # 1. Get all objects that needs to inherit properties
    objects = (
        Mineral.objects.only("id", "name")
        .filter(statuses__group__in=[3])
        .distinct()
    )
    objects = objects.values_list("id", flat=True)[:100]

    # 2. Calculate inheritance chain in batches of BATCH_SIZE
    inheritance_chain = pd.DataFrame()
    for batch in range(0, len(objects), BATCH_SIZE):
        print("Calculating inheritance chain for batch {} to {}".format(batch, batch + BATCH_SIZE))
        _objects = objects[batch:batch + BATCH_SIZE]

        # TODO: currently, retrieving parents non-approved by admin and without direct statuses
        with connection.cursor() as cursor:
            cursor.execute(GET_INHERITANCE_PROPS_QUERY, [tuple(_objects)])
            _related_objects = cursor.fetchall()
            _fields = [x[0] for x in cursor.description]
            _related_objects = pd.DataFrame([dict(zip(_fields, x)) for x in _related_objects])
            inheritance_chain = pd.concat([inheritance_chain, _related_objects])

    inheritance_chain = inheritance_chain.reset_index(drop=True)
    inheritance_chain['base_statuses'] = inheritance_chain.apply(lambda x: [float(_x) for _x in x['base_statuses']], axis=1)
    inheritance_chain['statuses'] = inheritance_chain.apply(lambda x: [float(_x) for _x in x['statuses']], axis=1)


    # 3. Calculate inherited formulas.
    _inherited_props = inheritance_chain.loc[
        (inheritance_chain["has_formula"] == False) &
        (inheritance_chain["has_parent_formula"] == True)
    ]

    _statuses = np.array([
        4.00, 4.05,
    ])

    _inherited_props = _inherited_props[
        _inherited_props['base_statuses'].apply(lambda x: bool(np.intersect1d(_statuses, x).any()))
    ]

    # group by base_id and iterate over groups
    # for each group, get all formulas and statuses
    for _item in _inherited_props.groupby("base_id"):
        _props = _item[1]

    # _relations = (
    #     _relations.groupby(["base_mineral", "relation", "depth"])
    #     .agg(
    #         {
    #             "formulas": lambda x: list(x),
    #             "statuses": lambda x: list(x)[0] if len(list(x)) else None,
    #         }
    #     )
    #     .reset_index()
    # )
    # _relations = _relations.sort_values(by=["depth"], ascending=True).drop_duplicates(
    #     subset=["base_mineral"], keep="first"
    # )
    # _relations.drop(
    #     columns=[
    #         "relation",
    #         "statuses",
    #         "depth",
    #     ],
    #     inplace=True,
    # )
    # _relations["base_mineral"] = _relations["base_mineral"].astype("str")

    print(_inherited_props)
