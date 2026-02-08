const fs = require('fs');
const path = require('path');
const readline = require('readline');

const DATA_DIR = path.join(__dirname, '../lego_inventory_data');
const OUTPUT_FILE = path.join(__dirname, '../supabase/seed.sql');

// Map CSV filenames to Table names and Allowed Columns
const FILES_TO_TABLES = [
    { file: 'themes.csv', table: 'themes', columns: ['id', 'name', 'parent_id'] },
    { file: 'colors.csv', table: 'colors', columns: ['id', 'name', 'rgb', 'is_trans'] },
    { file: 'part_categories.csv', table: 'part_categories', columns: ['id', 'name'] },
    { file: 'parts.csv', table: 'parts', columns: ['part_num', 'name', 'part_cat_id', 'part_material'] },
    { file: 'elements.csv', table: 'elements', columns: ['element_id', 'part_num', 'color_id'] },
    { file: 'part_relationships.csv', table: 'part_relationships', columns: ['rel_type', 'child_part_num', 'parent_part_num'] },
    { file: 'minifigs.csv', table: 'minifigs', columns: ['fig_num', 'name', 'num_parts'] }, // Exclude img_url for now as schema might not have it yet except by migration... wait, I added migration. Let's try to include it IF CSV has it. But CSV header for minifigs has img_url.
    // Wait, I added img_url to sets, minifigs, inventory_parts in migration 20260208000000_add_img_url.sql.
    // So I CAN include it here.
    { file: 'sets.csv', table: 'sets', columns: ['set_num', 'name', 'year', 'theme_id', 'num_parts', 'img_url'] },
    { file: 'inventories.csv', table: 'inventories', columns: ['id', 'version', 'set_num'] },
    { file: 'inventory_parts.csv', table: 'inventory_parts', columns: ['inventory_id', 'part_num', 'color_id', 'quantity', 'is_spare', 'img_url'] },
    { file: 'inventory_minifigs.csv', table: 'inventory_minifigs', columns: ['inventory_id', 'fig_num', 'quantity'] },
    { file: 'inventory_sets.csv', table: 'inventory_sets', columns: ['inventory_id', 'set_num', 'quantity'] }
];

// RE-Check minifigs header: fig_num,name,num_parts,img_url
// RE-Check migration: ALTER TABLE minifigs ADD COLUMN IF NOT EXISTS img_url text; -- Yes I added it.

async function processFile(fileInfo, writeStream) {
    const filePath = path.join(DATA_DIR, fileInfo.file);
    if (!fs.existsSync(filePath)) {
        console.warn(`Skipping missing file: ${fileInfo.file}`);
        return;
    }

    console.log(`Processing ${fileInfo.file}...`);

    const fileStream = fs.createReadStream(filePath);
    const rl = readline.createInterface({
        input: fileStream,
        crlfDelay: Infinity
    });

    let headerMap = null; // Maps CSV index to Column Name
    let batch = [];
    const BATCH_SIZE = 1000;

    for await (let line of rl) {
        if (!line.trim()) continue;

        // Match CSV fields: quoted "..." or unquoted
        const matches = line.match(/(".*?"|[^",\s]+)(?=\s*,|\s*$)/g);
        // Use parsed line
        const row = parseCSVLine(line);

        if (!headerMap) {
            // Create map: index -> column_name
            headerMap = row.map(h => h.trim());
            continue;
        }

        if (row.length !== headerMap.length) {
            continue;
        }

        const validValues = [];
        let skipRow = false;

        // Iterate over required target columns
        for (const targetCol of fileInfo.columns) {
            // Find index of this column in the CSV
            const idx = headerMap.indexOf(targetCol);

            if (idx === -1) {
                // If a required column is missing in CSV, insert NULL
                validValues.push('NULL');
            } else {
                let val = row[idx].trim();

                // Value formatting
                if (val === 't') val = 'true';
                else if (val === 'f') val = 'false';

                if (val === '') {
                    validValues.push('NULL');
                } else {
                    const escaped = val.replace(/'/g, "''");
                    validValues.push(`'${escaped}'`);
                }
            }
        }

        batch.push(`(${validValues.join(',')})`);

        if (batch.length >= BATCH_SIZE) {
            writeStream.write(`INSERT INTO ${fileInfo.table} (${fileInfo.columns.join(',')}) VALUES \n${batch.join(',\n')};\n`);
            batch = [];
        }
    }

    if (batch.length > 0) {
        writeStream.write(`INSERT INTO ${fileInfo.table} (${fileInfo.columns.join(',')}) VALUES \n${batch.join(',\n')};\n`);
    }
}

function parseCSVLine(text) {
    const result = [];
    let cur = '';
    let inQuote = false;
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        if (char === '"') {
            inQuote = !inQuote;
        } else if (char === ',' && !inQuote) {
            result.push(cur);
            cur = '';
        } else {
            cur += char;
        }
    }
    result.push(cur);
    return result;
}

async function main() {
    const writeStream = fs.createWriteStream(OUTPUT_FILE);

    writeStream.write('-- Seed data generated from Rebrickable CSVs\n');
    writeStream.write('SET session_replication_role = replica;\n\n'); // Disable triggers/FKs

    for (const item of FILES_TO_TABLES) {
        await processFile(item, writeStream);
    }

    writeStream.write('\nSET session_replication_role = origin;\n'); // Re-enable triggers/FKs
    writeStream.end();

    console.log('Seed file generated successfully!');
}

main();
