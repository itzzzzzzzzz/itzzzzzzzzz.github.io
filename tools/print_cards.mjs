// Prints karten/karten.html to karten/Wyoming Karteikarten.pdf with Edge, and says how much room each card has left
// below its text (in mm; under 4 mm is tight): node tools/print_cards.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const dir = path.resolve(here, '..', 'karten');
const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const port = 9800 + Math.floor(Math.random() * 150);
const udd = path.join(os.tmpdir(), 'edge-print-' + port);
const proc = spawn(edge, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${udd}`, '--no-first-run',
  '--disable-extensions', '--disable-sync', '--hide-scrollbars', '--mute-audio', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
for (let i = 0; i < 60 && !ws; i++) {
  try { const j = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const t = j.find(x => x.type === 'page'); if (t) ws = new WebSocket(t.webSocketDebuggerUrl); } catch { }
  if (!ws) await sleep(250);
}
await new Promise(r => ws.addEventListener('open', r));
let id = 0; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async expr => (await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true })).result?.result?.value;

await send('Page.enable');
await send('Emulation.setEmulatedMedia', { media: 'print' });
await send('Page.navigate', { url: pathToFileURL(path.join(dir, 'karten.html')).href });
for (let i = 0; i < 50 && !(await ev(`document.readyState === 'complete'`)); i++) await sleep(100);
await ev('document.fonts.ready.then(() => true)');
console.log(JSON.stringify(await ev(`(function () { var r = []; document.querySelectorAll('.card').forEach(function (c) {
  var p = c.querySelector('p').getBoundingClientRect(), b = c.getBoundingClientRect(); r.push(Math.round((b.bottom - p.bottom) / 3.78 * 10) / 10); });
  return { cards: r.length, sheets: document.querySelectorAll('.sheet').length, roomBelowMm: r, tight: r.filter(function (x) { return x < 4; }).length }; })()`)));
const r = await send('Page.printToPDF', { printBackground: true, preferCSSPageSize: true, marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0, scale: 1, displayHeaderFooter: false });
fs.writeFileSync(path.join(dir, 'Wyoming Karteikarten.pdf'), Buffer.from(r.result.data, 'base64'));
console.log('written', path.join(dir, 'Wyoming Karteikarten.pdf'));
ws.close(); proc.kill(); process.exit(0);
