#!/usr/bin/env node
/**
 * Write an .excalidraw diagram into an Obsidian vault through the `obsidian` CLI,
 * handling the full create + chunked-append + verify dance automatically.
 *
 * This is the ONE entry point for writing diagrams to iCloud-synced vaults
 * (paths under ~/Library/Mobile Documents/...), where the filesystem is
 * TCC-blocked and only the Obsidian app can touch files. It also works for any
 * other vault, since the CLI proxies to the running app regardless.
 *
 * Why a dedicated writer (lessons this encodes):
 *   - The CLI forwards args to the running app over a process-singleton socket
 *     with a payload ceiling (~10-11KB). Larger `content=` fails: either a
 *     silent broken pipe (exit 0, nothing written) or an "Argument must be a
 *     file path or a NativeImage" error. So the JSON body is split into
 *     sub-limit chunks (default 8000B) and streamed with `append`.
 *   - The CLI's confirmation line ("Created:"/"Overwrote:"/"Appended to:") is
 *     UNRELIABLE: it is printed for small payloads but OMITTED for larger ones
 *     that still succeed (~5-10KB appends write fine yet echo nothing). So we do
 *     NOT gate on it. The real success gate is a read-back element count.
 *   - `append` inserts a real newline between chunks — harmless because we split
 *     the compact JSON BETWEEN elements (outside any string), so the reassembled
 *     multi-line JSON is still valid. (Requires single-line labels: no \n/\t/\"
 *     inside any text value — guarded below.)
 *   - Overwriting a note that is CURRENTLY OPEN in Obsidian silently no-ops.
 *     Close the note (or write a fresh path) before updating; the read-back
 *     verify will catch the stale state.
 *   - The CLI emits banner noise ("Loading updated app package…", "installer is
 *     out of date", update-check timestamps) and an intermittent "NativeImage"
 *     error; banners are filtered and transient errors are retried.
 *
 * Usage (MUST run unsandboxed — the CLI hangs under the command sandbox):
 *   node scripts/your-generator.js > "$TMPDIR/diagram.excalidraw"
 *   node scripts/write-to-vault.js \
 *     --vault "My Vault" \
 *     --path  "Diagrams/my-diagram.excalidraw.md" \
 *     --input "$TMPDIR/diagram.excalidraw"
 *
 *   # or pipe the diagram in on stdin:
 *   node scripts/your-generator.js | node scripts/write-to-vault.js \
 *     --vault "My Vault" --path "Diagrams/my-diagram.excalidraw.md"
 *
 * Flags:
 *   --vault <name>      (required) vault name as shown by `obsidian vaults`
 *   --path  <path>      (required) target note path; coerced to end in .excalidraw.md
 *   --input <file>      diagram JSON file (default: stdin)
 *   --chunk-bytes <n>   max append payload (default 9000; keep well under ~12KB)
 *   --no-verify         skip the read-back JSON validation
 */
'use strict';

const fs = require('fs');
const { spawnSync } = require('child_process');

// ---------------------------------------------------------------- arg parsing
function parseArgs(argv) {
  const out = { chunkBytes: 8000, verify: true };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--vault') out.vault = argv[++i];
    else if (a === '--path') out.path = argv[++i];
    else if (a === '--input') out.input = argv[++i];
    else if (a === '--chunk-bytes') out.chunkBytes = parseInt(argv[++i], 10);
    else if (a === '--no-verify') out.verify = false;
    else die(`unknown argument: ${a}`);
  }
  if (!out.vault) die('missing --vault');
  if (!out.path) die('missing --path');
  return out;
}

function die(msg) {
  console.error(`write-to-vault: ${msg}`);
  process.exit(1);
}

const BANNER = /Loading updated app package|installer is out of date|Checking for update|Latest version is|App is up to date|^\s*Success\.\s*$|^\s*20\d\d-\d\d-\d\d /;
function filterBanner(s) {
  return (s || '').split('\n').filter(l => l && !BANNER.test(l)).join('\n');
}

const HARD_ERR = ['Broken pipe', 'write() failed', 'not found', 'may require a plugin'];
const TRANSIENT = ['NativeImage']; // intermittent CLI/Electron hiccup — retry
function sleep(ms) { spawnSync(process.execPath, ['-e', `setTimeout(()=>{}, ${ms})`]); }

// Run one obsidian CLI command, retrying transient errors and timeouts.
// Returns the banner-filtered output. Hard errors abort. The confirmation line
// is NOT required (it is omitted for larger successful payloads) — correctness
// is gated by the final read-back verify instead.
function obsidian(args, { timeout = 60000, retries = 3 } = {}) {
  for (let attempt = 1; ; attempt++) {
    const r = spawnSync('obsidian', args, { encoding: 'utf8', timeout, maxBuffer: 64 * 1024 * 1024 });
    if (r.error) {
      if (r.error.code === 'ENOENT') die('`obsidian` CLI not found on PATH.');
      if (r.error.code === 'ETIMEDOUT') {
        if (attempt <= retries) { console.error(`  (timeout, retry ${attempt}/${retries})`); sleep(3000); continue; }
        die(`CLI timed out (${timeout}ms) after ${retries} retries. Run UNSANDBOXED (the socket hangs under the sandbox); the app may also be wedged — restart Obsidian.`);
      }
      die(`CLI spawn error: ${r.error.message}`);
    }
    const out = `${filterBanner(r.stdout)}\n${filterBanner(r.stderr)}`.trim();
    if (TRANSIENT.some(m => out.includes(m)) && attempt <= retries) {
      console.error(`  (transient CLI error, retry ${attempt}/${retries})`); sleep(2500); continue;
    }
    const hit = HARD_ERR.find(m => out.includes(m));
    if (hit) { console.error(out); die(`CLI error ("${hit}"). Check the vault name, path, and that the payload is under --chunk-bytes.`); }
    return out;
  }
}

// ---------------------------------------------------------------- main
const opts = parseArgs(process.argv.slice(2));

// Coerce path so the embed resolves: obsidian create only writes .md, and
// `![[x.excalidraw]]` resolves to x.excalidraw.md.
let notePath = opts.path;
if (notePath.endsWith('.excalidraw')) notePath += '.md';
else if (!notePath.endsWith('.excalidraw.md')) {
  console.error(`write-to-vault: warning — --path does not end in .excalidraw.md (got "${notePath}"); the embed may not resolve.`);
}

const raw = opts.input ? fs.readFileSync(opts.input, 'utf8') : fs.readFileSync(0, 'utf8');
let doc;
try { doc = JSON.parse(raw); } catch (e) { die(`input is not valid JSON: ${e.message}`); }
if (!Array.isArray(doc.elements)) die('input JSON has no `elements` array — is this an .excalidraw document?');

// Escape guard: any backslash in the compact JSON (a \n, \t, \\, or \" inside a
// text value) would be corrupted by the CLI's content= interpretation.
const compact = JSON.stringify(doc);
if (compact.includes('\\')) {
  die('drawing JSON contains escaped characters (a newline, tab, backslash, or quote inside a label).\n' +
      '       Use plain SINGLE-LINE labels with no " characters for CLI writes.');
}

// --- Build the markdown header (everything up to and including the ```json fence).
const textEls = doc.elements
  .filter(e => e.type === 'text' && typeof e.text === 'string')
  .map(e => `${e.text} ^${e.id}`);
const headerLines = [
  '---', '', 'excalidraw-plugin: parsed', 'tags: [excalidraw]', '', '---',
  '==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==',
  '', '# Excalidraw Data', '', '## Text Elements', ...textEls, '',
  '%%', '## Drawing', '```json',
];
// Literal "\n" markers — the CLI expands them into real newlines on write.
const headerContent = headerLines.join('\\n');

// --- Split the JSON body BETWEEN elements so each append stays under the limit.
const prefix = '{"type":"excalidraw","version":2,"source":"https://excalidraw.com","elements":[';
const suffix = '],"appState":' + JSON.stringify(doc.appState || { gridSize: null, viewBackgroundColor: '#ffffff' }) +
               ',"files":' + JSON.stringify(doc.files || {}) + '}';
const elemStrs = doc.elements.map(e => JSON.stringify(e));

const groups = [];
let cur = [], curLen = 0;
for (const s of elemStrs) {
  if (s.length + prefix.length > opts.chunkBytes) {
    die(`a single element serializes to ${s.length} bytes, over --chunk-bytes ${opts.chunkBytes}. Raise --chunk-bytes (stay under ~12000).`);
  }
  if (cur.length && curLen + s.length + 1 > opts.chunkBytes) { groups.push(cur); cur = []; curLen = 0; }
  cur.push(s); curLen += s.length + 1;
}
if (cur.length) groups.push(cur);

// First append: prefix + elems ; middle: ,elems ; last also closes with suffix.
const bodies = groups.map((g, i) => {
  let s = (i === 0 ? prefix : ',') + g.join(',');
  if (i === groups.length - 1) s += suffix;
  return s;
});

// Local reassembly sanity check before touching the vault.
const reassembled = bodies.join('');
let parsed;
try { parsed = JSON.parse(reassembled); } catch (e) { die(`internal: reassembled body is not valid JSON: ${e.message}`); }
if (parsed.elements.length !== doc.elements.length) die('internal: reassembly changed element count');

// ---------------------------------------------------------------- write
const V = `vault=${opts.vault}`;
const P = `path=${notePath}`;
const log = (m) => console.error(m);

log(`write-to-vault: ${doc.elements.length} elements, ${bodies.length} chunk(s) → ${opts.vault}:${notePath}`);

obsidian(['create', V, P, `content=${headerContent}`, 'overwrite']);
log(`  header written (${textEls.length} text elements)`);

bodies.forEach((b, i) => {
  obsidian(['append', V, P, `content=${b}`]);
  log(`  append ${i + 1}/${bodies.length} (${b.length} bytes)`);
});

obsidian(['append', V, P, 'content=```']);
obsidian(['append', V, P, 'content=%%']);
log('  closing fence written');

// ---------------------------------------------------------------- verify
// This is the authoritative success check — the per-call confirmation lines are
// unreliable, so we confirm the whole document round-tripped by element count.
if (opts.verify) {
  const back = obsidian(['read', V, P]); // read prints the note
  const m = back.split('\n');
  let f = false; const json = [];
  for (const l of m) {
    if (l.trim() === '```json') { f = true; continue; }
    if (f && l.trim() === '```') break;
    if (f) json.push(l);
  }
  let v;
  try { v = JSON.parse(json.join('\n')); }
  catch (e) {
    die(`verify: read-back JSON did not parse (${e.message}).\n` +
        '       Likely the target note was OPEN in Obsidian (overwrite no-ops on open notes) ' +
        'or a chunk exceeded the IPC limit. Close the note or lower --chunk-bytes, then retry.');
  }
  if (v.elements.length !== doc.elements.length) {
    die(`verify: read-back has ${v.elements.length} elements, expected ${doc.elements.length}.\n` +
        '       The note may have been OPEN in Obsidian (close it) or a chunk was dropped (lower --chunk-bytes).');
  }
  log(`  verified: ${v.elements.length} elements round-tripped`);
} else {
  log('  (verify skipped — pass without --no-verify to confirm the write)');
}

log('write-to-vault: done');
