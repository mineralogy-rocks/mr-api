# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
from django.db import connection

from .choices import INHERIT_FORMULA
from .models.mineral import Mineral
from .models.mineral import MineralInheritance
from .queries import GET_INHERITANCE_PROPS_QUERY

CHUNK_SIZE = 100
STATUS_SYNONYM = np.arange(2.00, 2.11, 0.01, dtype=np.double)
STATUS_VARIETY = np.arange(4.00, 4.06, 0.01, dtype=np.double)
STATUS_POLYTYPE = [3.0]
STATUS_MIXTURE = [8.0]
STATUS_APPROVED = [0.0]


def calculate_inherited_props(chunk_size=100):
    # 0. Truncate inheritance table and restart sequence.
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;".format(MineralInheritance._meta.db_table))

    # 1. Get all objects that needs to inherit properties
    objects = Mineral.objects.only("id", "name").filter(statuses__group__in=[3]).distinct()
    objects = objects.values_list("id", flat=True)

    # 2. Calculate inheritance chain in batches of BATCH_SIZE
    inheritance_chain = pd.DataFrame()
    for batch in range(0, len(objects), chunk_size):
        print("Calculating inheritance chain for batch {} to {}".format(batch, batch + chunk_size))
        _objects = objects[batch : batch + chunk_size]

        # TODO: currently, retrieving parents non-approved by admin and without direct statuses
        with connection.cursor() as cursor:
            cursor.execute(GET_INHERITANCE_PROPS_QUERY, [tuple(_objects)])
            _related_objects = cursor.fetchall()
            _fields = [x[0] for x in cursor.description]
            _related_objects = pd.DataFrame([dict(zip(_fields, x)) for x in _related_objects])
        inheritance_chain = pd.concat([inheritance_chain, _related_objects])

    inheritance_chain = inheritance_chain.reset_index(drop=True)
    inheritance_chain["base_statuses"] = inheritance_chain.apply(
        lambda x: [float(_x) for _x in x["base_statuses"]], axis=1
    )
    inheritance_chain["statuses"] = inheritance_chain.apply(lambda x: [float(_x) for _x in x["statuses"]], axis=1)

    # 3. Calculate inherited formulas for Chemical [4.00] and Uncertain Varieties [4.05].
    #    We only retrieve those cases where child doesn't have formula and a parent has formula.
    _populate_formulas(inheritance_chain)


def _populate_formulas(inheritance_chain: pd.DataFrame):
    _inherited_props = inheritance_chain.loc[
        inheritance_chain.index.where(~inheritance_chain.base_has_formula & inheritance_chain.has_formula).dropna(),
        ["base_id", "base_name", "id", "name", "base_statuses", "statuses", "depth", "base_has_formula", "has_formula"],
    ]
    _inherited_props = _inherited_props[
        _inherited_props["base_statuses"].apply(lambda x: bool(np.intersect1d([4.00, 4.05], x).any()))
    ]
    if _inherited_props.empty:
        return

    _create_objs = []
    # group by base_id and iterate over inheritance chain
    for _item, _props in _inherited_props.groupby("base_id"):
        # It is fine to inherit from grouping terms, as those contain general formula definitions.
        # - a. make sure we do not inherit from synonyms [2.*], polytypes [3.0], mixtures [8.0]
        _props = _props[
            ~_props["statuses"].apply(
                lambda x: bool(
                    np.intersect1d(
                        np.concatenate([STATUS_SYNONYM, STATUS_POLYTYPE, STATUS_MIXTURE], dtype=np.float32),
                        np.array(x, dtype=np.float32),
                    ).any()
                )
            )
        ]
        if _props.empty:
            continue
        # - b. arrange by depth and get:
        #      I. Base is a chemical variety:
        #        (1) the closest variety
        #        (2) or IMA-approved mineral
        #        (3) or default the closest item present
        #      II. Base is a synonym:
        #        TODO: implement
        _props = _props.sort_values(by=["depth"], ascending=True)
        for _prop in _props.itertuples():
            if bool(
                np.intersect1d(
                    np.concatenate([STATUS_APPROVED, STATUS_VARIETY], dtype=np.float32),
                    np.array(_prop.statuses, dtype=np.float32),
                ).any()
            ):
                _create_objs += [MineralInheritance(mineral_id=_item, prop=INHERIT_FORMULA, inherit_from_id=_prop.id)]
                break
            continue

    if _create_objs:
        _created_objs = MineralInheritance.objects.bulk_create(_create_objs, batch_size=1000)
        print(_created_objs)
