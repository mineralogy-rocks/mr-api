ALTER TABLE public.mineral_crystallography DROP CONSTRAINT mineral_crystallography_mineral_id_fkey;
ALTER TABLE public.mineral_crystallography ADD CONSTRAINT mineral_crystallography_mineral_id_fkey FOREIGN KEY (mineral_id) REFERENCES public.mineral_log(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE public.mineral_relation_suggestion DROP CONSTRAINT mineral_relation_suggestion_relation_id_fkey;
ALTER TABLE public.mineral_relation_suggestion ADD CONSTRAINT mineral_relation_suggestion_relation_id_fkey FOREIGN KEY (relation_id) REFERENCES public.mineral_log(id) ON DELETE CASCADE ON UPDATE CASCADE;

DELETE FROM mineral_log ml
WHERE ml.name ILIKE '% ';
