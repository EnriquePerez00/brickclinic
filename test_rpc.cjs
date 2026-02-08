
// Script to simulate a file upload to the Edge Function
const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Mock CSV Content: 5 parts from Set 75301-1 (Luke's X-Wing)
// Real set has ~470 parts. We send 5.
// We expect a match but low percentage, OR if strict coverage, maybe 100% of THESE parts are in the set.
// Part 3001 (Brick 2x4) - Color 0 (Black) - Qty 2
// Part 3003 (Brick 2x2) - Color 15 (White) - Qty 5
const csvContent = `part_num,color_id,quantity
3001,0,2
3003,15,5
3023,71,10
3024,72,5
3710,0,1`;

async function testFunction() {
    console.log("Simulating CSV Upload to compare-sets...");

    const boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW';
    let body = `--${boundary}\r\n`;
    body += 'Content-Disposition: form-data; name="file"; filename="test_inventory.csv"\r\n';
    body += 'Content-Type: text/csv\r\n\r\n';
    body += csvContent + '\r\n';
    body += `--${boundary}--\r\n`;

    try {
        const response = await fetch('http://127.0.0.1:54321/functions/v1/compare-sets', {
            method: 'POST',
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
            },
            body: body
        });

        const text = await response.text();
        console.log("Status:", response.status);
        console.log("Response:", text);

    } catch (err) {
        console.error("Fetch error:", err);
    }
}

testFunction();
