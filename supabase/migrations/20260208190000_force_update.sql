-- Refactoring Matching Logic for Streaming and Theme Filtering

DROP FUNCTION IF EXISTS get_candidate_inventories(jsonb, text[]);
DROP FUNCTION IF EXISTS get_filtered_set_count(text[]);
DROP FUNCTION IF EXISTS score_inventory_batch(int[], jsonb);
DROP FUNCTION IF EXISTS get_set_missing_parts(varchar, jsonb);

-- 1. Helper: Get Candidates (Optionally Filtered by Theme)
CREATE OR REPLACE FUNCTION get_candidate_inventories(user_parts JSONB, filter_themes TEXT[] DEFAULT NULL)
RETURNS TABLE (inventory_id INT, set_num VARCHAR)
language plpgsql
STABLE
AS $$
DECLARE
    major_themes TEXT[] := ARRAY['Star Wars', 'Technic', 'City', 'Architecture', 'Ninjago'];
    is_filtered BOOLEAN;
BEGIN
    -- Determine if we have a restrictive filter
    is_filtered := (filter_themes IS NOT NULL AND cardinality(filter_themes) > 0);

    RETURN QUERY
    WITH user_part_list AS (
        SELECT 
            (x->>'part_num')::VARCHAR as part_num,
            (x->>'color_id')::INT as color_id
        FROM jsonb_array_elements(user_parts) x
    ),
    -- 1. Identify Target Sets (Theme Filter)
    target_sets AS (
        SELECT s.set_num, i.id as inventory_id
        FROM sets s
        JOIN inventories i ON i.set_num = s.set_num
        JOIN themes t ON t.id = s.theme_id
        WHERE 
            NOT is_filtered -- If not filtered, take all (Logic will handle this later)
            OR t.name = ANY(filter_themes)
            OR ('Otros' = ANY(filter_themes) AND NOT (t.name = ANY(major_themes)))
    ),
    -- 2. Identify Sets with Matching Parts
    part_matching_sets AS (
        SELECT DISTINCT ip.inventory_id
        FROM inventory_parts ip
        JOIN user_part_list upl 
            ON ip.part_num = upl.part_num
            AND ip.color_id = upl.color_id
    )
    -- 3. Final Selection
    SELECT ts.inventory_id, ts.set_num
    FROM target_sets ts
    LEFT JOIN part_matching_sets pms ON ts.inventory_id = pms.inventory_id
    WHERE 
        -- IF Filtered (Theme Selected): Take ALL sets in theme (Exhaustive)
        is_filtered 
        -- IF Not Filtered (Todos): Take ONLY sets with matching parts (Opportunistic)
        OR pms.inventory_id IS NOT NULL;
END;
$$;

-- 3. Helper: Get Count of Filtered Sets (For UI)
CREATE OR REPLACE FUNCTION get_filtered_set_count(filter_themes TEXT[] DEFAULT NULL)
RETURNS INT
language plpgsql
STABLE
AS $$
DECLARE
    major_themes TEXT[] := ARRAY['Star Wars', 'Technic', 'City', 'Architecture', 'Ninjago'];
    is_filtered BOOLEAN;
BEGIN
    is_filtered := (filter_themes IS NOT NULL AND cardinality(filter_themes) > 0);
    
    RETURN (
        SELECT COUNT(*)::INT
        FROM sets s
        JOIN themes t ON t.id = s.theme_id
        WHERE 
            NOT is_filtered
            OR t.name = ANY(filter_themes)
            OR ('Otros' = ANY(filter_themes) AND NOT (t.name = ANY(major_themes)))
    );
END;
$$;


-- 2. Helper: Score a Batch of Inventories
CREATE OR REPLACE FUNCTION score_inventory_batch(inventory_ids INT[], user_parts JSONB)
RETURNS TABLE (
    set_num VARCHAR,
    name VARCHAR,
    year INT,
    num_parts INT,
    img_url VARCHAR,
    match_percent NUMERIC,
    missing_pieces INT
)
language plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH user_collection AS (
        SELECT 
            (x->>'part_num')::VARCHAR as part_num,
            (x->>'color_id')::INT as color_id,
            (x->>'quantity')::INT as quantity
        FROM jsonb_array_elements(user_parts) x
    ),
    set_scores AS (
        SELECT 
            ip.inventory_id,
            -- Total pieces needed (Sum of quantity), excluding spares
            sum(ip.quantity)::NUMERIC as total_pieces,
            -- Missing pieces: Sum(Required - Have) where Have < Required
            sum(
                GREATEST(0, ip.quantity - COALESCE(uc.quantity, 0))
            )::NUMERIC as missing_pieces
        FROM inventory_parts ip
        LEFT JOIN user_collection uc 
            ON ip.part_num = uc.part_num 
            AND ip.color_id = uc.color_id
        WHERE ip.inventory_id = ANY(inventory_ids)
          AND ip.is_spare = false -- Exclude spares from calculation
        GROUP BY ip.inventory_id
    )
    SELECT 
        s.set_num,
        s.name,
        s.year,
        ss.total_pieces::INT as num_parts, -- Corrected: Return only calculated non-spare pieces from inventory
        s.img_url::VARCHAR,
        -- Similarity Calculation based on Missing Pieces
        -- Formula: ((Total - Missing) / Total) * 100
        round(
            CASE 
                WHEN ss.total_pieces > 0 THEN 
                    ((ss.total_pieces - ss.missing_pieces) / ss.total_pieces) * 100
                ELSE 0 
            END, 
        1) as match_percent,
        ss.missing_pieces::INT -- New column for UI validation
    FROM set_scores ss
    -- Nexus: inventories.id used as link to inventory_parts via set_scores result
    JOIN inventories i ON i.id = ss.inventory_id
    JOIN sets s ON s.set_num = i.set_num;
END;
$$;

-- 4. Helper: Get Missing Parts for Download
CREATE OR REPLACE FUNCTION get_set_missing_parts(p_set_num VARCHAR, user_parts JSONB)
RETURNS TABLE (
    part_num VARCHAR,
    color_id INT,
    missing_qty INT,
    part_name VARCHAR,
    color_name VARCHAR
)
language plpgsql
STABLE
AS $$
DECLARE
    target_inventory_id INT;
BEGIN
    -- Get Inventory ID via strict link
    SELECT id INTO target_inventory_id
    FROM inventories
    WHERE set_num = p_set_num
    LIMIT 1;

    RETURN QUERY
    WITH user_collection AS (
        SELECT 
            (x->>'part_num')::VARCHAR as part_num,
            (x->>'color_id')::INT as color_id,
            (x->>'quantity')::INT as quantity
        FROM jsonb_array_elements(user_parts) x
    )
    SELECT 
        ip.part_num,
        ip.color_id,
        (ip.quantity - COALESCE(uc.quantity, 0))::INT as missing_qty,
        p.name::VARCHAR as part_name,
        c.name::VARCHAR as color_name
    FROM inventory_parts ip
    -- Nexus: inventories.id -> inventory_parts.inventory_id
    LEFT JOIN user_collection uc 
        ON ip.part_num = uc.part_num 
        AND ip.color_id = uc.color_id
    JOIN parts p ON p.part_num = ip.part_num
    JOIN colors c ON c.id = ip.color_id
    WHERE ip.inventory_id = target_inventory_id
      AND ip.is_spare = false
      AND (ip.quantity - COALESCE(uc.quantity, 0)) > 0;
END;
$$;
