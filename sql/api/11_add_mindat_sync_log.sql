CREATE TABLE mindat_sync_log(
	id serial PRIMARY KEY,
	VALUES jsonb DEFAULT NULL,
	created_at timestamp DEFAULT current_timestamp
);
