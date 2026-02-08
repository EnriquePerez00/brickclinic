-- Module 2: Star Wars DNA Profiles
-- Stores statistical fingerprints of official Star Wars construction patterns
-- Using unique table names to avoid conflicts

CREATE TABLE IF NOT EXISTS sw_dna_profiles (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER NOT NULL,
    set_num VARCHAR,
    model_category VARCHAR, -- 'small_ship', 'medium_ship', 'ucs', 'base', 'vehicle'
    num_parts INTEGER,
    
    -- Structural DNA
    snot_ratio FLOAT, -- % of parts using SNOT techniques
    vertical_ratio FLOAT, -- % traditional vertical stacking
    complexity_score FLOAT, -- Avg connections per part
    
    -- Color DNA (JSON array of [color_id, weight])
    primary_colors JSONB,
    secondary_colors JSONB,
    
    -- Connectivity DNA (JSON object)
    connectivity_patterns JSONB,
    
    -- Metadata
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file VARCHAR,
    
    UNIQUE(theme_id, set_num)
);

-- Aggregated DNA by category
CREATE TABLE IF NOT EXISTS sw_dna_aggregated (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER NOT NULL,
    model_category VARCHAR NOT NULL,
    
    -- Aggregated statistics
    avg_snot_ratio FLOAT,
    avg_vertical_ratio FLOAT,
    avg_complexity FLOAT,
    
    -- Most common colors
    color_palette JSONB,
    
    -- Most common part combinations
    top_connectivity_patterns JSONB,
    
    num_sets_analyzed INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(theme_id, model_category)
);

-- Index for fast theme queries
CREATE INDEX IF NOT EXISTS idx_swd_theme ON sw_dna_profiles(theme_id);
CREATE INDEX IF NOT EXISTS idx_swd_category ON sw_dna_profiles(model_category);
CREATE INDEX IF NOT EXISTS idx_swd_parts ON sw_dna_profiles(num_parts);

COMMENT ON TABLE sw_dna_profiles IS 'Statistical fingerprints extracted from official LEGO sets';
COMMENT ON COLUMN sw_dna_profiles.snot_ratio IS 'Percentage of parts using Studs Not On Top techniques';
COMMENT ON COLUMN sw_dna_profiles.connectivity_patterns IS 'Part co-occurrence matrix with PMI scores';
