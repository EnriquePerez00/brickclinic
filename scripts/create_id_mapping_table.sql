-- Module 1: ID Cross-Reference System
-- Maps Rebrickable part IDs to LDraw filenames

CREATE TABLE IF NOT EXISTS part_id_mapping (
    rebrickable_id VARCHAR PRIMARY KEY,
    ldraw_filename VARCHAR NOT NULL,
    part_name VARCHAR,
    category VARCHAR,
    verified BOOLEAN DEFAULT FALSE,
    mapping_method VARCHAR, -- 'exact', 'fuzzy', 'manual'
    confidence_score FLOAT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Index for fast LDraw lookups (reverse mapping)
CREATE INDEX idx_ldraw_filename ON part_id_mapping(ldraw_filename);

-- Index for category-based queries
CREATE INDEX idx_category ON part_id_mapping(category);

-- View for high-confidence mappings only
CREATE VIEW verified_mappings AS
SELECT * FROM part_id_mapping 
WHERE verified = TRUE AND confidence_score > 0.9;

-- Audit table for tracking mapping changes
CREATE TABLE IF NOT EXISTS part_mapping_audit (
    id SERIAL PRIMARY KEY,
    rebrickable_id VARCHAR,
    old_ldraw_filename VARCHAR,
    new_ldraw_filename VARCHAR,
    changed_by VARCHAR,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);

COMMENT ON TABLE part_id_mapping IS 'Cross-reference between Rebrickable and LDraw part numbering systems';
COMMENT ON COLUMN part_id_mapping.mapping_method IS 'Method used: exact (direct match), fuzzy (similarity), manual (human verified)';
COMMENT ON COLUMN part_id_mapping.confidence_score IS 'Confidence from 0.0 to 1.0, where 1.0 is certain';
