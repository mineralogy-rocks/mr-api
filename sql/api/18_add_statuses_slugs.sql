ALTER TABLE status_group_list ADD COLUMN slug varchar(100) UNIQUE DEFAULT NULL;
ALTER TABLE status_list ADD COLUMN slug varchar(200) UNIQUE DEFAULT NULL;

UPDATE status_group_list AS sgl SET
slug = new.slug
FROM (VALUES (1, 'grouping'), (2, 'synonyms'), (3, 'varieties'),
			 (4, 'polytypes'), (5, 'obsolete-nomenclature'), (6, 'anthropotype'),
			 (7, 'mineraloids'), (8, 'rocks'), (9, 'unnamed'), (10, 'mixtures'),
			 (11, 'ima-approved-minerals')) AS new (id, slug)
WHERE sgl.id = new.id;

UPDATE status_list AS sl SET slug = new.slug
FROM (VALUES (16, 'serie'), (17, 'root-mineral-name'), (18, 'subgroup'),
			 (19, 'group'), (20, 'supergroup'), (1, 'ima-approved-mineral')) AS new (id, slug)
WHERE sl.id = new.id;
