#!/usr/bin/env node
/**
 * Example: generate a Circle of Trust network diagram.
 *
 * Usage:
 *   node example.js                           # prints JSON to stdout
 *   node example.js > my-diagram.excalidraw   # write to file
 *
 * Then embed in Obsidian:
 *   ![[my-diagram.excalidraw]]
 */

'use strict';

const ex = require('./shapes');

// --- Node positions ---
// Layout: Rose at top center, Bob/Carol in middle, Sarah/Frank at bottom
const ROSE   = { x: 560,  y: 40,  w: 200, h: 80, cx: 660, cy: 80  };
const BOB    = { x: 160,  y: 260, w: 200, h: 80, cx: 260, cy: 300 };
const CAROL  = { x: 960,  y: 260, w: 200, h: 80, cx: 1060, cy: 300 };
const SARAH  = { x: 40,   y: 500, w: 200, h: 80, cx: 140, cy: 540 };
const FRANK  = { x: 1100, y: 500, w: 200, h: 80, cx: 1200, cy: 540 };

const elements = [
  // Nodes
  ...ex.node('rose',  ROSE.x,  ROSE.y,  ROSE.w,  ROSE.h,  'Rose\nWard (pays)\nno Guardian role'),
  ...ex.node('bob',   BOB.x,   BOB.y,   BOB.w,   BOB.h,   'Bob\nWard (pays)\nGuardian → Rose'),
  ...ex.node('carol', CAROL.x, CAROL.y, CAROL.w, CAROL.h, 'Carol\nWard (pays)\nGuardian → Rose, Bob'),
  ...ex.node('sarah', SARAH.x, SARAH.y, SARAH.w, SARAH.h, 'Sarah\nWard (pays)\nMutual w/ Bob'),
  ...ex.node('frank', FRANK.x, FRANK.y, FRANK.w, FRANK.h, 'Frank\nGuardian only\n(no Ward acct, free)', {
    strokeColor: '#6b7280',
    strokeStyle: 'dashed',
  }),

  // Arrows (Guardian → Ward direction)
  ex.arrow('a_bob_rose',   'bob',   'rose',  [BOB.cx,   BOB.cy],   [ROSE.cx,  ROSE.cy],  { startFocus:  0.3, endFocus: -0.4, label: 'guards' }),
  ex.arrow('a_carol_rose', 'carol', 'rose',  [CAROL.cx, CAROL.cy], [ROSE.cx,  ROSE.cy],  { startFocus: -0.3, endFocus:  0.4, label: 'guards' }),
  ex.arrow('a_sarah_bob',  'sarah', 'bob',   [SARAH.cx, SARAH.cy], [BOB.cx,   BOB.cy],   { startFocus:  0.4, endFocus: -0.4, label: 'guards' }),
  ex.arrow('a_bob_sarah',  'bob',   'sarah', [BOB.cx,   BOB.cy],   [SARAH.cx, SARAH.cy], { startFocus: -0.4, endFocus:  0.4, label: 'guards' }),
  ex.arrow('a_carol_bob',  'carol', 'bob',   [CAROL.cx, CAROL.cy], [BOB.cx,   BOB.cy],   { label: 'also guards' }),
  ex.arrow('a_frank_carol','frank', 'carol', [FRANK.cx, FRANK.cy], [CAROL.cx, CAROL.cy], { label: 'guards' }),

  // MUTUAL annotation
  ex.floatingLabel('mutual_lbl', 100, 470, '← MUTUAL →', { fontSize: 10 }),

  // Legend
  ...ex.annotationBox('legend', 1020, 40, 320, 155,
    'Legend\n\nSolid blue border = Ward (pays)\nDashed gray border = Guardian only\n\nArrow direction: Guardian → Ward\n(Bob guards Rose = arrow points to Rose)\n\nMUTUAL = both guard each other',
    { strokeColor: '#d1d5db', fontSize: 12 }
  ),
];

process.stdout.write(JSON.stringify(ex.document(elements), null, 2) + '\n');
