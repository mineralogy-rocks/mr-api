CREATE TABLE ima_status_list(
  id serial PRIMARY KEY,
  key varchar(100) NOT NULL,
  name varchar(255) DEFAULT NULL
);

INSERT INTO ima_status_list (key, name) VALUES ('APPROVED', 'Approved'),
                                               ('DISCREDITED', 'Discredited'),
                                               ('PENDING_PUBLICATION', 'Pending Publication'),
                                               ('GRANDFATHERED', 'Grandfathered'),
                                               ('QUESTIONABLE', 'Questionable');

CREATE TABLE ima_note_list(
  id serial PRIMARY KEY,
  key varchar(100) NOT NULL,
  name varchar(255) DEFAULT NULL
);

INSERT INTO ima_note_list (key, name) VALUES ('REJECTED', 'Rejected'),
											                       ('PENDING_APPROVAL', 'Pending Approval'),
                                             ('GROUP', 'Group'), ('REDEFINED', 'Redefined'),
                                             ('RENAMED', 'Renamed'),
                                             ('INTERMEDIATE', 'Intermediate'),
                                             ('PUBLISHED_WITHOUT_APPROVAL', 'Published without Approval'),
                                             ('UNNAMED_VALID', 'Unnamed Valid'),
                                             ('UNNAMED_INVALID', 'Unnamed Invalid'),
                                             ('NAMED_AMPHIBOLE', 'Named Amphibole');

CREATE TABLE mineral_ima_status(
	id serial PRIMARY KEY,
  mineral_id uuid NOT NULL,
  ima_status_id int NOT NULL,
	created_at timestamp DEFAULT current_timestamp,
  FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE,
  FOREIGN KEY (ima_status_id) REFERENCES ima_status_list(id) ON DELETE CASCADE
);

CREATE TABLE mineral_ima_note(
  id serial PRIMARY KEY,
  mineral_id uuid NOT NULL,
  ima_note_id int NOT NULL,
  created_at timestamp DEFAULT current_timestamp,
  FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE,
  FOREIGN KEY (ima_note_id) REFERENCES ima_note_list(id) ON DELETE CASCADE
);

CREATE TABLE data_context_list(
  id serial PRIMARY KEY,
  name varchar(100) DEFAULT NULL
);

INSERT INTO data_context_list(name) VALUES ('Physical properties'), ('Optical properties');

CREATE TABLE mineral_context(
  id serial PRIMARY KEY,
  mineral_id uuid NOT NULL,
  context_id int NOT NULL,
  data JSONB DEFAULT NULL,
  created_at timestamp DEFAULT current_timestamp,
  FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE,
  FOREIGN KEY (context_id) REFERENCES data_context_list(id) ON DELETE CASCADE
);

CREATE INDEX mineral_context_mineral_idx ON mineral_context(mineral_id);
