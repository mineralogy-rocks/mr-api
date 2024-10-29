# -*- coding: UTF-8 -*-
import numpy as np
import pandas as pd
from django.db import connection

from .choices import INHERIT_CRYSTAL_SYSTEM
from .choices import INHERIT_FORMULA
from .choices import INHERIT_PHYSICAL_PROPERTIES
from .models.mineral import Mineral
from .models.mineral import MineralInheritance
from .queries import GET_INHERITANCE_PROPS_QUERY

STATUS_SYNONYM = np.arange(2.00, 2.12, 0.01, dtype=np.double)
STATUS_VARIETY = np.arange(4.00, 4.07, 0.01, dtype=np.double)
STATUS_GROUP = np.arange(1.00, 1.50, 0.10, dtype=np.double)
STATUS_POLYTYPE = [3.0]
STATUS_MIXTURE = [8.0]
STATUS_APPROVED = [0.0]


def generate_inheritance_chain(chunk_size=1000):
    # 0. Truncate inheritance table and restart sequence.
    # TODO: move this to end and keep in a transaction
    with connection.cursor() as cursor:
        print("Truncating table {}".format(MineralInheritance._meta.db_table))
        cursor.execute("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;".format(MineralInheritance._meta.db_table))

    # 1. Get all objects that needs to inherit properties
    objects = Mineral.objects.only("id", "name").filter(statuses__group__in=[2, 3]).distinct()
    objects = objects.values_list("id", flat=True)

    # 2. Calculate inheritance chain in batches of chunk_size
    inheritance_chain = pd.DataFrame()
    for batch in range(0, len(objects), chunk_size):
        print("Calculating inheritance chain for batch {} to {}".format(batch, batch + chunk_size))
        _objects = objects[batch : batch + chunk_size]

        # TODO: currently, retrieving parents non-approved by admin and without direct statuses
        with connection.cursor() as cursor:
            cursor.execute(GET_INHERITANCE_PROPS_QUERY, [tuple(_objects)])
            _related_objects = cursor.fetchall()
            _fields = [x[0] for x in cursor.description]
            _related_objects = pd.DataFrame([dict(zip(_fields, x, strict=False)) for x in _related_objects])
        inheritance_chain = pd.concat([inheritance_chain, _related_objects])

    inheritance_chain = inheritance_chain.reset_index(drop=True)
    inheritance_chain["base_statuses"] = inheritance_chain.apply(
        lambda x: [float(_x) for _x in x["base_statuses"]], axis=1
    )
    inheritance_chain["statuses"] = inheritance_chain.apply(lambda x: [float(_x) for _x in x["statuses"]], axis=1)

    # 3. Calculate inherited formulas for all synonyms [2.*] and varieties [4.*].
    #    We only retrieve those entries where child doesn't have formula and a parent has formula.
    _populate_formulas(inheritance_chain)

    # 4. Calculate inherited crystal systems for Structural [4.04] and Uncertain Varieties [4.05].
    #    We only retrieve those entries where child doesn't have crystal system and a parent has crystal system.
    _populate_crystal_systems(inheritance_chain)


def _populate_props(chain: pd.DataFrame, prop_id, prohibited_statuses=None):
    if prohibited_statuses is None:
        prohibited_statuses = []
    if chain.empty:
        return

    _create_objs = []
    # group by base_id and iterate over inheritance chain
    for _item, _props in chain.groupby("base_id"):
        # Filter out prohibited statuses and make sure we do not inherit anything from those species
        _props = _props[
            ~_props["statuses"].apply(
                lambda x: _is_intersect(
                    np.concatenate(prohibited_statuses, dtype=np.float32),
                    np.array(x, dtype=np.float32),
                )
            )
        ]
        if _props.empty:
            continue
        # - b. arrange by depth and get:
        #      I. Base is a variety:
        #        (1) the closest variety or IMA-approved mineral
        #        (2) or default the closest item present
        #      II. Base is a synonym:
        #        TODO: implement
        _props = _props.sort_values(by=["depth"], ascending=True)
        _has_priority = _is_intersect(
            np.concatenate([STATUS_APPROVED, STATUS_VARIETY], dtype=np.float32),
            np.concatenate([*_props.statuses], dtype=np.float32),
        )
        for _prop in _props.itertuples():
            if _has_priority:
                if _is_intersect(
                    np.concatenate([STATUS_APPROVED, STATUS_VARIETY], dtype=np.float32),
                    np.array(_prop.statuses, dtype=np.float32),
                ):
                    _create_objs += [MineralInheritance(mineral_id=_item, prop=prop_id, inherit_from_id=_prop.id)]
                    break
                continue
            _create_objs += [MineralInheritance(mineral_id=_item, prop=prop_id, inherit_from_id=_prop.id)]
            break

    if _create_objs:
        MineralInheritance.objects.bulk_create(_create_objs, batch_size=1000)


def _populate_physical_properties(inheritance_chain: pd.DataFrame):
    _inherited_props = inheritance_chain.loc[
        inheritance_chain.index.where(
            ~inheritance_chain.base_has_physical_properties & inheritance_chain.has_physical_properties
        ).dropna(),
        [
            "base_id",
            "base_name",
            "id",
            "name",
            "base_statuses",
            "statuses",
            "depth",
            "base_has_physical_properties",
            "has_physical_properties",
        ],
    ]
    _inherited_props = _inherited_props[
        _inherited_props["base_statuses"].apply(
            lambda x: _is_intersect(
                np.concatenate([STATUS_SYNONYM, STATUS_VARIETY], dtype=np.float32),
                np.array(x, dtype=np.float32),
            )
        )
    ]
    _populate_props(_inherited_props, INHERIT_PHYSICAL_PROPERTIES, [STATUS_SYNONYM])


def _populate_crystal_systems(inheritance_chain: pd.DataFrame):
    _inherited_props = inheritance_chain.loc[
        inheritance_chain.index.where(
            ~inheritance_chain.base_has_crystallography & inheritance_chain.has_crystallography
        ).dropna(),
        [
            "base_id",
            "base_name",
            "id",
            "name",
            "base_statuses",
            "statuses",
            "depth",
            "base_has_crystallography",
            "has_crystallography",
        ],
    ]
    _inherited_props = _inherited_props[
        _inherited_props["base_statuses"].apply(
            lambda x: _is_intersect(
                np.concatenate([STATUS_SYNONYM, STATUS_VARIETY], dtype=np.float32),
                np.array(x, dtype=np.float32),
            )
        )
    ]
    _populate_props(_inherited_props, INHERIT_CRYSTAL_SYSTEM, [STATUS_SYNONYM, STATUS_POLYTYPE, STATUS_MIXTURE])


def _populate_formulas(inheritance_chain: pd.DataFrame):
    _inherited_props = inheritance_chain.loc[
        inheritance_chain.index.where(~inheritance_chain.base_has_formula & inheritance_chain.has_formula).dropna(),
        ["base_id", "base_name", "id", "name", "base_statuses", "statuses", "depth", "base_has_formula", "has_formula"],
    ]
    _inherited_props = _inherited_props[
        _inherited_props["base_statuses"].apply(
            lambda x: _is_intersect(
                np.concatenate([STATUS_SYNONYM, STATUS_VARIETY, STATUS_POLYTYPE], dtype=np.float32),
                np.array(x, dtype=np.float32),
            )
        )
    ]
    # It is fine to inherit from grouping terms, as those contain general formula definitions.
    # Basically, it is fine to inherit from any term that has formula, except synonyms or mixtures.
    # - a. so make sure we do not inherit from synonyms [2.*], and mixtures [8.0]
    _populate_props(_inherited_props, INHERIT_FORMULA, [STATUS_SYNONYM, STATUS_MIXTURE])


def _is_intersect(x, y):
    return bool(np.intersect1d(x, y).any())
