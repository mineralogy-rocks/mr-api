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
                    'description_long', sl.description_long
                ) ORDER BY sl.status_id), '[]'::json ) AS statuses_
            FROM mineral_status ms
            INNER JOIN status_list sl ON ms.status_id = sl.id
            INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
            WHERE ms.mineral_id = main_table.id
        ) AS _statuses,
        CASE WHEN main_table.is_grouping THEN (
                SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                    SELECT csl.id, csl.name, count(csl.id) AS count
                    FROM mineral_crystallography mc
                    INNER JOIN crystal_system_list csl ON mc.crystal_system_id = csl.id
                    LEFT JOIN mineral_hierarchy_view mhv ON mc.mineral_id = mhv.relation_id
                    WHERE mhv.mineral_id = main_table.id
                    GROUP BY csl.id
                    ORDER BY count DESC, name DESC
                ) temp_
            ) ELSE (
                SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                    SELECT csl.id, csl.name
                    FROM mineral_crystallography mc
                    INNER JOIN crystal_system_list csl ON mc.crystal_system_id = csl.id
                    WHERE mc.mineral_id = main_table.id
                ) temp_
            )
        END AS crystal_systems,
        CASE WHEN main_table.is_grouping THEN (
                SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                    SELECT cl.id, cl.name, count(cl.id) AS count
                    FROM mineral_country mc
                    INNER JOIN country_list cl ON mc.country_id = cl.id AND cl.id <> 250
                    LEFT JOIN mineral_hierarchy_view mhv ON mc.mineral_id = mhv.relation_id
                    WHERE mhv.mineral_id = main_table.id
                    GROUP BY cl.id
                    ORDER BY count DESC, name DESC
                    LIMIT 5
                ) temp_
            ) ELSE (
                SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                    SELECT cl.id, cl.name
                    FROM mineral_country mc
                    INNER JOIN country_list cl ON mc.country_id = cl.id AND cl.id <> 250
                    WHERE mc.mineral_id = main_table.id
                ) temp_
            )
        END AS _discovery_countries,
        CASE WHEN main_table.is_grouping THEN (
                SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                        SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id,
                                count(mhv.mineral_id) AS count,
                                to_jsonb(sgl) AS group
                        FROM mineral_hierarchy_view mhv
                        INNER JOIN mineral_status ms ON ms.mineral_id = mhv.relation_id
                        INNER JOIN status_list sl ON sl.id = ms.status_id
                        INNER JOIN status_group_list sgl ON sgl.id = sl.status_group_id
                        WHERE mhv.mineral_id = main_table.id AND sgl.id IN (3, 11)
                        GROUP BY sgl.id
                ) temp_
            ) ELSE (
                SELECT COALESCE(json_agg(temp_), '[]'::json)
                FROM (
                    SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id, inner_.count, inner_.group FROM (
                        SELECT COUNT(mr.id) AS count, to_jsonb(sgl) AS group
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
                            SELECT to_jsonb(temp_) AS group FROM
                                (
                                    SELECT sgl.id, 'Isostructural minerals' AS name FROM status_group_list sgl WHERE sgl.id = 11
                                ) temp_
                            )
                        FROM mineral_log ml_
                        INNER JOIN mineral_status ms ON ms.mineral_id = ml_.id
                        WHERE ms.status_id = 1 AND NOT ms.needs_revision AND ml_.ns_family = main_table.ns_family AND ml_.id <> main_table.id
                        HAVING count(ml_.id) > 0
                    ) inner_
                ) temp_
            )
        END AS _relations,
        (
            SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                SELECT ml.id, ml.name, CONCAT('/mineral/', ml.id::text) AS url
                FROM mineral_hierarchy_view mhv
                INNER JOIN mineral_log ml ON mhv.relation_id = ml.id
                WHERE mhv.mineral_id = main_table.id
                ORDER BY name ASC
                LIMIT 5
            ) temp_
        ) AS _hierarchy
    FROM ( %s ) AS main_table
"""
