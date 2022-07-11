DROP TABLE IF EXISTS nuxt_tabs;

/* update ns classification tables */
ALTER TABLE ns_class RENAME COLUMN id_class TO id;

ALTER TABLE ns_subclass RENAME COLUMN id_class TO ns_class;
ALTER TABLE ns_subclass RENAME COLUMN id_subclass TO ns_subclass;

ALTER TABLE ns_family RENAME COLUMN id_class TO ns_class;
ALTER TABLE ns_family RENAME COLUMN id_subclass TO ns_subclass;
ALTER TABLE ns_family RENAME COLUMN id_family TO ns_family;


CREATE TABLE status_group_list(
	id serial PRIMARY KEY,
	name varchar(200) UNIQUE NOT NULL
);
INSERT INTO status_group_list (name) VALUES ('Grouping'), ('Synonyms'), ('Varieties'), ('Polytypes'), ('Obsolete nomenclature'),
											('Anthropotype'), ('Mineraloids'), ('Rocks'), ('Unnamed'), ('Mixtures'), ('IMA minerals');
ALTER TABLE status_list RENAME TO status_list_old;
CREATE TABLE status_list (
	id SERIAL PRIMARY KEY,
	status_id numeric(4,2) NOT NULL,
	status_group_id INT DEFAULT NULL REFERENCES status_group_list ON UPDATE CASCADE,
	description_short varchar(100) NOT NULL,
	description_long TEXT DEFAULT NULL
);

INSERT INTO status_list (status_id, status_group_id, description_short, description_long)
SELECT status_id, status_group_list.id, description_short, description_long FROM status_list_old
LEFT JOIN status_group_list ON status_list_old.description_group = status_group_list.name;

ALTER TABLE mineral_status RENAME TO mineral_status_old;
CREATE TABLE mineral_status (
	id serial PRIMARY KEY,
	mineral_id uuid NOT NULL REFERENCES mineral_log(mineral_id) ON UPDATE CASCADE,
	status_id INT NOT NULL REFERENCES status_list(id) ON UPDATE CASCADE,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  	UNIQUE (mineral_id, status_id)
);
INSERT INTO mineral_status (mineral_id, status_id, created_at, updated_at)
SELECT mso.mineral_id, sl.id, mso.created_at, mso.updated_at FROM mineral_status_old mso
INNER JOIN status_list sl ON sl.status_id = mso.status_id;

ALTER TABLE mineral_relation DROP CONSTRAINT mineral_relation_mineral_status_id_fkey;
DROP TABLE mineral_status_old, status_list_old;
ALTER TABLE mineral_relation ADD CONSTRAINT mineral_relation_mineral_status_id_fkey FOREIGN KEY (mineral_status_id) REFERENCES mineral_status(id) ON UPDATE cascade on delete cascade;

ALTER TABLE relation_type_list RENAME COLUMN relation_type_id TO id;
ALTER TABLE relation_type_list RENAME COLUMN type TO name;

ALTER TABLE country_list RENAME COLUMN country_id TO id;
ALTER TABLE country_list RENAME COLUMN country_name TO name;

ALTER TABLE nationality_list RENAME COLUMN nationality_id TO id;
ALTER TABLE nationality_list RENAME COLUMN nationality_name TO name;

ALTER TABLE goldschmidt_class_list RENAME COLUMN goldschmidt_class_id TO id;
ALTER TABLE goldschmidt_class_list RENAME COLUMN goldschmidt_class_name TO name;

ALTER TABLE bonding_type_list ALTER COLUMN bonding_type_name TYPE varchar(200) USING bonding_type_name::varchar;
ALTER TABLE bonding_type_list RENAME COLUMN bonding_type_id TO id;
ALTER TABLE bonding_type_list RENAME COLUMN bonding_type_name TO name;

ALTER TABLE phase_state_list  ALTER COLUMN phase_state_name TYPE varchar(200) USING phase_state_name::varchar;
ALTER TABLE phase_state_list RENAME COLUMN phase_state_id TO id;
ALTER TABLE phase_state_list RENAME COLUMN phase_state_name TO name;

ALTER TABLE chemical_group_list  ALTER COLUMN chemical_group_name TYPE varchar(200) USING chemical_group_name::varchar;
ALTER TABLE chemical_group_list RENAME COLUMN chemical_group_id TO id;
ALTER TABLE chemical_group_list RENAME COLUMN chemical_group_name TO name;

ALTER TABLE element_list RENAME COLUMN element_id TO id;


/* ions cleanup */

ALTER TABLE ion_class_list  ALTER COLUMN ion_class_name TYPE varchar(200) USING ion_class_name::varchar;
ALTER TABLE ion_class_list RENAME COLUMN ion_class_id TO id;
ALTER TABLE ion_class_list RENAME COLUMN ion_class_name TO name;

ALTER TABLE ion_subclass_list  ALTER COLUMN ion_subclass_name TYPE varchar(200) USING ion_subclass_name::varchar;
ALTER TABLE ion_subclass_list RENAME COLUMN ion_subclass_id TO id;
ALTER TABLE ion_subclass_list RENAME COLUMN ion_subclass_name TO name;

ALTER TABLE ion_group_list  ALTER COLUMN ion_group_name TYPE varchar(200) USING ion_group_name::varchar;
ALTER TABLE ion_group_list RENAME COLUMN ion_group_id TO id;
ALTER TABLE ion_group_list RENAME COLUMN ion_group_name TO name;

ALTER TABLE ion_subgroup_list  ALTER COLUMN ion_subgroup_name TYPE varchar(200) USING ion_subgroup_name::varchar;
ALTER TABLE ion_subgroup_list RENAME COLUMN ion_subgroup_id TO id;
ALTER TABLE ion_subgroup_list RENAME COLUMN ion_subgroup_name TO name;
ALTER TABLE ion_subgroup_list ADD CONSTRAINT ion_subgroup_list_un UNIQUE ("name");

ALTER TABLE ion_type_list  ALTER COLUMN ion_type_name TYPE varchar(200) USING ion_type_name::varchar;
ALTER TABLE ion_type_list RENAME COLUMN ion_type_id TO id;
ALTER TABLE ion_type_list RENAME COLUMN ion_type_name TO name;

alter table ion_list rename to ion_log;
ALTER TABLE ion_log  ALTER COLUMN ion_name TYPE varchar(200) USING ion_name::varchar;
ALTER TABLE ion_log RENAME COLUMN ion_id TO id;
ALTER TABLE ion_log RENAME COLUMN ion_name TO name;

ALTER TABLE ion_position_list RENAME COLUMN ion_position_id TO id;
ALTER TABLE ion_position_list RENAME COLUMN ion_position_name TO name;


/* mineral_log cleanup */

ALTER TABLE mineral_log RENAME COLUMN mineral_id TO id;
ALTER TABLE mineral_log RENAME COLUMN mineral_name TO name;
ALTER TABLE mineral_log RENAME COLUMN id_class TO ns_class;
ALTER TABLE mineral_log RENAME COLUMN id_subclass TO ns_subclass;
ALTER TABLE mineral_log RENAME COLUMN id_family TO ns_family;
ALTER TABLE mineral_log RENAME COLUMN id_mineral TO ns_mineral;

-- convert mineral_log.ns_subclass to int
ALTER TABLE mineral_log DROP CONSTRAINT fk_ns_subclass;
WITH temp_ AS (
    SELECT ml.id AS id_, ns.id AS ns_subclass_id FROM mineral_log ml
	INNER JOIN ns_subclass ns ON ml.ns_subclass = ns.ns_subclass
)
UPDATE mineral_log
SET ns_subclass = temp_.ns_subclass_id
FROM temp_
WHERE id = temp_.id_;
ALTER TABLE mineral_log ALTER COLUMN ns_subclass SET DEFAULT NULL::integer;
ALTER TABLE mineral_log ALTER COLUMN ns_subclass TYPE integer USING (ns_subclass::integer);
ALTER TABLE mineral_log ADD CONSTRAINT mineral_log_ns_subclass_fk FOREIGN KEY (ns_subclass) REFERENCES ns_subclass(id) ON UPDATE CASCADE ON DELETE CASCADE;

-- convert mineral_log.ns_family to int
ALTER TABLE mineral_log DROP CONSTRAINT fk_ns_family;
WITH temp_ AS (
    SELECT ml.id AS id_, ns.id AS ns_family_id FROM mineral_log ml
	INNER JOIN ns_family ns ON ml.ns_family = ns.ns_family
)
UPDATE mineral_log
SET ns_family = temp_.ns_family_id
FROM temp_
WHERE id = temp_.id_;
ALTER TABLE mineral_log ALTER COLUMN ns_family SET DEFAULT NULL::integer;
ALTER TABLE mineral_log ALTER COLUMN ns_family TYPE integer USING (ns_family::integer);
ALTER TABLE mineral_log ADD CONSTRAINT mineral_log_ns_family_fk FOREIGN KEY (ns_family) REFERENCES ns_family(id) ON UPDATE CASCADE ON DELETE CASCADE;

-- convert ns_family.ns_subclass to int and change FK
ALTER TABLE ns_family DROP CONSTRAINT fk_ns_subclass;
WITH temp_ AS (
    SELECT nf.id AS id_, ns.id AS ns_subclass_id FROM ns_family nf
    INNER JOIN ns_subclass ns ON ns.ns_subclass = nf.ns_subclass
)
UPDATE ns_family
SET ns_subclass = temp_.ns_subclass_id
FROM temp_
WHERE id = temp_.id_;
ALTER TABLE ns_family ALTER COLUMN ns_subclass SET DEFAULT NULL::integer;
ALTER TABLE ns_family ALTER COLUMN ns_subclass TYPE integer USING (ns_subclass::integer);
ALTER TABLE ns_family ADD CONSTRAINT ns_family_ns_subclass_fk FOREIGN KEY (ns_subclass) REFERENCES ns_subclass(id) ON UPDATE CASCADE ON DELETE CASCADE;


DROP TABLE IF EXISTS mineral_ion_real;
DROP TABLE IF EXISTS mineral_name_institution;
DROP TABLE IF EXISTS mineral_name_ion;
DROP TABLE IF EXISTS mineral_name_language;
DROP TABLE IF EXISTS mineral_name_locality_country;
DROP TABLE IF EXISTS mineral_name_locality;
DROP TABLE IF EXISTS mineral_name_other;
DROP TABLE IF EXISTS mineral_name_person;

ALTER TABLE mineral_country DROP COLUMN created_at;
ALTER TABLE mineral_country DROP COLUMN updated_at;


/* crystallography cleanup */

ALTER TABLE crystal_system_list RENAME COLUMN crystal_system_id TO id;
ALTER TABLE crystal_system_list RENAME COLUMN crystal_system_name TO name;

ALTER TABLE crystal_class_list  ALTER COLUMN crystal_class_name TYPE varchar(200) USING crystal_class_name::varchar;
ALTER TABLE crystal_class_list RENAME COLUMN crystal_class_id TO id;
ALTER TABLE crystal_class_list RENAME COLUMN crystal_class_name TO name;

ALTER TABLE space_group_list ALTER COLUMN space_group_name TYPE varchar(200) USING space_group_name::varchar;
ALTER TABLE space_group_list RENAME COLUMN space_group_id TO id;
ALTER TABLE space_group_list RENAME COLUMN space_group_name TO name;

ALTER TABLE mineral_crystallography DROP COLUMN ns_space_group_id;
DROP TABLE IF EXISTS ns_space_group_list;

ALTER TABLE mineral_crystallography RENAME TO mineral_crystallography_old;
CREATE TABLE mineral_crystallography (
	id serial PRIMARY KEY,
	mineral_id uuid NOT NULL REFERENCES mineral_log(id) ON UPDATE CASCADE,
	crystal_system_id int NOT NULL REFERENCES crystal_system_list(id) ON UPDATE CASCADE,
	crystal_class_id int DEFAULT NULL REFERENCES crystal_class_list(id) ON UPDATE CASCADE,
	space_group_id int DEFAULT NULL REFERENCES space_group_list(id) ON UPDATE CASCADE,
	a decimal default null,
	b decimal default null,
	c decimal default null,
	alpha decimal default null,
	beta decimal default null,
	gamma decimal default null,
	z int default null
);
INSERT INTO mineral_crystallography (mineral_id, crystal_system_id, crystal_class_id, space_group_id, a, b, c, alpha, beta, gamma, z)
SELECT mco.mineral_id, mco.crystal_system_id, mco.crystal_class_id, mco.space_group_id, mco.a, mco.b, mco.c, mco.alpha,
	   mco.beta, mco.gamma, mco.z FROM mineral_crystallography_old mco;

DROP TABLE IF EXISTS mineral_crystallography_old;


/* group ions cleanup */

ALTER TABLE gr_ions RENAME to mineral_ion_position;
ALTER TABLE mineral_ion_position ADD CONSTRAINT mineral_ion_position_ion_log_id_fkey
FOREIGN KEY (ion_id) REFERENCES ion_log(id) ON UPDATE cascade on delete cascade;

/* physical properties tables */

CREATE TABLE color_list(
	id serial PRIMARY KEY,
	name varchar(100) NOT NULL,
	code varchar(100) DEFAULT NULL
);

CREATE TABLE mineral_color (
	id serial PRIMARY KEY,
	mineral_id uuid NOT NULL REFERENCES mineral_log(id) ON UPDATE CASCADE,
	color_id int NOT NULL REFERENCES color_list(id) ON UPDATE CASCADE
);
