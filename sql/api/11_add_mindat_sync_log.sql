CREATE TABLE mindat_sync_log(
	id serial PRIMARY KEY,
	mineral_id uuid REFERENCES mineral_log(id) ON UPDATE CASCADE ON DELETE SET NULL,
	VALUES jsonb DEFAULT NULL,
	created_at timestamp DEFAULT current_timestamp
);
