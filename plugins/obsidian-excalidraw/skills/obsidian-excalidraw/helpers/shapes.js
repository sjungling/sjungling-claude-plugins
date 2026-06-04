/**
 * Excalidraw shape factory for Obsidian.
 *
 * Generates valid Excalidraw JSON elements with no external dependencies.
 *
 * Usage (require):
 *   const ex = require('./shapes');
 *   const elements = [
 *     ...ex.node('alice', 100, 80, 180, 70, 'Alice\nWard'),
 *     ...ex.node('bob',   400, 80, 180, 70, 'Bob\nGuardian', { strokeStyle: 'dashed' }),
 *     ex.arrow('a1', 'bob', 'alice', [490, 115], [190, 115]),
 *   ];
 *   require('fs').writeFileSync('out.excalidraw', JSON.stringify(ex.document(elements), null, 2));
 */

'use strict';

let _seed = 1000;
const nextSeed = () => ++_seed;
const ts = 1717500000000; // fixed timestamp — deterministic output

// Base fields shared by all elements
function base(id, type, x, y, w, h, opts = {}) {
  const seed = nextSeed();
  return {
    id,
    type,
    x,
    y,
    width: w,
    height: h,
    angle: 0,
    strokeColor: opts.strokeColor || '#374151',
    backgroundColor: opts.backgroundColor || '#ffffff',
    fillStyle: opts.fillStyle || 'solid',
    strokeWidth: opts.strokeWidth != null ? opts.strokeWidth : 2,
    strokeStyle: opts.strokeStyle || 'solid',
    roughness: 0,
    opacity: 100,
    groupIds: [],
    roundness: opts.roundness !== undefined ? opts.roundness : { type: 2 },
    seed,
    version: 1,
    versionNonce: seed,
    isDeleted: false,
    boundElements: opts.boundElements || [],
    updated: ts,
    link: null,
    locked: false,
  };
}

// Text element — either bound (containerId set) or floating
function textEl(id, containerId, x, y, w, h, text, opts = {}) {
  const seed = nextSeed();
  const fontSize = opts.fontSize || 13;
  return {
    id,
    type: 'text',
    x,
    y,
    width: w,
    height: h,
    angle: 0,
    strokeColor: opts.strokeColor || '#1e1e2e',
    backgroundColor: 'transparent',
    fillStyle: 'hachure',
    strokeWidth: 1,
    strokeStyle: 'solid',
    roughness: 0,
    opacity: 100,
    groupIds: [],
    seed,
    version: 1,
    versionNonce: seed,
    isDeleted: false,
    boundElements: [],
    updated: ts,
    link: null,
    locked: false,
    text,
    originalText: text,
    fontSize,
    fontFamily: opts.fontFamily || 1,
    textAlign: opts.textAlign || 'center',
    verticalAlign: opts.verticalAlign || 'middle',
    baseline: fontSize,
    containerId: containerId || null,
  };
}

/**
 * Ellipse node with a bound text label.
 * Returns [ellipse, text] — spread into your elements array.
 *
 * @param {string} id
 * @param {number} x - top-left x
 * @param {number} y - top-left y
 * @param {number} w - width
 * @param {number} h - height
 * @param {string} label - text content, use \n for line breaks
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, backgroundColor, fontSize
 */
function node(id, x, y, w, h, label, opts = {}) {
  const textId = `${id}_t`;
  const shape = {
    ...base(id, 'ellipse', x, y, w, h, opts),
    boundElements: label ? [{ type: 'text', id: textId }] : [],
  };
  if (!label) return [shape];
  const text = textEl(textId, id, x + 4, y + 4, w - 8, h - 8, label, opts);
  return [shape, text];
}

/**
 * Rectangle node with a bound text label.
 * Returns [rect, text] — spread into your elements array.
 *
 * @param {string} id
 * @param {number} x - top-left x
 * @param {number} y - top-left y
 * @param {number} w - width
 * @param {number} h - height
 * @param {string} label - text content
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, backgroundColor, rounded (bool), fontSize
 */
function box(id, x, y, w, h, label, opts = {}) {
  const textId = `${id}_t`;
  const rounded = opts.rounded !== false; // default rounded
  const shape = {
    ...base(id, 'rectangle', x, y, w, h, { ...opts, roundness: rounded ? { type: 3 } : null }),
    boundElements: label ? [{ type: 'text', id: textId }] : [],
  };
  if (!label) return [shape];
  const text = textEl(textId, id, x + 8, y + 8, w - 16, h - 16, label, { ...opts, textAlign: opts.textAlign || 'left', verticalAlign: 'top' });
  return [shape, text];
}

/**
 * Annotation/callout box — rectangle with left-aligned, top-aligned text.
 * Returns [rect, text] — spread into your elements array.
 *
 * @param {string} id
 * @param {number} x
 * @param {number} y
 * @param {number} w
 * @param {number} h
 * @param {string} text - multi-line content
 * @param {object} opts - strokeColor, fontSize
 */
function annotationBox(id, x, y, w, h, text, opts = {}) {
  return box(id, x, y, w, h, text, {
    strokeColor: opts.strokeColor || '#d1d5db',
    strokeWidth: 1,
    fontSize: opts.fontSize || 12,
    textAlign: 'left',
    verticalAlign: 'top',
    ...opts,
  });
}

/**
 * Directional arrow between two shapes, bound to their IDs.
 *
 * @param {string} id
 * @param {string} fromId - ID of source shape
 * @param {string} toId   - ID of target shape
 * @param {number[]} fromCenter - [x, y] center of source shape (for path direction)
 * @param {number[]} toCenter   - [x, y] center of target shape
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, startFocus, endFocus, gap, label
 */
function arrow(id, fromId, toId, fromCenter, toCenter, opts = {}) {
  const dx = toCenter[0] - fromCenter[0];
  const dy = toCenter[1] - fromCenter[1];
  const gap = opts.gap != null ? opts.gap : 6;
  const seed = nextSeed();

  const el = {
    id,
    type: 'arrow',
    x: fromCenter[0],
    y: fromCenter[1],
    width: Math.abs(dx),
    height: Math.abs(dy),
    angle: 0,
    strokeColor: opts.strokeColor || '#374151',
    backgroundColor: 'transparent',
    fillStyle: 'hachure',
    strokeWidth: opts.strokeWidth != null ? opts.strokeWidth : 2,
    strokeStyle: opts.strokeStyle || 'solid',
    roughness: 0,
    opacity: 100,
    groupIds: [],
    roundness: { type: 2 },
    seed,
    version: 1,
    versionNonce: seed,
    isDeleted: false,
    boundElements: [],
    updated: ts,
    link: null,
    locked: false,
    points: [[0, 0], [dx, dy]],
    lastCommittedPoint: null,
    startBinding: { elementId: fromId, focus: opts.startFocus || 0, gap },
    endBinding: { elementId: toId, focus: opts.endFocus || 0, gap },
    startArrowhead: opts.startArrowhead || null,
    endArrowhead: opts.endArrowhead != null ? opts.endArrowhead : 'arrow',
    elbowed: false,
  };

  if (!opts.label) return el;

  // Attach a floating label near the midpoint
  const midX = fromCenter[0] + dx / 2 - 30;
  const midY = fromCenter[1] + dy / 2 - 16;
  const lbl = floatingLabel(`${id}_lbl`, midX, midY, opts.label, {
    fontSize: 11,
    strokeColor: opts.strokeColor || '#6b7280',
  });

  return [el, lbl];
}

/**
 * Floating text label (not bound to any shape).
 *
 * @param {string} id
 * @param {number} x
 * @param {number} y
 * @param {string} text
 * @param {object} opts - fontSize, strokeColor, textAlign
 */
function floatingLabel(id, x, y, text, opts = {}) {
  const fontSize = opts.fontSize || 12;
  const approxW = text.length * (fontSize * 0.6);
  const approxH = (text.split('\n').length) * (fontSize * 1.4);
  return textEl(id, null, x, y, Math.max(approxW, 40), Math.max(approxH, fontSize + 4), text, {
    ...opts,
    textAlign: opts.textAlign || 'center',
    verticalAlign: 'top',
  });
}

/**
 * Wraps an elements array in the top-level Excalidraw document structure.
 *
 * @param {Array} elements - flat array of element objects
 * @param {object} opts - viewBackgroundColor
 * @returns {object} ready to JSON.stringify and write as .excalidraw
 */
function document(elements, opts = {}) {
  // Flatten one level — allows passing [...node(), arrow()] without manual spreading
  const flat = elements.flat(1).filter(Boolean);
  return {
    type: 'excalidraw',
    version: 2,
    source: 'https://excalidraw.com',
    elements: flat,
    appState: {
      gridSize: null,
      viewBackgroundColor: opts.viewBackgroundColor || '#ffffff',
    },
    files: {},
  };
}

module.exports = { node, box, annotationBox, arrow, floatingLabel, document };
