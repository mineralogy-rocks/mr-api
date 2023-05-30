CREATE INDEX mineral_hierarchy_view_mineral_idx ON mineral_hierarchy_view (mineral_id);
CREATE INDEX mineral_hierarchy_view_relation_idx ON mineral_hierarchy_view (relation_id);
CREATE INDEX mineral_log_ns_family_idx ON mineral_log (ns_family);
CREATE INDEX mineral_status_needs_revision_idx ON mineral_status (needs_revision);
CREATE INDEX mineral_formula_mineral_idx ON mineral_formula(mineral_id);
CREATE INDEX mineral_crystallography_mineral_idx ON mineral_crystallography(mineral_id);

CREATE INDEX mineral_crystallography_crystal_system_idx ON mineral_crystallography(crystal_system_id);
CREATE INDEX mineral_status_mineral_idx ON mineral_status(mineral_id);
CREATE INDEX mineral_status_status_idx ON mineral_status(status_id);
CREATE INDEX mineral_relation_mineral_idx ON mineral_relation(mineral_id);
CREATE INDEX mineral_relation_relation_idx ON mineral_relation(relation_id);
CREATE INDEX mineral_relation_mineral_status_idx ON mineral_relation(mineral_status_id);
