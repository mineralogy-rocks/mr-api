CREATE TABLE diaphaneity_list (
	diaphaneity_id SERIAL PRIMARY KEY,
	diaphaneity_name varchar(150) NOT NULL UNIQUE
);

CREATE TABLE mineral_diaphaneity_tuple (
	mineral_id uuid NOT NULL,
	diaphaneity_id INT NOT NULL
);