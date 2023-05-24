CREATE OR REPLACE FUNCTION formula_to_html(formula TEXT)
RETURNS TEXT AS $$
DECLARE
    replacements CONSTANT JSONB :=
    '[
        {"to_replace": "(_)(.*?_)", "replacement": "\\1<sub>\\2</sub>"},
        {"to_replace": "(\\^)(.*?\\^)", "replacement": "\\1<sup>\\2</sup>"},
        {"to_replace": "_", "replacement": ""},
        {"to_replace": "\\^", "replacement": ""}
    ]';
    replacement JSONB;
    parsed TEXT := formula;
BEGIN
    IF formula IS NOT NULL THEN
        FOR replacement IN SELECT jsonb_array_elements(replacements) LOOP
            parsed := regexp_replace(parsed, replacement->>'to_replace', replacement->>'replacement', 'g');
        END LOOP;
        RETURN parsed;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql;


UPDATE mineral_formula
SET formula = new.formula
FROM (
	SELECT mf.id, formula_to_html(formula) AS formula
	FROM mineral_formula mf
	WHERE mf.source_id = 1
) new
WHERE mineral_formula.id = new.id;

INSERT INTO formula_source_list (name, url) VALUES ('crystallography.net', 'https://www.crystallography.net/');

CREATE TABLE mineral_structure (
	id serial PRIMARY KEY,
	mineral_id uuid NOT NULL REFERENCES mineral_log(id) ON UPDATE CASCADE ON DELETE CASCADE,
	cod_id int DEFAULT NULL,
	amcsd_id varchar(50) DEFAULT NULL,
	source_id int DEFAULT NULL REFERENCES formula_source_list(id) ON UPDATE CASCADE ON DELETE CASCADE,
	a numeric DEFAULT NULL,
	a_sigma numeric DEFAULT NULL,
	b numeric DEFAULT NULL,
	b_sigma numeric DEFAULT NULL,
	c numeric DEFAULT NULL,
	c_sigma numeric DEFAULT NULL,
	alpha numeric DEFAULT NULL,
	alpha_sigma numeric DEFAULT NULL,
	beta numeric DEFAULT NULL,
	beta_sigma numeric DEFAULT NULL,
	gamma numeric DEFAULT NULL,
	gamma_sigma numeric DEFAULT NULL,
	volume numeric DEFAULT NULL,
	volume_sigma numeric DEFAULT NULL,
	space_group varchar(100) DEFAULT NULL,
	formula varchar(1000) DEFAULT NULL,
	calculated_formula varchar(1000) DEFAULT NULL,
	reference text DEFAULT NULL,
	links TEXT ARRAY,
	note text DEFAULT NULL,
	created_at timestamp DEFAULT current_timestamp,
	updated_at timestamp DEFAULT current_timestamp
);

CREATE TRIGGER mineral_structure_update_date BEFORE
UPDATE ON public.mineral_structure FOR EACH ROW EXECUTE FUNCTION update_timestamp();
