-- Refactoring Matching Logic for Streaming and Theme Filtering

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
RETURNS SETOF match_set_result
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
            count(*)::NUMERIC as total_lines,
            sum(
                CASE 
                    WHEN uc.part_num IS NOT NULL THEN 
                        0.8 + LEAST(0.2, 0.2 * (COALESCE(uc.quantity, 0)::numeric / ip.quantity::numeric))
                    ELSE 0
                END
            ) as total_score
        FROM inventory_parts ip
        LEFT JOIN user_collection uc 
            ON ip.part_num = uc.part_num 
            AND ip.color_id = uc.color_id
        WHERE ip.inventory_id = ANY(inventory_ids)
        GROUP BY ip.inventory_id
    )
    SELECT 
        s.set_num,
        s.name,
        s.year,
        s.num_parts,
        s.img_url::VARCHAR,
        round((ss.total_score / ss.total_lines) * 100, 1) as match_percent
    FROM set_scores ss
    -- Nexus: inventories.id used as link to inventory_parts via set_scores result
    JOIN inventories i ON i.id = ss.inventory_id
    JOIN sets s ON s.set_num = i.set_num;
END;
$$;
