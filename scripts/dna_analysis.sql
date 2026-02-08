-- Function to extract "DNA" from a Theme
-- Returns a JSONB object with distributions

CREATE OR REPLACE FUNCTION get_theme_dna(target_theme_id INT)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'theme_id', target_theme_id,
        'part_categories', (
            SELECT jsonb_object_agg(name, usage_percent)
            FROM (
                SELECT 
                    pc.name,
                    ROUND((SUM(ip.quantity)::numeric / total.qty) * 100, 2) as usage_percent
                FROM sets s
                JOIN inventories i ON s.set_num = i.set_num
                JOIN inventory_parts ip ON i.id = ip.inventory_id
                JOIN parts p ON ip.part_num = p.part_num
                JOIN part_categories pc ON p.part_cat_id = pc.id
                CROSS JOIN (
                    SELECT SUM(ip2.quantity) as qty
                    FROM sets s2
                    JOIN inventories i2 ON s2.set_num = i2.set_num
                    JOIN inventory_parts ip2 ON i2.id = ip2.inventory_id
                    WHERE s2.theme_id = target_theme_id
                ) total
                WHERE s.theme_id = target_theme_id
                GROUP BY pc.name, total.qty
                ORDER BY usage_percent DESC
                LIMIT 10
            ) cats
        ),
        'color_palette', (
            SELECT jsonb_object_agg(name, usage_percent)
            FROM (
                SELECT 
                    c.name,
                    ROUND((SUM(ip.quantity)::numeric / total.qty) * 100, 2) as usage_percent
                FROM sets s
                JOIN inventories i ON s.set_num = i.set_num
                JOIN inventory_parts ip ON i.id = ip.inventory_id
                JOIN colors c ON ip.color_id = c.id
                CROSS JOIN (
                    SELECT SUM(ip2.quantity) as qty
                    FROM sets s2
                    JOIN inventories i2 ON s2.set_num = i2.set_num
                    JOIN inventory_parts ip2 ON i2.id = ip2.inventory_id
                    WHERE s2.theme_id = target_theme_id
                ) total
                WHERE s.theme_id = target_theme_id
                GROUP BY c.name, total.qty
                ORDER BY usage_percent DESC
                LIMIT 10
            ) cols
        ),
        'geometric_profile', (
            SELECT jsonb_build_object(
                'avg_volume', ROUND(AVG(psd.volume)::numeric, 2),
                'total_volume', ROUND(SUM(psd.volume * ip.quantity)::numeric, 2)
            )
            FROM sets s
            JOIN inventories i ON s.set_num = i.set_num
            JOIN inventory_parts ip ON i.id = ip.inventory_id
            JOIN part_spatial_data psd ON ip.part_num = psd.part_num
            WHERE s.theme_id = target_theme_id
        )
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;
