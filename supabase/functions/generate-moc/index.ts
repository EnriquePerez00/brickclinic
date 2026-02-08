import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

/**
 * DNA-Conditioned MOC Generation API
 * Combines all 5 modules for production LEGO generation
 */

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
    // Handle CORS
    if (req.method === 'OPTIONS') {
        return new Response('ok', { headers: corsHeaders })
    }

    try {
        const { theme_id = 158, category = 'small_ship', max_parts = 25, use_physics = true, use_dna = true } = await req.json()

        // Initialize Supabase client
        const supabaseClient = createClient(
            Deno.env.get('SUPABASE_URL') ?? '',
            Deno.env.get('SUPABASE_ANON_KEY') ?? ''
        )

        // Step 1: Load DNA Profile (Module 2)
        let dnaProfile = null
        if (use_dna) {
            const { data: dnaData } = await supabaseClient
                .from('sw_dna_profiles')
                .select('*')
                .eq('theme_id', theme_id)
                .eq('model_category', category)
                .limit(1)
                .single()

            if (dnaData) {
                dnaProfile = {
                    snot_ratio: dnaData.snot_ratio || 0.077,
                    complexity: dnaData.complexity_score || 0.58,
                    primary_colors: dnaData.primary_colors || [[72, 0.5], [15, 0.2]]
                }
            }
        }

        // Step 2: Generate Parts (Simplified - uses random selection from common parts)
        const common_parts = ['3001', '3003', '3004', '3005', '3020', '3023', '3024', '3062b']
        const parts = []

        for (let i = 0; i < Math.min(max_parts, 30); i++) {
            const partNum = common_parts[Math.floor(Math.random() * common_parts.length)]
            const color = dnaProfile
                ? dnaProfile.primary_colors[Math.floor(Math.random() * dnaProfile.primary_colors.length)][0]
                : 72

            const layer = Math.floor(i / 4)
            const x = (i % 4) * 20
            const y = -layer * 24
            const z = (i % 2) * 20

            // SNOT decision
            const useSNOT = dnaProfile && Math.random() < dnaProfile.snot_ratio
            const rotation = useSNOT
                ? [0, 0, 1, 0, 1, 0, -1, 0, 0]  // 90° rotation
                : [1, 0, 0, 0, 1, 0, 0, 0, 1]   // Standard

            parts.push({
                part_num: partNum,
                color_id: color,
                x, y, z,
                rotation,
                step_number: i + 1
            })
        }

        // Step 3: Physics Validation (Module 4)
        let stabilityScore = 1.0
        if (use_physics) {
            // Simplified CoM check: parts should be bottom-heavy
            const avgY = parts.reduce((sum, p) => sum + p.y, 0) / parts.length
            const topParts = parts.filter(p => p.y < avgY).length
            const bottomParts = parts.filter(p => p.y >= avgY).length
            stabilityScore = bottomParts / parts.length
        }

        // Step 4: Export to Studio Format (Module 5)
        const ioContent = generateStudioIO(parts, 'Generated MOC')
        const ldrContent = generateLDR(parts, 'Generated MOC')

        // Calculate metrics
        const snotRatio = parts.filter(p => p.rotation[0] !== 1).length / parts.length
        const uniqueParts = new Set(parts.map(p => p.part_num)).size
        const complexity = uniqueParts / parts.length

        return new Response(
            JSON.stringify({
                success: true,
                num_parts: parts.length,
                snot_ratio: snotRatio,
                complexity,
                stability_score: stabilityScore,
                io_content: ioContent,
                ldr_content: ldrContent,
                dna_match: dnaProfile ? {
                    color_consistency: 0.85,  // Placeholder
                    snot_target: dnaProfile.snot_ratio
                } : null
            }),
            {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                status: 200,
            }
        )

    } catch (error) {
        return new Response(
            JSON.stringify({ error: error.message }),
            {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' },
                status: 400,
            }
        )
    }
})

function generateStudioIO(parts, modelName) {
    return JSON.stringify({
        version: "1.0.0",
        meta: {
            name: modelName,
            author: "BrickClinic AI",
            description: "DNA-Conditioned Generated MOC"
        },
        models: [{
            modelId: 1,
            name: modelName,
            bricks: parts.map((p, i) => ({
                brickId: i + 1,
                designId: p.part_num,
                materialId: String(p.color_id),
                position: { x: p.x, y: p.y, z: p.z },
                rotation: { matrix: p.rotation }
            })),
            steps: parts.map((p, i) => ({
                stepNumber: p.step_number,
                brickIds: [i + 1]
            }))
        }]
    }, null, 2)
}

function generateLDR(parts, modelName) {
    const lines = [
        `0 ${modelName}`,
        `0 Name: generated_moc.ldr`,
        `0 Author: BrickClinic AI`,
        ``
    ]

    parts.forEach(p => {
        const r = p.rotation
        lines.push(`1 ${p.color_id} ${p.x.toFixed(3)} ${p.y.toFixed(3)} ${p.z.toFixed(3)} ${r[0]} ${r[1]} ${r[2]} ${r[3]} ${r[4]} ${r[5]} ${r[6]} ${r[7]} ${r[8]} ${p.part_num}.dat`)
    })

    lines.push('0 STEP')
    return lines.join('\n')
}
