CREATE TEXT SEARCH CONFIGURATION mrdict ( COPY = simple );
ALTER TEXT SEARCH CONFIGURATION mrdict
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, simple;

ALTER TABLE mineral_log DROP COLUMN search_vector IF EXIST;
DROP INDEX search_vector_idx IF EXISTS;
ALTER TABLE mineral_log ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (
  setweight(to_tsvector('mrdict', coalesce(name, '')), 'A') ||
  setweight(to_tsvector('mrdict', coalesce(ima_symbol,'')), 'B') ||
  setweight(to_tsvector('mrdict', coalesce(description,'')), 'C')
) STORED;

CREATE INDEX search_vector_idx ON mineral_log USING GIN (search_vector);

