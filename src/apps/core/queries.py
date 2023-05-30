# -*- coding: UTF-8 -*-


LIST_VIEW_QUERY = """
    SELECT main_table.*,
        (
            SELECT JSONB_BUILD_OBJECT(
                    'id', mh.id,
                    'discovery_year', mh.discovery_year,
                    'discovery_year_note', mh.discovery_year_note,
                    'ima_year', mh.ima_year,
                    'publication_year', mh.publication_year,
                    'approval_year', mh.approval_year,
                    'first_usage_date', mh.first_usage_date,
                    'first_known_use', mh.first_known_use
                )::json
            FROM mineral_history mh
            WHERE mh.mineral_id = main_table.id
        ) AS _history,
        (
            SELECT COALESCE(json_agg(
                JSONB_BUILD_OBJECT(
                    'status_id', sl.status_id,
                    'group', to_jsonb(sgl),
                    'description_short', sl.description_short,
                    'description_long', sl.description_long,
                    'mineral', (
                        SELECT JSONB_BUILD_OBJECT(
                            'slug', ml.slug,
                            'name', ml.name,
                            'statuses', ARRAY(
                                SELECT sl.status_id FROM mineral_status ms
                                INNER JOIN status_list sl ON ms.status_id = sl.id
                                WHERE ms.mineral_id = ml.id AND ms.direct_status
                            )
                        )
                        FROM mineral_log ml
                        WHERE ml.id = mr.relation_id AND ml.id IS NOT NULL
                    )
                ) ORDER BY sl.status_id), '[]'::json ) AS statuses_
            FROM mineral_status ms
            INNER JOIN status_list sl ON ms.status_id = sl.id
            INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
            LEFT JOIN mineral_relation mr on ms.id = mr.mineral_status_id
            WHERE ms.mineral_id = main_table.id and ms.direct_status
        ) AS _statuses,
        CASE WHEN main_table.is_grouping THEN (
                SELECT COALESCE(json_agg(_temp), '[]'::json) FROM (
                    SELECT csl.id, csl.name, COUNT(csl.id) AS count
                    FROM mineral_crystallography mc
                    INNER JOIN crystal_system_list csl ON mc.crystal_system_id = csl.id
                    WHERE mc.mineral_id IN (
                        SELECT mhv.relation_id FROM mineral_hierarchy_view mhv
                        INNER JOIN mineral_status ms ON ms.mineral_id = mhv.relation_id AND ms.direct_status AND ms.status_id = 1
                        WHERE mhv.mineral_id = main_table.id
                        GROUP BY mhv.relation_id
                    )
                    GROUP BY csl.id
                    ORDER BY count DESC, name DESC
                ) _temp
            ) ELSE (
                SELECT COALESCE(json_agg(_temp), '[]'::json) FROM (
                    SELECT csl.id, csl.name
                    FROM mineral_crystallography mc
                    INNER JOIN crystal_system_list csl ON mc.crystal_system_id = csl.id
                    WHERE mc.mineral_id = main_table.id
                ) _temp
            )
        END AS crystal_systems,
        CASE WHEN main_table.is_grouping THEN (
                SELECT COALESCE(json_agg(_temp), '[]'::json) FROM (
                    SELECT cl.id, cl.name, COUNT(cl.id) AS count
                    FROM mineral_country mc
                    INNER JOIN country_list cl ON mc.country_id = cl.id AND cl.id <> 250
                    LEFT JOIN mineral_hierarchy_view mhv ON mc.mineral_id = mhv.relation_id
                    WHERE mhv.mineral_id = main_table.id
                    AND EXISTS (
                        SELECT 1
                        FROM mineral_status ms
                        INNER JOIN status_list sl ON ms.status_id = sl.id
                        WHERE ms.mineral_id = mhv.relation_id AND ms.direct_status AND sl.status_group_id = 11
                    )
                    GROUP BY cl.id
                    ORDER BY count DESC, name DESC
                    LIMIT 5
                ) _temp
            ) ELSE (
                SELECT COALESCE(json_agg(_temp), '[]'::json) FROM (
                    SELECT cl.id, cl.name
                    FROM mineral_country mc
                    INNER JOIN country_list cl ON mc.country_id = cl.id AND cl.id <> 250
                    WHERE mc.mineral_id = main_table.id
                ) _temp
            )
        END AS _discovery_countries,
        CASE WHEN main_table.is_grouping THEN (
                SELECT COALESCE(json_agg(_temp), '[]'::json) FROM (
                        SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id,
                                _inner.count, _inner.is_parent, _inner.group
                        FROM (
                            SELECT COUNT(DISTINCT mhv.relation_id) AS count,
                                    mhv.is_parent,
                                    to_jsonb(sgl) AS group
                            FROM mineral_hierarchy_view mhv
                            INNER JOIN mineral_status ms ON ms.mineral_id = mhv.relation_id
                            INNER JOIN status_list sl ON sl.id = ms.status_id
                            INNER JOIN status_group_list sgl ON sgl.id = sl.status_group_id
                            WHERE ms.direct_status AND mhv.mineral_id = main_table.id AND sgl.id IN (3, 11)
                            GROUP BY sgl.id, mhv.is_parent
                            UNION
                            SELECT COUNT(ml.id),
                            mhv.is_parent,
                            JSONB_BUILD_OBJECT(
                                'id', sl.id + 100,
                                'name', CONCAT(sl.description_short, 's')
                            ) AS group
                            FROM mineral_hierarchy_view mhv
                            INNER JOIN mineral_log ml ON mhv.relation_id = ml.id
                            INNER JOIN mineral_status ms ON ms.mineral_id = ml.id
                            INNER JOIN status_list sl ON ms.status_id = sl.id
                            WHERE ms.direct_status AND mhv.mineral_id = main_table.id AND sl.status_group_id  = 1
                            GROUP BY sl.id, mhv.is_parent
                        ) _inner ORDER BY _inner.count desc
                ) _temp
            ) ELSE (
                SELECT COALESCE(json_agg(_temp), '[]'::json)
                FROM (
                    SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id, FALSE AS is_parent, inner_.count, inner_.group FROM (
                        SELECT COUNT(DISTINCT mr.relation_id) AS count, to_jsonb(sgl) AS group
                        FROM mineral_status ms
                        LEFT JOIN mineral_relation mr ON ms.id = mr.mineral_status_id
                        INNER JOIN status_list sl ON ms.status_id = sl.id
                        INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                        WHERE NOT ms.direct_status AND
                            mr.mineral_id = main_table.id AND
                            sgl.id IN (2, 3)
                        GROUP BY sgl.id
                        UNION
                        SELECT COUNT(ml_.id) AS count, (
                            SELECT to_jsonb(_temp) AS group FROM
                                (
                                    SELECT sgl.id, 'Nickel-Strunz related minerals' AS name FROM status_group_list sgl WHERE sgl.id = 11
                                ) _temp
                            )
                        FROM mineral_log ml_
                        INNER JOIN mineral_status ms ON ms.mineral_id = ml_.id
                        WHERE ms.status_id = 1 AND NOT ms.needs_revision AND ml_.ns_family = main_table.ns_family AND ml_.id <> main_table.id
                        HAVING count(ml_.id) > 0
                        UNION
                        SELECT count(ml.id), JSONB_BUILD_OBJECT(
                            'id', sl.id + 100,
                            'name', CONCAT(sl.description_short, 's')
                            ) AS group
                        FROM mineral_hierarchy_view mhv
                        INNER JOIN mineral_log ml ON mhv.relation_id = ml.id
                        INNER JOIN mineral_status ms ON ms.mineral_id = ml.id
                        INNER JOIN status_list sl ON ms.status_id = sl.id
                        WHERE mhv.mineral_id = main_table.id AND sl.status_group_id  = 1
                        GROUP BY sl.id
                    ) inner_
                ) _temp
            )
        END AS _relations
    FROM ( %s ) AS main_table
"""


GET_RELATIONS_QUERY = """
              SELECT
                    temp.id AS base_mineral,
                    temp.relation_id AS relation,
                    ARRAY(
                        SELECT DISTINCT sl.status_id
                        FROM mineral_status ms
                        INNER JOIN status_list sl ON ms.status_id = sl.id
                        WHERE ms.mineral_id = temp.relation_id AND ms.direct_status
                    ) AS statuses,
                    temp.depth
                FROM (
                    WITH RECURSIVE cte(id, mineral_id, relation_id, DEPTH) AS (
                        SELECT
                            mr.mineral_id,
                            mr.mineral_id,
                            mr.relation_id,
                            0
                        FROM mineral_relation mr
                        INNER JOIN mineral_status ms ON mr.mineral_status_id = ms.id AND ms.direct_status
                        WHERE ms.status_id <> 1 AND mr.mineral_id IN %s
                        UNION
                        SELECT
                            cte.id,
                            mr.mineral_id,
                            mr.relation_id,
                            DEPTH + 1
                        FROM mineral_relation mr
                        INNER JOIN cte ON mr.mineral_id = cte.relation_id
                        INNER JOIN mineral_status ms ON mr.mineral_status_id = ms.id AND ms.direct_status
                    )
                    SELECT cte.* FROM cte
                ) temp;
"""
