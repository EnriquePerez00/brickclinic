import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'http://127.0.0.1:54321';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0';

const supabase = createClient(supabaseUrl, supabaseKey);

async function check() {
    console.log('Checking database content...');

    const { count: setsCount, error: setsError } = await supabase
        .from('sets')
        .select('*', { count: 'exact', head: true });

    if (setsError) {
        console.error('Error checking sets:', setsError.message);
    } else {
        console.log(`Sets Table Rows: ${setsCount}`);
    }

    const { count: partsCount, error: partsError } = await supabase
        .from('inventory_parts')
        .select('*', { count: 'exact', head: true });

    if (partsError) {
        // If table doesn't exist, this might error
        console.error('Error checking inventory_parts:', partsError.message);
    } else {
        console.log(`Inventory Parts Table Rows: ${partsCount}`);
    }
}

check();
