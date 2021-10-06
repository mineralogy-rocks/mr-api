  ALTER TABLE mineral_relation
    ADD column mineral_status_id int DEFAULT NULL REFERENCES mineral_status(id) ON UPDATE CASCADE;