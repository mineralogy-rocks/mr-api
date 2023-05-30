DROP MATERIALIZED VIEW IF EXISTS mineral_hierarchy_view;

CREATE MATERIALIZED VIEW mineral_hierarchy_view AS
SELECT
	row_number() OVER () AS id,
	temp_.id AS mineral_id,
  temp_.mineral_id AS relation_id,
  temp_.is_parent FROM (
  SELECT ml.id, children.mineral_id, TRUE AS is_parent
  FROM mineral_log ml
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
              WHERE parent_id = ml.id
          UNION
              SELECT
                  e.id,
                  e.mineral_id,
                  e.parent_id
              FROM
                  mineral_hierarchy e
              INNER JOIN HIERARCHY h ON h.mineral_id = e.parent_id
          )
              SELECT
                  h.mineral_id
              FROM
                  HIERARCHY h WHERE h.mineral_id <> ml.id
      ) temp_
  ) AS children
  UNION
  SELECT ml.id, children.mineral_id, FALSE AS is_parent FROM
  mineral_log ml
  CROSS JOIN LATERAL (
      SELECT
      temp_.parent_id AS mineral_id
          FROM
              (
          WITH RECURSIVE HIERARCHY AS (
              SELECT
                  id,
                  mineral_id,
                  parent_id
              FROM
                  mineral_hierarchy
              WHERE mineral_id = ml.id
          UNION
              SELECT
                  e.id,
                  e.mineral_id,
                  e.parent_id
              FROM
                  mineral_hierarchy e
              INNER JOIN HIERARCHY h ON h.parent_id = e.mineral_id
          )
              SELECT
                  h.parent_id
              FROM
                  HIERARCHY h WHERE h.parent_id <> ml.id
      ) temp_
  ) children
) temp_;


CREATE UNIQUE INDEX ON mineral_hierarchy_view(id);
CREATE INDEX mineral_hierarchy_view_mineral_idx ON mineral_hierarchy_view (mineral_id);
CREATE INDEX mineral_hierarchy_view_relation_idx ON mineral_hierarchy_view (relation_id);
