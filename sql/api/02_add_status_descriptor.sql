CREATE TABLE status_descriptor_list (
    status_concat_type_id serial primary key,
    status_id references status_list (status_id) on update cascade not null,
    start_or_end boolean not null,
    concat_string varchar(50) not null,
	unique(status_id)
);