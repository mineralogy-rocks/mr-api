ALTER TABLE mineral_status RENAME TO mineral_status_old;

CREATE TABLE mineral_status (
	id serial PRIMARY KEY,
	mineral_id uuid NOT NULL,
	status_id int NOT NULL,
	needs_revision bool NOT NULL DEFAULT FALSE,
	note TEXT DEFAULT NULL,
	author_id int DEFAULT NULL,
  direct_status bool DEFAULT TRUE,
	created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT mineral_status_mineral_id_status_id_unique UNIQUE (mineral_id, status_id, direct_status),
	CONSTRAINT mineral_status_mineral_id_fkey1 FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT mineral_status_status_id_fkey FOREIGN KEY (status_id) REFERENCES status_list(id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT mineral_status_revised_by_fkey FOREIGN KEY (author_id) REFERENCES auth_user(id) ON DELETE SET NULL ON UPDATE CASCADE
);

INSERT INTO mineral_status (mineral_id, status_id, created_at, updated_at)
SELECT mso.mineral_id, mso.status_id, mso.created_at, mso.updated_at FROM mineral_status_old mso;


CREATE TRIGGER update_date BEFORE
UPDATE ON mineral_status FOR EACH ROW EXECUTE FUNCTION update_timestamp();

DROP TABLE IF EXISTS mineral_relation;
DROP TABLE IF EXISTS mineral_status_old;

CREATE TABLE mineral_relation(
    id serial primary key,
    mineral_id uuid not null references mineral_log(id) on update cascade on delete cascade,
    mineral_status_id int default null references mineral_status(id) on update CASCADE ON DELETE CASCADE,
    relation_id uuid default null references mineral_log(id) on update cascade,
    note text default null,
    unique(mineral_id, mineral_status_id, relation_id)
);

CREATE TABLE mineral_relation_suggestion(
    id serial primary key,
    mineral_id uuid not null references mineral_log(id) on update cascade on delete cascade,
    relation_id uuid default null references mineral_log(id) on update cascade,
    relation_type_id int DEFAULT NULL,
    is_processed bool DEFAULT FALSE
);
