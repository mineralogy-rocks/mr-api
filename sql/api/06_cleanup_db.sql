DROP TABLE IF EXISTS nuxt_tabs;

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
INSERT INTO status_group_list (name) VALUES ('grouping'), ('synonyms'), ('varieties'), ('polytypes'), ('obsolete nomenclature'), 
											('anthropotype'), ('mineraloids'), ('rocks'), ('unnamed'), ('mixtures'), ('IMA minerals');
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

ALTER TABLE mineral_log RENAME COLUMN mineral_id TO id;
ALTER TABLE mineral_log RENAME COLUMN mineral_name TO name;
ALTER TABLE mineral_log RENAME COLUMN id_class TO ns_class;
ALTER TABLE mineral_log RENAME COLUMN id_subclass TO ns_subclass;
ALTER TABLE mineral_log RENAME COLUMN id_family TO ns_family;
ALTER TABLE mineral_log RENAME COLUMN id_mineral TO ns_mineral;

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

ALTER TABLE crystal_system_list RENAME COLUMN crystal_system_id TO id;
ALTER TABLE crystal_system_list RENAME COLUMN crystal_system_name TO name;

ALTER TABLE crystal_class_list  ALTER COLUMN crystal_class_name TYPE varchar(200) USING crystal_class_name::varchar;
ALTER TABLE crystal_class_list RENAME COLUMN crystal_class_id TO id;
ALTER TABLE crystal_class_list RENAME COLUMN crystal_class_name TO name;
