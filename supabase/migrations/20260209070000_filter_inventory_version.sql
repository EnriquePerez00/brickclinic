-- Filter duplicate inventory versions: Only show version 1 (main version)

DROP FUNCTION IF EXISTS get_candidate_inventories(JSONB, TEXT[]);

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
    -- 1. Identify Target Sets (Theme Filter) - ONLY VERSION 1
    target_sets AS (
        SELECT s.set_num, i.id as inventory_id
        FROM sets s
        JOIN inventories i ON i.set_num = s.set_num
        JOIN themes t ON t.id = s.theme_id
        WHERE 
            i.version = 1  -- ✅ ONLY main version
            AND (
                NOT is_filtered -- If not filtered, take all (Logic will handle this later)
                OR t.name = ANY(filter_themes)
                OR ('Otros' = ANY(filter_themes) AND NOT (t.name = ANY(major_themes)))
            )
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
