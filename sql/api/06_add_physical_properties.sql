CREATE TABLE diaphaneity_list (
	diaphaneity_id SERIAL PRIMARY KEY,
	diaphaneity_name varchar(150) NOT NULL UNIQUE
);

CREATE TABLE mineral_diaphaneity_tuple (
    id SERIAL PRIMARY KEY,
	mineral_id uuid NOT NULL REFERENCES mineral_log(mineral_id) ON UPDATE CASCADE ON DELETE CASCADE,
	diaphaneity_id INT NOT NULL
);