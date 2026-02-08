-- 1. Borrar la versión antigua
DROP FUNCTION IF EXISTS score_inventory_batch(integer[], jsonb);

-- 2. Crear la nueva versión con columnas extra
CREATE OR REPLACE FUNCTION score_inventory_batch(inventory_ids INT[], user_parts JSONB)
RETURNS TABLE (
    set_num VARCHAR, 
    name VARCHAR, 
    year INT, 
    num_parts INT, 
    total_parts INT, 
    unique_parts INT, 
    img_url VARCHAR, 
    match_percent NUMERIC
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
            count(*)::INT as total_lines, -- Piezas Diferentes
            sum(ip.quantity)::INT as total_qty, -- Piezas Totales
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
        ss.total_qty as total_parts, 
        ss.total_lines as unique_parts, 
        s.img_url::VARCHAR,
        round((ss.total_score / ss.total_lines) * 100, 1) as match_percent
    FROM set_scores ss
    JOIN inventories i ON i.id = ss.inventory_id
    JOIN sets s ON s.set_num = i.set_num;
END;
$$;