ALTER TABLE mineral_log ADD COLUMN description TEXT DEFAULT NULL,
						ADD COLUMN mindat_id int DEFAULT NULL,
						ADD COLUMN ima_symbol varchar(12) DEFAULT NULL;

ALTER TABLE mineral_history ADD COLUMN discovery_year int DEFAULT NULL,
							ADD COLUMN ima_year int DEFAULT NULL,
							ADD COLUMN publication_year int DEFAULT NULL,
							ADD COLUMN approval_year int DEFAULT NULL;

CREATE TABLE formula_source_list(
	id serial PRIMARY KEY,
	name varchar(100) NOT NULL,
	url varchar(100) DEFAULT null
);

INSERT INTO formula_source_list(name, url) VALUES ('mineralogy.rocks', 'https://mineralogy.rocks/'),
('mindat.org', 'https://www.mindat.org/'), ('IMA', 'https://rruff.info/');

CREATE TABLE mineral_formula(
	id serial PRIMARY KEY,
	mineral_id uuid REFERENCES mineral_log(id) ON UPDATE CASCADE ON DELETE CASCADE,
	formula varchar(1000) DEFAULT NULL,
	note TEXT DEFAULT NULL,
	source_id int REFERENCES formula_source_list(id) ON UPDATE CASCADE ON DELETE RESTRICT,
	show_on_site boolean DEFAULT FALSE,
	created_at timestamp DEFAULT current_timestamp
);

INSERT INTO mineral_formula (mineral_id, formula, source_id, show_on_site)
SELECT ml.id AS mineral_id, ml.formula, 1 AS source_id, TRUE AS show_on_site
FROM mineral_log ml WHERE ml.formula IS NOT NULL;

ALTER TABLE mineral_log DROP COLUMN formula;
