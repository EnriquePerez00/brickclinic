-- Task 1: Indexing Strategy
-- Optimized index for high-speed lookups on part+color
CREATE INDEX IF NOT EXISTS idx_inventory_parts_part_color 
ON inventory_parts (part_num, color_id);

-- Check if type exists to avoid errors during iteration
DROP TYPE IF EXISTS match_set_result CASCADE;
CREATE TYPE match_set_result AS (
    set_num VARCHAR,
    name VARCHAR,
    year INT,
    num_parts INT,
    img_url VARCHAR,
    match_percent NUMERIC
);

-- Task 2 & 3: The "Benevolent" Matching Function
-- Implemented as a set-returning function for efficiency
CREATE OR REPLACE FUNCTION match_lego_sets(user_parts JSONB)
RETURNS SETOF match_set_result
language plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    WITH user_collection AS (
        -- Parse user input JSON into a temporary dataset
        SELECT 
            (x->>'part_num')::VARCHAR as part_num,
            (x->>'color_id')::INT as color_id,
            (x->>'quantity')::INT as quantity
        FROM jsonb_array_elements(user_parts) x
    ),
    candidate_inventories AS (
        -- Optimization: First find inventories that have AT LEAST ONE matching part
        -- This avoids scanning the entire database of disjoint sets
        SELECT DISTINCT ip.inventory_id
        FROM inventory_parts ip
        JOIN user_collection uc 
            ON ip.part_num = uc.part_num 
            AND ip.color_id = uc.color_id
    ),
    set_scores AS (
        -- Calculate score for each candidate inventory
        SELECT 
            ip.inventory_id,
            -- Metric: Total lines in the set's inventory
            count(*)::NUMERIC as total_lines,
            -- Metric: Sum of Weighted Scores
            -- Logic: 
            --   If match: Base 0.8 + Bonus (capped at 0.2)
            --   If no match: 0
            sum(
                CASE 
                    WHEN uc.part_num IS NOT NULL THEN 
                        0.8 + LEAST(0.2, 0.2 * (COALESCE(uc.quantity, 0)::numeric / ip.quantity::numeric))
                    ELSE 0
                END
            ) as total_score
        FROM inventory_parts ip
        JOIN candidate_inventories ci ON ci.inventory_id = ip.inventory_id
        -- LEFT JOIN to preserve "misses" (parts in set but not in user collection)
        LEFT JOIN user_collection uc 
            ON ip.part_num = uc.part_num 
            AND ip.color_id = uc.color_id
        GROUP BY ip.inventory_id
    )
    SELECT 
        s.set_num,
        s.name,
        s.year,
        s.num_parts,
        s.img_url::VARCHAR,
        -- Final Percentage: (Total Score / Total Lines) * 100
        round((ss.total_score / ss.total_lines) * 100, 1) as match_percent
    FROM set_scores ss
    JOIN inventories i ON i.id = ss.inventory_id
    JOIN sets s ON s.set_num = i.set_num
    -- Constraint: Filter out very low matches if needed, or just order
    ORDER BY match_percent DESC
    LIMIT 5;
END;
$$;
