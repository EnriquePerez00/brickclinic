-- Enable UUID extension if needed, though int/varchar PKs are used here
-- Drop tables if they exist to start fresh (CASCADE to handle FKs)
DROP TABLE IF EXISTS inventory_sets CASCADE;
DROP TABLE IF EXISTS inventory_minifigs CASCADE;
DROP TABLE IF EXISTS inventory_parts CASCADE;
DROP TABLE IF EXISTS inventories CASCADE;
DROP TABLE IF EXISTS sets CASCADE;
DROP TABLE IF EXISTS minifigs CASCADE;
DROP TABLE IF EXISTS part_relationships CASCADE;
DROP TABLE IF EXISTS elements CASCADE;
DROP TABLE IF EXISTS parts CASCADE;
DROP TABLE IF EXISTS part_categories CASCADE;
DROP TABLE IF EXISTS colors CASCADE;
DROP TABLE IF EXISTS themes CASCADE;

-- 1. Themes (Corrected: id is integer, parent_id refs themes(id))
CREATE TABLE themes (
    id integer PRIMARY KEY,
    name varchar(255) NOT NULL,
    parent_id integer REFERENCES themes(id)
);

-- 2. Colors
CREATE TABLE colors (
    id integer PRIMARY KEY,
    name varchar(255) NOT NULL,
    rgb varchar(6) NOT NULL,
    is_trans boolean NOT NULL
);

-- 3. Part Categories
CREATE TABLE part_categories (
    id integer PRIMARY KEY,
    name varchar(255) NOT NULL
);

-- 4. Parts
CREATE TABLE parts (
    part_num varchar(50) PRIMARY KEY,
    name text NOT NULL,
    part_cat_id integer REFERENCES part_categories(id),
    part_material varchar(255) -- captured from CSV if exists
);

-- 5. Elements
CREATE TABLE elements (
    element_id varchar(50) PRIMARY KEY,
    part_num varchar(50) REFERENCES parts(part_num),
    color_id integer REFERENCES colors(id)
);

-- 6. Part Relationships
CREATE TABLE part_relationships (
    rel_type varchar(10) NOT NULL,
    child_part_num varchar(50) REFERENCES parts(part_num),
    parent_part_num varchar(50) REFERENCES parts(part_num),
    PRIMARY KEY (rel_type, child_part_num, parent_part_num)
);

-- 7. Minifigs
CREATE TABLE minifigs (
    fig_num varchar(50) PRIMARY KEY,
    name varchar(255) NOT NULL,
    num_parts integer NOT NULL
);

-- 8. Sets
CREATE TABLE sets (
    set_num varchar(50) PRIMARY KEY,
    name varchar(255) NOT NULL,
    year integer NOT NULL,
    theme_id integer REFERENCES themes(id),
    num_parts integer NOT NULL
);

-- 9. Inventories
CREATE TABLE inventories (
    id integer PRIMARY KEY,
    version integer NOT NULL,
    set_num varchar(50) REFERENCES sets(set_num)
);

-- 10. Inventory Parts
CREATE TABLE inventory_parts (
    inventory_id integer REFERENCES inventories(id),
    part_num varchar(50) REFERENCES parts(part_num),
    color_id integer REFERENCES colors(id),
    quantity integer NOT NULL,
    is_spare boolean NOT NULL,
    PRIMARY KEY (inventory_id, part_num, color_id, is_spare)
);

-- 11. Inventory Minifigs
CREATE TABLE inventory_minifigs (
    inventory_id integer REFERENCES inventories(id),
    fig_num varchar(50) REFERENCES minifigs(fig_num),
    quantity integer NOT NULL,
    PRIMARY KEY (inventory_id, fig_num)
);

-- 12. Inventory Sets
CREATE TABLE inventory_sets (
    inventory_id integer REFERENCES inventories(id),
    set_num varchar(50) REFERENCES sets(set_num),
    quantity integer NOT NULL,
    PRIMARY KEY (inventory_id, set_num)
);

-- Enable Row Level Security (RLS) on all tables as best practice
ALTER TABLE themes ENABLE ROW LEVEL SECURITY;
ALTER TABLE colors ENABLE ROW LEVEL SECURITY;
ALTER TABLE part_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE parts ENABLE ROW LEVEL SECURITY;
ALTER TABLE elements ENABLE ROW LEVEL SECURITY;
ALTER TABLE part_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE minifigs ENABLE ROW LEVEL SECURITY;
ALTER TABLE sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventories ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_parts ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_minifigs ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_sets ENABLE ROW LEVEL SECURITY;

-- Create basic read-only policies for public access (adjust as needed)
CREATE POLICY "Public read access" ON themes FOR SELECT USING (true);
CREATE POLICY "Public read access" ON colors FOR SELECT USING (true);
CREATE POLICY "Public read access" ON part_categories FOR SELECT USING (true);
CREATE POLICY "Public read access" ON parts FOR SELECT USING (true);
CREATE POLICY "Public read access" ON elements FOR SELECT USING (true);
CREATE POLICY "Public read access" ON part_relationships FOR SELECT USING (true);
CREATE POLICY "Public read access" ON minifigs FOR SELECT USING (true);
CREATE POLICY "Public read access" ON sets FOR SELECT USING (true);
CREATE POLICY "Public read access" ON inventories FOR SELECT USING (true);
CREATE POLICY "Public read access" ON inventory_parts FOR SELECT USING (true);
CREATE POLICY "Public read access" ON inventory_minifigs FOR SELECT USING (true);
CREATE POLICY "Public read access" ON inventory_sets FOR SELECT USING (true);
ALTER TABLE sets ADD COLUMN IF NOT EXISTS img_url text;
ALTER TABLE minifigs ADD COLUMN IF NOT EXISTS img_url text;
ALTER TABLE inventory_parts ADD COLUMN IF NOT EXISTS img_url text;
