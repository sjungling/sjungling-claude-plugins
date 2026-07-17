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

/**
 * Real Excalidraw format has no "label" shorthand on containers — a labeled
 * shape/arrow is actually TWO elements: the container, plus a separate `text`
 * element with `containerId` pointing back at it (and the container lists the
 * text element in its own `boundElements`). This builds that text element.
 *
 * @param {string} id - id for the new text element
 * @param {string} containerId - id of the shape/arrow this text is bound to
 * @param {string} text - content (use \n for line breaks)
 * @param {number} cx - x-center of the area the text should occupy
 * @param {number} cy - y-center of the area the text should occupy
 * @param {object} opts - fontSize, strokeColor, textAlign, verticalAlign, maxWidth
 */
function boundText(id, containerId, text, cx, cy, opts = {}) {
  const fontSize = opts.fontSize || 13;
  const lines = String(text).split('\n');
  const charW = fontSize * 0.6;
  const lineH = fontSize * 1.25;
  let width = Math.max(...lines.map((l) => l.length * charW), fontSize);
  if (opts.maxWidth) width = Math.min(width, opts.maxWidth);
  const height = lines.length * lineH;
  const textAlign = opts.textAlign || 'center';
  const verticalAlign = opts.verticalAlign || 'middle';

  // cx/cy denote the center of the available area regardless of alignment —
  // text elements are always positioned by their own top-left x/y + width/height.
  const x = textAlign === 'left' ? cx - (opts.areaWidth ? opts.areaWidth / 2 : width / 2) : cx - width / 2;
  const y = verticalAlign === 'top' ? cy - (opts.areaHeight ? opts.areaHeight / 2 : height / 2) : cy - height / 2;

  const seed = nextSeed();
  return {
    id,
    type: 'text',
    x,
    y,
    width,
    height,
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
    textAlign,
    verticalAlign,
    baseline: fontSize,
    containerId,
  };
}

/**
 * Ellipse node with an inline label.
 * Returns [ellipse, text] when labeled, [ellipse] otherwise — spread into your elements array.
 *
 * @param {string} id
 * @param {number} x - top-left x
 * @param {number} y - top-left y
 * @param {number} w - width
 * @param {number} h - height
 * @param {string} label - text content (use \n for line breaks)
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, backgroundColor, fontSize
 */
function node(id, x, y, w, h, label, opts = {}) {
  const shape = base(id, 'ellipse', x, y, w, h, opts);
  const result = [shape];
  if (label) {
    const textId = `${id}__label`;
    shape.boundElements = [{ type: 'text', id: textId }];
    result.push(boundText(textId, id, label, x + w / 2, y + h / 2, {
      fontSize: opts.fontSize,
      maxWidth: w - 10,
    }));
  }
  return result;
}

/**
 * Rectangle node with an inline label.
 * Returns [rect, text] when labeled, [rect] otherwise — spread into your elements array.
 *
 * @param {string} id
 * @param {number} x - top-left x
 * @param {number} y - top-left y
 * @param {number} w - width
 * @param {number} h - height
 * @param {string} label - text content (use \n for line breaks)
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, backgroundColor, rounded (bool), fontSize, textAlign, verticalAlign
 */
function box(id, x, y, w, h, label, opts = {}) {
  const rounded = opts.rounded !== false;
  const shape = base(id, 'rectangle', x, y, w, h, { ...opts, roundness: rounded ? { type: 3 } : null });
  const result = [shape];
  if (label) {
    const textId = `${id}__label`;
    const pad = 10;
    shape.boundElements = [{ type: 'text', id: textId }];
    result.push(boundText(textId, id, label, x + w / 2, y + h / 2, {
      fontSize: opts.fontSize,
      textAlign: opts.textAlign,
      verticalAlign: opts.verticalAlign,
      maxWidth: w - 2 * pad,
      areaWidth: w - 2 * pad,
      areaHeight: h - 2 * pad,
    }));
  }
  return result;
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
 * Returns a single arrow element, or [arrow, text] when opts.label is set —
 * spread into your elements array (works either way; document() flattens).
 *
 * @param {string} id
 * @param {string} fromId - ID of source shape
 * @param {string} toId   - ID of target shape
 * @param {number[]} fromCenter - [x, y] center of source shape (for path direction)
 * @param {number[]} toCenter   - [x, y] center of target shape
 * @param {object} opts - strokeColor, strokeWidth, strokeStyle, startFocus, endFocus, gap, label, labelColor, labelFontSize
 *
 * When `opts.label` is set, a separate text element is created with
 * `containerId` pointing at the arrow, positioned at the arrow's midpoint —
 * this is what actually renders on the line in Obsidian's embedded preview.
 * Keep arrow labels terse (1–3 words); long labels crowd the line.
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

  const textId = `${id}__label`;
  el.boundElements = [{ type: 'text', id: textId }];
  const midX = fromCenter[0] + dx / 2;
  const midY = fromCenter[1] + dy / 2;
  const text = boundText(textId, id, opts.label, midX, midY, {
    fontSize: opts.labelFontSize || 11,
    strokeColor: opts.labelColor,
  });
  return [el, text];
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
  const seed = nextSeed();
  return {
    id,
    type: 'text',
    x,
    y,
    width: Math.max(approxW, 40),
    height: Math.max(approxH, fontSize + 4),
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
    verticalAlign: 'top',
    baseline: fontSize,
    containerId: null,
  };
}

/**
 * Ensure arrow bindings are bidirectional.
 *
 * An arrow names its endpoints via startBinding/endBinding, and each endpoint
 * shape must list the arrow in its own `boundElements`. The factories set the
 * forward links; this pass fills in the reverse ones. Idempotent.
 */
function linkBindings(flat) {
  const byId = new Map(flat.map((e) => [e.id, e]));
  const ensure = (host, ref) => {
    if (!host) return;
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

module.exports = { node, box, annotationBox, arrow, floatingLabel, document, linkBindings, boundText, ellipseEdge, rectEdge };
