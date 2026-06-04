#!/usr/bin/env node
/**
 * Example: generate a simple org-chart / hierarchy diagram.
 *
 * Usage:
 *   node example.js                        # prints JSON to stdout
 *   node example.js > my-diagram.excalidraw  # write to file
 *
 * Then embed in Obsidian:
 *   ![[my-diagram.excalidraw]]
 */

'use strict';

const ex = require('../scripts/shapes');

// Node positions — CEO at top, two VPs in middle, three ICs at bottom
const CEO  = { x: 511, y: 40,  w: 180, h: 70, cx: 601, cy: 75  };
const VP1  = { x: 200, y: 200, w: 180, h: 70, cx: 290, cy: 235 };
const VP2  = { x: 830, y: 200, w: 180, h: 70, cx: 920, cy: 235 };
const IC1  = { x: 60,  y: 370, w: 180, h: 70, cx: 150, cy: 405 };
const IC2  = { x: 340, y: 370, w: 180, h: 70, cx: 430, cy: 405 };
const IC3  = { x: 830, y: 370, w: 180, h: 70, cx: 920, cy: 405 };

const elements = [
  // Nodes
  ...ex.node('ceo', CEO.x, CEO.y, CEO.w, CEO.h, 'CEO'),
  ...ex.node('vp1', VP1.x, VP1.y, VP1.w, VP1.h, 'VP Engineering'),
  ...ex.node('vp2', VP2.x, VP2.y, VP2.w, VP2.h, 'VP Product'),
  ...ex.node('ic1', IC1.x, IC1.y, IC1.w, IC1.h, 'Engineering', { strokeColor: '#6b7280', strokeStyle: 'dashed' }),
  ...ex.node('ic2', IC2.x, IC2.y, IC2.w, IC2.h, 'Design',      { strokeColor: '#6b7280', strokeStyle: 'dashed' }),
  ...ex.node('ic3', IC3.x, IC3.y, IC3.w, IC3.h, 'Research',    { strokeColor: '#6b7280', strokeStyle: 'dashed' }),

  // Reporting lines (arrow direction: manager → report)
  ex.arrow('a_ceo_vp1', 'ceo', 'vp1', [CEO.cx, CEO.cy], [VP1.cx, VP1.cy], { label: 'reports to' }),
  ex.arrow('a_ceo_vp2', 'ceo', 'vp2', [CEO.cx, CEO.cy], [VP2.cx, VP2.cy], { label: 'reports to' }),
  ex.arrow('a_vp1_ic1', 'vp1', 'ic1', [VP1.cx, VP1.cy], [IC1.cx, IC1.cy], { label: 'manages' }),
  ex.arrow('a_vp1_ic2', 'vp1', 'ic2', [VP1.cx, VP1.cy], [IC2.cx, IC2.cy], { label: 'manages' }),
  ex.arrow('a_vp2_ic3', 'vp2', 'ic3', [VP2.cx, VP2.cy], [IC3.cx, IC3.cy], { label: 'manages' }),

  // Legend
  ...ex.annotationBox('legend', 1060, 40, 240, 100,
    'Legend\n\nSolid blue = primary node\nDashed gray = secondary node\nArrow = relationship',
    { strokeColor: '#d1d5db', fontSize: 12 }
  ),
];

process.stdout.write(JSON.stringify(ex.document(elements), null, 2) + '\n');
