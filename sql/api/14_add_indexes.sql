CREATE INDEX mineral_hierarchy_view_mineral_idx ON mineral_hierarchy_view (mineral_id);
CREATE INDEX mineral_hierarchy_view_relation_idx ON mineral_hierarchy_view (relation_id);
CREATE INDEX mineral_log_ns_family_idx ON mineral_log (ns_family);
CREATE INDEX mineral_status_needs_revision_idx ON mineral_status (needs_revision);
