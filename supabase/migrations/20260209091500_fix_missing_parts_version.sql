-- Fix get_set_missing_parts to use version 1 explicitly

DROP FUNCTION IF EXISTS get_set_missing_parts(varchar, jsonb);

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
    -- Get Inventory ID for VERSION 1 (main version)
    SELECT id INTO target_inventory_id
    FROM inventories
    WHERE set_num = p_set_num
      AND version = 1  -- ✅ Only use version 1
    LIMIT 1;

    IF target_inventory_id IS NULL THEN
        RAISE EXCEPTION 'Set % version 1 not found', p_set_num;
    END IF;

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
