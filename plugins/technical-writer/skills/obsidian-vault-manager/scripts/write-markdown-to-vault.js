#!/usr/bin/env node
/**
 * Write a plain markdown note into an Obsidian vault through the `obsidian`
 * CLI, chunked to stay under the CLI's IPC payload ceiling, with banner
 * filtering, transient-error retries, and a read-back verify.
 *
 * This is the reliable path for iCloud-synced vaults (paths under
 * ~/Library/Mobile Documents/iCloud~md~obsidian/Documents/<name>): TCC can
 * block direct filesystem read/write to that path even with the sandbox
 * disabled, so a plain `Write` tool call is not guaranteed to land. The
 * `obsidian` CLI proxies to the running app, which holds the entitlement.
 * Also works for any other vault.
 *
 * Adapted from obsidian-excalidraw's write-to-vault.js (same plugin repo) —
 * same lessons (payload ceiling, unreliable confirmation line, run
 * unsandboxed) — simplified for plain markdown: there's no JSON structure to
 * split on, so the escaped content is chunked at arbitrary byte boundaries
 * (never inside a `\n`/`\t` escape pair) and every chunk after the first is
 * appended with `inline` so no extra newline is introduced at the seam.
 *
 * CORRECTION vs write-to-vault.js's stated assumption: empirically (CLI
 * 1.12.7) the CLI does NOT unescape `\\` → `\`. It does a single left-to-right
 * scan for literal `\n`/`\t` and converts matches to real newline/tab; any
 * other backslash is left untouched. There is therefore no way to escape a
 * literal backslash — source text that already contains a literal `\n` or
 * `\t` (e.g. a code sample describing escape sequences) will be silently
 * corrupted into a real newline/tab. This script does NOT attempt to double-
 * escape backslashes (that doesn't help — verified by testing — and only adds
 * stray characters); it instead warns when this is detected.
 *
 * Usage (MUST run unsandboxed — the CLI hangs under the command sandbox):
 *   node write-markdown-to-vault.js --vault "My Vault" --path "Folder/Note.md" --input note.md [--overwrite]
 *   cat note.md | node write-markdown-to-vault.js --vault "My Vault" --path "Folder/Note.md"
 *
 * Flags:
 *   --vault <name>      (required) vault name as shown by `obsidian vaults`
 *   --path  <path>      (required) vault-relative note path, must end in .md
 *   --input <file>      markdown source (default: stdin)
 *   --chunk-bytes <n>   max content= payload per call (default 8000; keep well under ~12KB)
 *   --overwrite         allow replacing an existing note (default: CLI errors if it exists)
 *   --no-verify         skip the read-back length validation
 */
'use strict';

const fs = require('fs');
const { spawnSync } = require('child_process');

// ---------------------------------------------------------------- arg parsing
function parseArgs(argv) {
  const out = { chunkBytes: 8000, overwrite: false, verify: true };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--vault') out.vault = argv[++i];
    else if (a === '--path') out.path = argv[++i];
    else if (a === '--input') out.input = argv[++i];
    else if (a === '--chunk-bytes') out.chunkBytes = parseInt(argv[++i], 10);
    else if (a === '--overwrite') out.overwrite = true;
    else if (a === '--no-verify') out.verify = false;
    else die(`unknown argument: ${a}`);
  }
  if (!out.vault) die('missing --vault');
  if (!out.path) die('missing --path');
  if (!out.path.endsWith('.md')) die(`--path must end in .md (got "${out.path}")`);
  return out;
}

function die(msg) {
  console.error(`write-markdown-to-vault: ${msg}`);
  process.exit(1);
}

const BANNER = /Loading updated app package|installer is out of date|Checking for update|Latest version is|App is up to date|^\s*Success\.\s*$|^\s*20\d\d-\d\d-\d\d /;
function filterBanner(s) {
  // Only drop lines that actually match a banner pattern — NOT blank lines.
  // Blank lines are semantically meaningful in markdown (paragraph breaks,
  // spacing around code fences); an earlier `l && ...` truthy filter here
  // silently ate every blank line in read-back output, producing false
  // verify mismatches even when the write was byte-perfect.
  return (s || '').split('\n').filter(l => !BANNER.test(l)).join('\n');
}

const HARD_ERR = ['Broken pipe', 'write() failed', 'may require a plugin'];
const TRANSIENT = ['NativeImage']; // intermittent CLI/Electron hiccup — retry
function sleep(ms) { spawnSync(process.execPath, ['-e', `setTimeout(()=>{}, ${ms})`]); }

// Run one obsidian CLI command, retrying transient errors and timeouts.
// Returns the banner-filtered output. Hard errors abort. The confirmation
// line is NOT required (it can be omitted for larger successful payloads) —
// correctness is gated by the final read-back verify instead.
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

// Escape real newline/tab characters into the literal two-char markers the
// CLI's content= parser expands back into newline/tab.
//
// IMPORTANT (empirically verified against CLI 1.12.7, not just inferred from
// docs): the CLI does a single left-to-right scan for the literal 2-char
// sequences `\n` / `\t` and converts each to a real newline/tab. It does NOT
// have a `\\` → `\` unescape pass — a literal backslash is left untouched
// UNLESS the very next character is 'n' or 't', in which case the pair is
// consumed as a newline/tab regardless of intent. There is no way to escape
// a literal backslash for this CLI. Consequence: source content that already
// contains a literal backslash immediately followed by 'n' or 't' (e.g. a
// code sample discussing `\n`/`\t` escape sequences, or a Windows path) WILL
// be silently corrupted into a real newline/tab on write. We warn about this
// below rather than attempting to "fix" it (there is no fix).
function escapeForCli(s) {
  return s.replace(/\n/g, '\\n').replace(/\t/g, '\\t');
}

function warnAboutLiteralEscapes(raw) {
  const matches = raw.match(/\\[nt]/g);
  if (matches && matches.length) {
    console.error(
      `write-markdown-to-vault: warning — source contains ${matches.length} literal ` +
      '"\\n"/"\\t" sequence(s) (e.g. inside a code sample). The obsidian CLI cannot ' +
      'distinguish these from real newline/tab escapes and WILL convert them to actual ' +
      'newlines/tabs on write. This is a CLI limitation, not a bug in this script.'
    );
  }
}

// Split an already-escaped string into <= chunkBytes pieces without ever
// splitting between a backslash and the character it escapes.
function chunkEscaped(escaped, chunkBytes) {
  const chunks = [];
  let i = 0;
  while (i < escaped.length) {
    let end = Math.min(i + chunkBytes, escaped.length);
    if (escaped[end - 1] === '\\' && end < escaped.length) end -= 1;
    chunks.push(escaped.slice(i, end));
    i = end;
  }
  return chunks;
}

// ---------------------------------------------------------------- main
const opts = parseArgs(process.argv.slice(2));
const raw = opts.input ? fs.readFileSync(opts.input, 'utf8') : fs.readFileSync(0, 'utf8');
if (!raw.trim()) die('input content is empty');
warnAboutLiteralEscapes(raw);

const escaped = escapeForCli(raw);
const chunks = chunkEscaped(escaped, opts.chunkBytes);

const V = `vault=${opts.vault}`;
const P = `path=${opts.path}`;
const log = (m) => console.error(m);

log(`write-markdown-to-vault: ${raw.length} bytes, ${chunks.length} chunk(s) → ${opts.vault}:${opts.path}`);

const createArgs = ['create', V, P, `content=${chunks[0]}`];
if (opts.overwrite) createArgs.push('overwrite');
obsidian(createArgs);
log(`  chunk 1/${chunks.length} written (create${opts.overwrite ? ', overwrite' : ''})`);

for (let i = 1; i < chunks.length; i++) {
  obsidian(['append', V, P, `content=${chunks[i]}`, 'inline']);
  log(`  chunk ${i + 1}/${chunks.length} written (append, inline)`);
}

// ---------------------------------------------------------------- verify
// The per-call confirmation line is unreliable for larger payloads (see
// write-to-vault.js), so the real success gate is a read-back comparison.
if (opts.verify) {
  const back = obsidian(['read', V, P]);
  // `read` may print its own banner/header noise beyond BANNER — compare by
  // checking the note's own content is a substring rather than exact match,
  // since the CLI can wrap output with contextual lines we don't control.
  if (!back.includes(raw.trim().slice(0, 200)) || !back.trim().endsWith(raw.trim().slice(-200))) {
    die('verify: read-back content does not match the start/end of the source.\n' +
        '       The note may have been OPEN in Obsidian (create/append can no-op on open notes)\n' +
        '       or a chunk was dropped. Close the note or lower --chunk-bytes, then retry.');
  }
  log(`  verified: read-back matches source start/end (${raw.length} bytes written)`);
} else {
  log('  (verify skipped — pass without --no-verify to confirm the write)');
}

log('write-markdown-to-vault: done');
