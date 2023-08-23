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
  updated_at timestamp DEFAULT current_timestamp,
  FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE,
  FOREIGN KEY (context_id) REFERENCES data_context_list(id) ON DELETE CASCADE
);


-- CREATE TABLE tenacity_list(
--   id serial PRIMARY KEY,
--   name varchar(255) DEFAULT NULL
-- );

-- INSERT INTO tenacity_list (name) VALUES ('brittle'),
--                                         ('very brittle'),
--                                         ('sectile'),
--                                         ('waxy'),
--                                         ('flexible'),
--                                         ('elastic'),
--                                         ('fragile'),
--                                         ('malleable');

-- CREATE TABLE mineral_physical_properties(
--   id serial PRIMARY KEY,
--   mineral_id uuid NOT NULL,

--   color varchar(255) DEFAULT NULL,
--   density_measured_min float DEFAULT NULL,
--   density_measured_max float DEFAULT NULL,
--   hardness_min float DEFAULT NULL,
--   hardness_max float DEFAULT NULL,
--   tenacity_id int DEFAULT NULL,


--   created_at timestamp DEFAULT current_timestamp,
--   updated_at timestamp DEFAULT current_timestamp,
--   FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE,
--   FOREIGN KEY (tenacity_id) REFERENCES tenacity_list(id) ON DELETE CASCADE
-- );

-- CREATE TABLE transparency_list(
--   id serial PRIMARY KEY,
--   name varchar(255) DEFAULT NULL
-- );

-- INSERT INTO transparency_list (name) VALUES ('Transparent'), ('Translucent'), ('Opaque');

-- CREATE TABLE mineral_diapheny(
--   id serial PRIMARY KEY,
--   mineral_id uuid NOT NULL,
--   transparency_id int NOT NULL,
--   FOREIGN KEY (mineral_id) REFERENCES mineral_log(id) ON DELETE CASCADE,
--   FOREIGN KEY (transparency_id) REFERENCES transparency_list(id) ON DELETE CASCADE
-- );

"colour",
  "diapheny",
  "dmeas",
  "dmeas2",
  "hmin",
  "hmax",
  "tenacity",
  "cleavage",
  "luminescence",
  "lustre",
  "streak",

  "opticaltype",
  "opticalsign",
  "opticalextinction",
  "opticalalpha",
  "opticalalpha2",
  "opticalalphaerror",
  "opticalbeta",
  "opticalbeta2",
  "opticalbetaerror",
  "opticalgamma",
  "opticalgamma2",
  "opticalgammaerror",
  "opticalomega",
  "opticalomega2",
  "opticalomegaerror",
  "opticalepsilon",
  "opticalepsilon2",
  "opticalepsilonerror",
  "opticaln",
  "opticaln2",
  "opticalnerror",
  "optical2vcalc",
  "optical2vcalc2",
  "optical2vcalcerror",
  "optical2vmeasured",
  "optical2vmeasured2",
  "optical2vmeasurederror",
  "opticaldispersion",
  "opticalpleochroism",
  "opticalpleochorismdesc",
  "opticalbirefringence",
  "opticalcomments",
  "opticalcolour",
  "opticalinternal",
  "opticaltropic",
  "opticalanisotropism",
  "opticalbireflectance",
  "opticalr",
