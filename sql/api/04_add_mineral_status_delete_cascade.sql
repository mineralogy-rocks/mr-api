BEGIN;
	ALTER TABLE mineral_status DROP CONSTRAINT ms_species_status_mineral_id_fkey;
	ALTER TABLE mineral_status ADD CONSTRAINT mineral_status_mineral_id_fkey FOREIGN KEY (mineral_id) REFERENCES mineral_log(mineral_id) ON UPDATE cascade on delete cascade;
COMMIT;
