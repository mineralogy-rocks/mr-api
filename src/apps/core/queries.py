relations_query = """
        (
            SELECT COALESCE(jsonb_agg(temp_), '[]'::jsonb)
            FROM (
                SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id, counts, status_group FROM (
                    SELECT COUNT(mr.id) AS counts, to_jsonb(sgl) AS status_group
                    FROM mineral_status ms
                    LEFT JOIN mineral_relation mr ON ms.id = mr.mineral_status_id
                    INNER JOIN status_list sl ON ms.status_id = sl.id
                    INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                    WHERE ms.direct_status AND
                        ms.mineral_id = mineral_log.id AND
                        sgl.id IN (1, 4)
                    GROUP BY sgl.id
                    UNION
                    SELECT count(ml_.id) AS counts, (SELECT to_jsonb(sgl) AS status_group FROM status_group_list sgl WHERE sgl.id = 11)
                    FROM ns_family nf
                    INNER JOIN mineral_log ml_ ON nf.id = ml_.ns_family
                    INNER JOIN mineral_status ms ON ms.mineral_id = ml_.id
                    INNER JOIN status_list sl ON ms.status_id = sl.id
                    INNER JOIN status_group_list sgl ON sl.status_group_id = sgl.id
                    WHERE sgl.id = 11 AND nf.id = mineral_log.ns_family AND ml_.id <> mineral_log.id
                    HAVING count(ml_.id) > 0
                ) inner_
            ) temp_
        )
        """
grouping_relations_query = """
        (
            SELECT COALESCE(jsonb_agg(temp_), '[]'::jsonb)
            FROM (
                    WITH RECURSIVE hierarchy as (
                        SELECT
                            id,
                            mineral_id,
                            parent_id
                        FROM mineral_hierarchy
                        WHERE mineral_id = mineral_log.id
                        UNION
                        SELECT
                            e.id,
                            e.mineral_id,
                            e.parent_id
                        FROM mineral_hierarchy e
                        INNER JOIN hierarchy h ON h.mineral_id = e.parent_id
                    )
                    SELECT (ROW_NUMBER() OVER (ORDER BY (SELECT 1))) AS id,
                            count(h.mineral_id) AS counts,
                            to_jsonb(sgl) AS status_group
                    FROM hierarchy h
                    INNER JOIN mineral_status ms ON ms.mineral_id = h.mineral_id
                    INNER JOIN status_list sl ON sl.id = ms.status_id
                    INNER JOIN status_group_list sgl ON sgl.id = sl.status_group_id
                    WHERE h.parent_id IS NOT NULL AND sgl.id IN (3, 4, 11)
                    GROUP BY sgl.id
            ) temp_
        )
        """

grouping_discovery_countries_query = """
        (
            SELECT COALESCE(json_agg(temp_), '[]'::json) FROM (
                SELECT cl.id, cl.name, count(cl.id) AS counts
                FROM mineral_country mc
                INNER JOIN country_list cl ON mc.country_id = cl.id
                INNER JOIN mineral_hierarchy mh ON mh.mineral_id = mc.mineral_id
                WHERE mh.parent_id = mineral_log.id
                AND cl.id <> 250
                GROUP BY cl.id
                ORDER BY counts DESC, name DESC
                LIMIT 5
            ) temp_
        )
        """
