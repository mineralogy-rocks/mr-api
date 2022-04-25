DROP TABLE IF EXISTS nuxt_tabs;

ALTER TABLE ns_class RENAME COLUMN id_class TO id;
ALTER TABLE ns_subclass RENAME COLUMN id_class TO ns_class,
                        RENAME COLUMN id_subclass TO ns_subclass;
ALTER TABLE ns_family RENAME COLUMN id_class TO ns_class,
                      RENAME COLUMN id_subclass TO ns_subclass,
                      RENAME COLUMN id_family TO ns_family;

