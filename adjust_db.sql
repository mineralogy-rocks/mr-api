drop table if exists nuxt_tabs;
create table nuxt_tabs (
	tab_id serial primary key,
	tab_short_name varchar(50) not null,
	tab_long_name text not null,
	unique(tab_short_name)
);

insert into nuxt_tabs(tab_short_name, tab_long_name)
values ('history', 'History'), ('classification', 'Classification taxonomy'), ('relations', 'People also search for');

drop table if exists mineral_relation cascade;

create table mineral_relation (
	id serial primary key,
	mineral_id uuid references mineral_list(mineral_id) on update cascade not null,
	relation_id uuid references mineral_list(mineral_id) on update cascade not null,
	direct_relation boolean not null,
	relation_type_id int references relation_list(relation_type_id) on update cascade not null,
	relation_note text default null,
	unique(mineral_id, relation_id, relation_type_id, direct_relation)
);