
// Script to simulate streaming request
const { createClient } = require('@supabase/supabase-js');

// Mock content
const csvContent = `part_num,color_id,quantity
3001,0,2
3003,15,5
3023,71,10
3024,72,5
3710,0,1`;

async function testStreaming() {
    console.log("Simulating Streaming Request...");

    // Boundary for multipart
    const boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW';
    let body = `--${boundary}\r\n`;
    body += 'Content-Disposition: form-data; name="file"; filename="test_stream.csv"\r\n';
    body += 'Content-Type: text/csv\r\n\r\n';
    body += csvContent + '\r\n';
    body += `--${boundary}\r\n`;
    body += 'Content-Disposition: form-data; name="themes"\r\n\r\n';
    body += 'Star Wars, Technic\r\n'; // Multi-theme test
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

        console.log("Status:", response.status);

        if (!response.body) {
            console.log("No body!");
            return;
        }

        // Read stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            console.log("Received chunk:", chunk);

            // In real client we'd parse this
        }

    } catch (err) {
        console.error("Error:", err);
    }
}

testStreaming();
