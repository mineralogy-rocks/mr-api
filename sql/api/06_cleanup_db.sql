DROP TABLE IF EXISTS nuxt_tabs;


ALTER TABLE ns_class RENAME COLUMN id_class TO id;
ALTER TABLE ns_subclass RENAME COLUMN id_class TO ns_class;
ALTER TABLE ns_subclass RENAME COLUMN id_subclass TO ns_subclass;
ALTER TABLE ns_family RENAME COLUMN id_class TO ns_class;
ALTER TABLE ns_family RENAME COLUMN id_subclass TO ns_subclass;
ALTER TABLE ns_family RENAME COLUMN id_family TO ns_family;
                      
   
ALTER TABLE status_list RENAME TO status_list_old;
CREATE TABLE status_list (
	id SERIAL PRIMARY KEY,
	status_id numeric(4,2) NOT NULL,
	description_group varchar(100) DEFAULT NULL,
	description_short varchar(100) NOT NULL,
	description_long TEXT DEFAULT NULL
);
INSERT INTO status_list (status_id, description_group, description_short, description_long) 
SELECT status_id, description_group, description_short, description_long FROM status_list_old;

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
