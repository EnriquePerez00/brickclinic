#!/usr/bin/env node
// sync-translations.js -- Brickclinic
// Syncs ES source to CA, EN-US, DE via DeepL API

// Disable SSL verification for corporate network environments
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

function loadEnv() {
  for (const file of ['.env.local', '.env']) {
    const envPath = path.join(rootDir, file);
    if (fs.existsSync(envPath)) {
      const raw = fs.readFileSync(envPath, 'utf-8');
      const lines = raw.split(String.fromCharCode(10));
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;
        const eqIdx = trimmed.indexOf('=');
        if (eqIdx === -1) continue;
        const key = trimmed.slice(0, eqIdx).trim();
        const val = trimmed.slice(eqIdx + 1).trim();
        if (!process.env[key]) process.env[key] = val;
      }
      console.log('Loaded env from', file);
      break;
    }
  }
}

loadEnv();

const DEEPL_API_KEY = process.env.DEEPL_API_KEY;
if (!DEEPL_API_KEY) {
  console.error('DEEPL_API_KEY not found in .env or .env.local');
  process.exit(1);
}

const DEEPL_URL = DEEPL_API_KEY.endsWith(':fx')
  ? 'https://api-free.deepl.com/v2/translate'
  : 'https://api.deepl.com/v2/translate';

const TARGETS = [
  { lang: 'ca', target: 'CA' },
  { lang: 'en', target: 'EN-US' },
  { lang: 'de', target: 'DE' },
];

const LOCALES_DIR = path.join(rootDir, 'src', 'locales');
const SOURCE_FILE = path.join(LOCALES_DIR, 'es', 'translation.json');

async function translateText(text, targetLang) {
  const body = new URLSearchParams({
    auth_key: DEEPL_API_KEY,
    text,
    source_lang: 'ES',
    target_lang: targetLang,
    tag_handling: 'html',
    preserve_formatting: '1',
  });
  const res = await fetch(DEEPL_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  if (!res.ok) throw new Error('DeepL ' + res.status + ': ' + await res.text());
  const data = await res.json();
  return data.translations[0].text;
}

async function translateObj(obj, targetLang, keyPath) {
  if (typeof obj === 'string') {
    if (!obj.trim()) return obj;
    try { return await translateText(obj, targetLang); }
    catch (e) { console.warn('warn', keyPath, e.message); return obj; }
  }
  if (Array.isArray(obj)) {
    const results = [];
    for (let i = 0; i < obj.length; i++) {
      results.push(await translateObj(obj[i], targetLang, keyPath + '[' + i + ']'));
    }
    return results;
  }
  if (obj && typeof obj === 'object') {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      out[k] = await translateObj(v, targetLang, keyPath + '.' + k);
    }
    return out;
  }
  return obj;
}

function extractMissing(src, tgt) {
  if (!src || typeof src !== 'object') return {};
  const out = {};
  for (const k of Object.keys(src)) {
    if (!(k in tgt)) {
      out[k] = src[k];
    } else if (src[k] && typeof src[k] === 'object' && !Array.isArray(src[k])
               && tgt[k] && typeof tgt[k] === 'object' && !Array.isArray(tgt[k])) {
      const nested = extractMissing(src[k], tgt[k]);
      if (Object.keys(nested).length) out[k] = nested;
    }
  }
  return out;
}

function deepMerge(tgt, add) {
  const out = { ...tgt };
  for (const [k, v] of Object.entries(add)) {
    if (k in out && out[k] && typeof out[k] === 'object' && !Array.isArray(out[k])
        && v && typeof v === 'object' && !Array.isArray(v)) {
      out[k] = deepMerge(out[k], v);
    } else {
      out[k] = v;
    }
  }
  return out;
}

async function main() {
  console.log('Brickclinic Translation Sync');
  const source = JSON.parse(fs.readFileSync(SOURCE_FILE, 'utf-8'));
  console.log('Source: es/translation.json (' + Object.keys(source).length + ' top-level keys)');

  for (const { lang, target } of TARGETS) {
    const file = path.join(LOCALES_DIR, lang, 'translation.json');
    console.log('');
    console.log('Processing: ' + lang + ' -> DeepL(' + target + ')');
    let existing = {};
    if (fs.existsSync(file)) {
      existing = JSON.parse(fs.readFileSync(file, 'utf-8'));
    }
    const missing = extractMissing(source, existing);
    const missingKeys = Object.keys(missing);
    if (!missingKeys.length) {
      console.log('  Up to date. Skipping.');
      continue;
    }
    console.log('  Missing top-level keys: ' + missingKeys.join(', '));
    console.log('  Translating...');
    const translated = await translateObj(missing, target, '');
    const merged = deepMerge(existing, translated);
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, JSON.stringify(merged, null, 4), 'utf-8');
    console.log('  Written: ' + file);
  }
  console.log('');
  console.log('Sync complete!');
}

main().catch(e => { console.error('Fatal error:', e); process.exit(1); });
