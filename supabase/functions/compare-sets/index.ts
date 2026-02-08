
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
    // Handle CORS
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders });
    }

    try {
        const formData = await req.formData();
        const file = formData.get('file');
        // Handle 'themes' parameter
        const themesParam = formData.get('themes');
        let filterThemes: string[] | null = null;
        if (themesParam) {
            filterThemes = themesParam.toString().split(',').map(t => t.trim()).filter(t => t.length > 0 && t !== 'Todos');
            if (filterThemes.length === 0) filterThemes = null;
        }

        if (!file) {
            return new Response(JSON.stringify({ error: 'No file uploaded' }), { status: 400, headers: corsHeaders });
        }

        // Parse CSV
        const text = await file.text();
        const lines = text.split('\n');
        const delimiter = lines[0].includes(';') ? ';' : ',';

        const headers = lines[0].toLowerCase().split(delimiter).map(h => h.trim().replace(/"/g, ''));
        const partNumIdx = headers.findIndex(h => h.includes('part') && !h.includes('name') && !h.includes('cat'));
        const colorIdIdx = headers.findIndex(h => h.includes('color'));
        const quantityIdx = headers.findIndex(h => h.includes('qty') || h.includes('quantity'));

        if (partNumIdx === -1) throw new Error('Column "part_num" not found');

        const userParts = [];
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            const parts = line.split(delimiter);
            if (parts.length > partNumIdx) {
                userParts.push({
                    part_num: parts[partNumIdx].trim(),
                    color_id: colorIdIdx !== -1 ? (parseInt(parts[colorIdIdx]) || -1) : -1,
                    quantity: quantityIdx !== -1 ? (parseInt(parts[quantityIdx]) || 1) : 1
                });
            }
        }

        // Initialize Supabase
        const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
        const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
        const supabase = createClient(supabaseUrl, supabaseKey);

        const userPartsPayload = userParts.map(p => ({
            part_num: p.part_num,
            color_id: p.color_id,
            quantity: p.quantity
        }));

        // 1. Get Candidates
        // 1. Get Candidates
        console.log(`[Info] Getting candidates for ${userParts.length} parts. Themes: ${filterThemes ? filterThemes.join(', ') : 'All'}`);
        const { data: candidates, error: candError } = await supabase.rpc('get_candidate_inventories', {
            user_parts: userPartsPayload,
            filter_themes: filterThemes
        });

        if (candError) throw candError;

        const inventoryIds = candidates.map((c: any) => c.inventory_id);
        console.log(`[Info] Found ${inventoryIds.length} candidates.`);

        // 2. Stream Results
        const body = new ReadableStream({
            async start(controller) {
                const encoder = new TextEncoder();
                const BATCH_SIZE = 50; // Increased for performance

                try {
                    // Send initial metadata
                    const meta = JSON.stringify({ type: 'metadata', total: inventoryIds.length, user_parts: userParts.length }) + '\n';
                    controller.enqueue(encoder.encode(meta));

                    for (let i = 0; i < inventoryIds.length; i += BATCH_SIZE) {
                        const batch = inventoryIds.slice(i, i + BATCH_SIZE);

                        const { data: scoredBatch, error: scoreError } = await supabase.rpc('score_inventory_batch', {
                            inventory_ids: batch,
                            user_parts: userPartsPayload
                        });

                        if (scoreError) {
                            console.error('Batch error:', scoreError);
                            continue;
                        }

                        if (scoredBatch && scoredBatch.length > 0) {
                            // Send batch as a JSON line
                            // Structure: { type: 'batch', data: [...] }
                            const chunk = JSON.stringify({ type: 'batch', data: scoredBatch }) + '\n';
                            controller.enqueue(encoder.encode(chunk));
                        }
                    }
                } catch (e) {
                    console.error('Stream error:', e);
                    const err = JSON.stringify({ type: 'error', message: e.message }) + '\n';
                    controller.enqueue(encoder.encode(err));
                } finally {
                    controller.close();
                }
            }
        });

        return new Response(body, {
            headers: {
                ...corsHeaders,
                'Content-Type': 'application/x-ndjson', // Newline Delimited JSON
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        });

    } catch (error: any) {
        return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: corsHeaders });
    }
});
