#!/usr/bin/env node
/**
 * Convert a .excalidraw JSON document into the single-line .excalidraw.md note
 * content needed to write a diagram into an iCloud (TCC-blocked) Obsidian vault
 * via the Obsidian CLI's `create content=...`.
 *
 * Background: Claude's process cannot write the filesystem for iCloud vaults
 * (paths under ~/Library/Mobile Documents/...) — only the Obsidian app can.
 * `obsidian create` writes through the app, but it (a) forces a .md extension
 * and (b) converts "\n"/"\t"/"\\" in content= into real characters. So we emit
 * the markdown wrapper using literal "\n" markers (the CLI rebuilds the lines)
 * while the embedded drawing JSON stays COMPACT — one line, no escape
 * sequences for the CLI to corrupt. See references/icloud-vaults.md.
 *
 * Usage:
 *   node scripts/your-generator.js | node scripts/to-obsidian-md.js > /tmp/note.txt
 *   obsidian create vault="My Vault" path="Diagrams/foo.excalidraw.md" \
 *     content="$(cat /tmp/note.txt)" overwrite
 *
 *   # or read from a file argument:
 *   node scripts/to-obsidian-md.js diagram.excalidraw > /tmp/note.txt
 */
'use strict';

const fs = require('fs');

const input = process.argv[2]
  ? fs.readFileSync(process.argv[2], 'utf8')
  : fs.readFileSync(0, 'utf8'); // stdin

let doc;
try {
  doc = JSON.parse(input);
} catch (e) {
  console.error(`to-obsidian-md: input is not valid JSON: ${e.message}`);
  process.exit(1);
}

// Compact => no structural newlines in the drawing block.
const compact = JSON.stringify(doc);

// The CLI's content= interprets escape sequences. Plain single-line labels
// produce zero backslashes in the compact JSON; anything escaped (a newline,
// tab, backslash, or quote inside a text value) would be corrupted on write.
// Fail loudly rather than silently produce a broken file.
if (compact.includes('\\')) {
  console.error(
    'to-obsidian-md: drawing JSON contains escaped characters (a newline, tab, ' +
    'backslash, or quote inside a text value).\n' +
    'The Obsidian CLI would corrupt these. Use plain SINGLE-LINE labels for CLI ' +
    'writes, or write the .excalidraw file directly to a filesystem-writable vault.'
  );
  process.exit(1);
}

// Text Elements section indexes each text element for Obsidian search/backlinks.
const textEls = (doc.elements || [])
  .filter(e => e.type === 'text' && typeof e.text === 'string')
  .map(e => `${e.text} ^${e.id}`);

const lines = [
  '---',
  '',
  'excalidraw-plugin: parsed',
  'tags: [excalidraw]',
  '',
  '---',
  '==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==',
  '',
  '# Excalidraw Data',
  '',
  '## Text Elements',
  ...textEls,
  '',
  '%%',
  '## Drawing',
  '```json',
  compact,
  '```',
  '%%',
];

// One physical line; the literal "\n" markers become real newlines on CLI write.
process.stdout.write(lines.join('\\n'));
