ALTER TABLE relation_list RENAME TO relation_type_list;

DROP TABLE IF EXISTS mineral_relation;


 CREATE TABLE mineral_relation(
    id serial primary key,
    mineral_id uuid not null references mineral_log(mineral_id) on update cascade,
    mineral_status_id int default null references mineral_status(id) on update cascade,
    relation_id uuid default null references mineral_log(mineral_id) on update cascade,
    relation_type_id int not null references relation_type_list(relation_type_id) on update cascade, 
    relation_note text default null,
    direct_relation bool default true,
    unique(mineral_id, mineral_status_id, relation_id, relation_type_id, relation_note, direct_relation)
);