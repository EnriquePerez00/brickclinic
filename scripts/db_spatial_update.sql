-- Enable JSONB checks if needed
-- Table for storing calculated spatial data from LDraw
CREATE TABLE IF NOT EXISTS part_spatial_data (
    part_num varchar(50) PRIMARY KEY REFERENCES parts(part_num) ON DELETE CASCADE,
    
    -- Bounding Box (LDraw Units)
    size_x float NOT NULL DEFAULT 0,
    size_y float NOT NULL DEFAULT 0,
    size_z float NOT NULL DEFAULT 0,
    
    -- Calculated Volume (AABB)
    volume float GENERATED ALWAYS AS (size_x * size_y * size_z) STORED,
    
    -- Detected Connectivity (e.g., {"studs": 8, "tubes": 3})
    connectivity_json jsonb DEFAULT '{}'::jsonb,
    
    -- Metadata
    last_updated timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE part_spatial_data ENABLE ROW LEVEL SECURITY;

-- Policy
CREATE POLICY "Public read access" ON part_spatial_data FOR SELECT USING (true);
