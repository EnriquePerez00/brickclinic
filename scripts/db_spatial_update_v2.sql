-- GNN v2: Sequential Construction & Connectivity Tables

-- 1. Construction Steps (Sequential Build Data)
CREATE TABLE IF NOT EXISTS construction_steps (
    id SERIAL PRIMARY KEY,
    set_num VARCHAR NOT NULL,
    step_number INT NOT NULL,
    graph_snapshot JSONB NOT NULL, -- {nodes: [{part_num, color, quantity}], edges: [[i,j]]}
    spatial_data JSONB,             -- {part_id: {pos: [x,y,z], rot: [r00..r22]}}
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(set_num, step_number)
);

CREATE INDEX idx_construction_steps_set ON construction_steps(set_num);
CREATE INDEX idx_construction_steps_step ON construction_steps(set_num, step_number);

-- 2. Connectivity Rules (Physical Connection Constraints)
CREATE TABLE IF NOT EXISTS connectivity_rules (
    id SERIAL PRIMARY KEY,
    part_a VARCHAR NOT NULL,
    part_b VARCHAR NOT NULL,
    connection_type VARCHAR NOT NULL, -- 'stud', 'technic_pin', 'clip', 'hinge'
    contact_points JSONB,              -- [{rel_pos: [x,y,z], tolerance: float}]
    frequency INT DEFAULT 1,
    theme_id INT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(part_a, part_b, connection_type, theme_id)
);

CREATE INDEX idx_connectivity_parts ON connectivity_rules(part_a, part_b);
CREATE INDEX idx_connectivity_theme ON connectivity_rules(theme_id);

-- 3. Neighborhood Frequency (Co-occurrence Statistics)
CREATE TABLE IF NOT EXISTS neighborhood_frequency (
    id SERIAL PRIMARY KEY,
    part_num VARCHAR NOT NULL,
    neighbor_part VARCHAR NOT NULL,
    co_occurrence_count INT DEFAULT 1,
    avg_distance FLOAT,
    std_distance FLOAT,
    theme_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(part_num, neighbor_part, theme_id)
);

CREATE INDEX idx_neighborhood_part ON neighborhood_frequency(part_num, theme_id);
CREATE INDEX idx_neighborhood_freq ON neighborhood_frequency(theme_id, co_occurrence_count DESC);

-- 4. Theme DNA Profiles (Cached Analysis)
CREATE TABLE IF NOT EXISTS theme_dna_profiles (
    theme_id INT PRIMARY KEY,
    theme_name VARCHAR,
    profile_data JSONB NOT NULL, -- Full JSON profile from gnn_enhancement_plan.md
    last_updated TIMESTAMP DEFAULT NOW()
);

COMMENT ON TABLE construction_steps IS 'Sequential construction data from LDraw OMR files';
COMMENT ON TABLE connectivity_rules IS 'Physical connection constraints extracted from official builds';
COMMENT ON TABLE neighborhood_frequency IS 'Part co-occurrence statistics by theme';
COMMENT ON TABLE theme_dna_profiles IS 'Cached theme characteristic profiles';
