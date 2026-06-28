/**
 * Excalidraw shape factory for Obsidian.
 *
 * Generates valid Excalidraw JSON elements with no external dependencies.
 *
 * Usage (require):
 *   const ex = require('./shapes');
 *   const elements = [
 *     ...ex.node('alpha', 100, 80, 180, 70, 'Alpha\nPrimary'),
 *     ...ex.node('beta',  400, 80, 180, 70, 'Beta\nSecondary', { strokeStyle: 'dashed' }),
 *     ex.arrow('a1', 'beta', 'alpha', [490, 115], [190, 115]),
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
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, startFocus, endFocus, gap, label, labelColor, labelFontSize
 *
 * When `opts.label` is set, the label is a text element BOUND to the arrow
 * (rendered on the line, with a gap, and moving with it) — not a floating
 * caption. Keep arrow labels terse (1–3 words); long labels crowd the line.
 *
 * The shape→arrow back-reference (`boundElements`) is wired automatically by
 * {@link document}, so you only pass the two shape IDs here.
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

  // Bound label: a text element whose containerId is this arrow. Excalidraw
  // pins it to the arrow's midpoint and paints a gap over the line. The arrow
  // must list the label in its own boundElements (the text→container link);
  // document() adds the reverse shape→arrow links.
  const labelId = `${id}_lbl`;
  el.boundElements = [{ type: 'text', id: labelId }];
  const fontSize = opts.labelFontSize || 11;
  const w = Math.max(opts.label.length * fontSize * 0.6, 20);
  const h = fontSize * 1.25;
  const midX = fromCenter[0] + dx / 2;
  const midY = fromCenter[1] + dy / 2;
  const lbl = textEl(labelId, id, midX - w / 2, midY - h / 2, w, h, opts.label, {
    fontSize,
    strokeColor: opts.labelColor || opts.strokeColor || '#374151',
    textAlign: 'center',
    verticalAlign: 'middle',
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
 * Ensure every binding is bidirectional.
 *
 * Excalidraw treats two elements as connected only when BOTH sides reference
 * each other: an arrow names its endpoints via start/endBinding, and each
 * endpoint shape must list the arrow in its own `boundElements`. Likewise a
 * bound text names its host via `containerId`, and the host must list the
 * text. The factories set the forward links; this pass fills in the reverse
 * ones so callers never have to. Idempotent — safe to run on already-linked
 * elements.
 */
function linkBindings(flat) {
  const byId = new Map(flat.map((e) => [e.id, e]));
  const ensure = (host, ref) => {
    if (!host) return; // binding points at an element not in this document
    if (!Array.isArray(host.boundElements)) host.boundElements = [];
    if (!host.boundElements.some((b) => b.id === ref.id)) host.boundElements.push(ref);
  };
  for (const el of flat) {
    if (el.type === 'arrow') {
      const from = el.startBinding && el.startBinding.elementId;
      const to = el.endBinding && el.endBinding.elementId;
      if (from) ensure(byId.get(from), { type: 'arrow', id: el.id });
      if (to) ensure(byId.get(to), { type: 'arrow', id: el.id });
    }
    if (el.type === 'text' && el.containerId) {
      ensure(byId.get(el.containerId), { type: 'text', id: el.id });
    }
  }
  return flat;
}

/**
 * Wraps an elements array in the top-level Excalidraw document structure.
 *
 * @param {Array} elements - flat array of element objects
 * @param {object} opts - viewBackgroundColor
 * @returns {object} ready to JSON.stringify and write as .excalidraw
 */
function document(elements, opts = {}) {
  // Flatten fully — allows passing [...node(), arrow()] without manual spreading
  const flat = linkBindings(elements.flat(Infinity).filter(Boolean));
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

/**
 * Returns the point on an ellipse boundary where a line from (cx,cy) exits toward (tx,ty).
 * Use this to compute arrow start/end points so arrows render edge-to-edge rather than
 * center-to-center in Obsidian's embedded preview (which skips Excalidraw's live binding).
 *
 * @param {number} cx - ellipse center x
 * @param {number} cy - ellipse center y
 * @param {number} a  - semi-axis x (half-width)
 * @param {number} b  - semi-axis y (half-height)
 * @param {number} tx - x of external target point
 * @param {number} ty - y of external target point
 * @returns {[number, number]}
 */
function ellipseEdge(cx, cy, a, b, tx, ty) {
  const dx = tx - cx, dy = ty - cy;
  if (dx === 0 && dy === 0) return [cx + a, cy];
  const t = 1 / Math.sqrt((dx / a) ** 2 + (dy / b) ** 2);
  return [cx + t * dx, cy + t * dy];
}

/**
 * Returns the point on a rectangle boundary where a line from the rect center exits toward (tx,ty).
 * Use with arrow() to produce edge-to-edge arrows: pass rectEdge(...) as fromCenter/toCenter.
 *
 * @param {number} rx - rect left x
 * @param {number} ry - rect top y
 * @param {number} rw - rect width
 * @param {number} rh - rect height
 * @param {number} tx - x of external target point
 * @param {number} ty - y of external target point
 * @returns {[number, number]}
 */
function rectEdge(rx, ry, rw, rh, tx, ty) {
  const cx = rx + rw / 2, cy = ry + rh / 2;
  const dx = tx - cx, dy = ty - cy;
  if (dx === 0 && dy === 0) return [cx, cy];
  const sx = dx !== 0 ? (rw / 2) / Math.abs(dx) : Infinity;
  const sy = dy !== 0 ? (rh / 2) / Math.abs(dy) : Infinity;
  const t = Math.min(sx, sy);
  return [cx + t * dx, cy + t * dy];
}

module.exports = { node, box, annotationBox, arrow, floatingLabel, document, linkBindings, ellipseEdge, rectEdge };
