import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
    // CORS headers
    if (req.method === 'OPTIONS') {
        return new Response('ok', {
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
            }
        });
    }

    try {
        const { set_num } = await req.json();

        if (!set_num) {
            return new Response(
                JSON.stringify({ error: 'set_num is required' }),
                { status: 400, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
            );
        }

        // Initialize Supabase client
        const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
        const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
        const supabase = createClient(supabaseUrl, supabaseKey);

        // Query database for set and its inventory
        // First, find the set
        const { data: sets, error: setError } = await supabase
            .from('sets')
            .select('*')
            .eq('set_num', set_num);

        if (setError || !sets || sets.length === 0) {
            return new Response(
                JSON.stringify({ error: `Set ${set_num} not found in database` }),
                { status: 404, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
            );
        }

        const setData = sets[0];

        // Find the inventory for this set (get latest version)
        const { data: inventories, error: invLookupError } = await supabase
            .from('inventories')
            .select('id, version')
            .eq('set_num', set_num)
            .order('version', { ascending: false })
            .limit(1);

        if (invLookupError || !inventories || inventories.length === 0) {
            return new Response(
                JSON.stringify({ error: `No inventory found for set ${set_num}` }),
                { status: 404, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
            );
        }

        const inventoryId = inventories[0].id;

        // Query inventory_parts for this inventory
        // Joining with parts and colors tables to get full details
        const { data: inventoryParts, error: invError } = await supabase
            .from('inventory_parts')
            .select(`
                part_num,
                color_id,
                quantity,
                is_spare,
                parts:part_num (part_num, name, part_cat_id),
                colors:color_id (id, name, rgb)
            `)
            .eq('inventory_id', inventoryId);

        if (invError) {
            console.error('Inventory error:', invError);
            return new Response(
                JSON.stringify({ error: 'Error fetching inventory', details: invError.message }),
                { status: 500, headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' } }
            );
        }

        // Generate CSV
        const csvLines = ['part_num,color_id,quantity,is_spare,part_name,color_name,color_rgb'];

        for (const item of inventoryParts || []) {
            const partName = item.parts?.name || 'Unknown';
            const colorName = item.colors?.name || 'Unknown';
            const colorRgb = item.colors?.rgb || '';

            const line = [
                item.part_num,
                item.color_id,
                item.quantity,
                item.is_spare ? '1' : '0',
                `"${partName.replace(/"/g, '""')}"`,
                `"${colorName.replace(/"/g, '""')}"`,
                colorRgb
            ].join(',');
            csvLines.push(line);
        }

        const csv = csvLines.join('\n');

        // Note: Edge Functions can't write to filesystem directly
        // Instead, we return the CSV content for the frontend to download

        return new Response(
            JSON.stringify({
                success: true,
                csv,
                num_parts: inventoryParts?.length || 0,
                set_info: {
                    set_num: setData.set_num,
                    name: setData.name,
                    year: setData.year,
                    theme_id: setData.theme_id
                }
            }),
            {
                status: 200,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        );

    } catch (error: any) {
        console.error('Error:', error);
        return new Response(
            JSON.stringify({ error: error.message || 'Unknown error' }),
            {
                status: 500,
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }
            }
        );
    }
});
