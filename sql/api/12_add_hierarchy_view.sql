CREATE MATERIALIZED VIEW mineral_hierarchy_view AS
SELECT
	row_number() OVER () AS id,
    ml.id AS mineral_id,
    children.mineral_id AS relation_id
FROM
    (
    SELECT
        ml.*,
        EXISTS(
            SELECT 1 FROM mineral_status ms
            INNER JOIN status_list sl ON ms.status_id = sl.id
            WHERE ms.mineral_id = ml.id AND sl.status_group_id = 1
            LIMIT 1
        ) AS "is_grouping"
    FROM
        mineral_log ml) ml
CROSS JOIN LATERAL (
        SELECT
            temp_.mineral_id
        FROM
            (
        WITH RECURSIVE HIERARCHY AS (
            SELECT
                id,
                mineral_id,
                parent_id
            FROM
                mineral_hierarchy
            WHERE
                CASE WHEN ml.is_grouping THEN parent_id = ml.id
                ELSE mineral_id = ml.id
                END
        UNION
            SELECT
                e.id,
                e.mineral_id,
                e.parent_id
            FROM
                mineral_hierarchy e
            INNER JOIN HIERARCHY h ON
                CASE
                    WHEN ml.is_grouping THEN h.mineral_id = e.parent_id
                    ELSE h.parent_id = e.mineral_id
                END
        )
            SELECT
                h.mineral_id
            FROM
                HIERARCHY h
            WHERE h.mineral_id <> ml.id
    ) temp_
) AS children;

CREATE UNIQUE INDEX ON mineral_hierarchy_view(id);

REFRESH MATERIALIZED VIEW CONCURRENTLY mineral_hierarchy_view;
