#!/usr/bin/env node
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.FLOW_PORT || '4173', 10);
const PROJECT_ROOT = process.env.FLOW_PROJECT_ROOT || process.cwd();
const DIAGRAM_NAME = process.env.FLOW_DIAGRAM || 'diagram';
const DIAGRAMS_DIR = join(PROJECT_ROOT, '.claude', 'diagrams');
const DIAGRAM_PATH = join(DIAGRAMS_DIR, `${DIAGRAM_NAME}.json`);
const PID_PATH = join(DIAGRAMS_DIR, '.server.pid');

await mkdir(DIAGRAMS_DIR, { recursive: true });

if (!existsSync(DIAGRAM_PATH)) {
  await writeFile(DIAGRAM_PATH, JSON.stringify({ nodes: [], edges: [] }, null, 2));
}

const clients = new Set();
let lastMtime = 0;

async function readGraph() {
  const raw = await readFile(DIAGRAM_PATH, 'utf8');
  return raw;
}

async function writeGraph(body) {
  const parsed = JSON.parse(body);
  if (!Array.isArray(parsed.nodes) || !Array.isArray(parsed.edges)) {
    throw new Error('Graph must have nodes[] and edges[]');
  }
  await writeFile(DIAGRAM_PATH, JSON.stringify(parsed, null, 2));
}

async function readBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8');
}

function sse(res) {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  res.write(`: connected\n\n`);
  clients.add(res);
  req => res.on?.('close', () => clients.delete(res));
}

function broadcast(event, data) {
  const payload = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const c of clients) c.write(payload);
}

// Poll file mtime so external edits (LLM writes) push to browser.
import { stat, watch } from 'node:fs/promises';
(async () => {
  try {
    const watcher = watch(DIAGRAM_PATH);
    for await (const _ of watcher) broadcast('graph-updated', { file: DIAGRAM_PATH });
  } catch {}
})();

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);

    if (req.method === 'GET' && url.pathname === '/') {
      const html = await readFile(join(__dirname, 'index.html'), 'utf8');
      res.writeHead(200, { 'Content-Type': 'text/html' });
      return res.end(html);
    }

    if (req.method === 'GET' && url.pathname === '/graph') {
      const body = await readGraph();
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(body);
    }

    if (req.method === 'PUT' && url.pathname === '/graph') {
      const body = await readBody(req);
      await writeGraph(body);
      res.writeHead(204);
      return res.end();
    }

    if (req.method === 'GET' && url.pathname === '/events') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
      });
      res.write(`: connected\n\n`);
      clients.add(res);
      req.on('close', () => clients.delete(res));
      return;
    }

    if (req.method === 'GET' && url.pathname === '/meta') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ diagram: DIAGRAM_NAME, path: DIAGRAM_PATH }));
    }

    if (req.method === 'POST' && url.pathname === '/shutdown') {
      res.writeHead(204);
      res.end();
      setTimeout(() => process.exit(0), 50);
      return;
    }

    res.writeHead(404);
    res.end('not found');
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end(String(err?.stack || err));
  }
});

server.listen(PORT, '127.0.0.1', async () => {
  await writeFile(PID_PATH, String(process.pid));
  console.log(`flow server pid=${process.pid} port=${PORT} diagram=${DIAGRAM_PATH}`);
});

process.on('SIGTERM', () => process.exit(0));
process.on('SIGINT', () => process.exit(0));
