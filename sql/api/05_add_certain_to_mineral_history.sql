DROP TABLE mineral_history;

CREATE TABLE mineral_history(
    id SERIAL PRIMARY KEY,
    mineral_id uuid NOT NULL REFERENCES mineral_log(mineral_id) ON UPDATE CASCADE ON DELETE CASCADE,
    discovery_year_min INT DEFAULT NULL,
    discovery_year_max INT DEFAULT NULL,
    discovery_year_note TEXT DEFAULT NULL,
    certain BOOLEAN DEFAULT TRUE,
    first_usage_date TEXT DEFAULT NULL,
    first_known_use TEXT DEFAULT NULL
);
