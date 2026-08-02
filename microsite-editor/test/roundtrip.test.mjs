/*
 * Round-trip cleanliness + core-editing test for editor.html.
 *
 * What it verifies (per TESTING.md):
 *  1. CLEAN ROUND-TRIP: load each fixture, make NO edits, export —
 *     the output must parse to a DOM identical to the input (the
 *     editor may not leak any artifact into the saved file).
 *  2. SELECTION LEAVES NO TRACE: click into text (which starts an
 *     editing session), press Escape, export — still identical.
 *  3. REAL EDITS SURVIVE, ARTIFACTS DON'T: type into a heading,
 *     export — the new text is present, and the export contains no
 *     msed markers / injected style / contenteditable.
 *  4. UNDO RESTORES THE ORIGINAL: after the edit, press Undo and
 *     export — identical to the input again.
 *  5. Versioned-filename suggestions increment correctly.
 *
 * Run:  node test/roundtrip.test.mjs
 * Needs: `npm i playwright-core` (or playwright) somewhere on
 * NODE_PATH, and a Chromium (auto-found, or set CHROMIUM_PATH).
 */
import { createRequire } from 'node:module';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright-core')); }
catch { ({ chromium } = require('playwright')); }

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const editorURL = pathToFileURL(path.join(root, 'editor.html')).href;
const fixtures = [
  'simple-onepager.html',
  'tabbed-spa.html',
  'cdn-framework.html',
  'base64-images.html',
];

function findChromium(){
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  for (const p of ['/opt/pw-browsers/chromium', '/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome']){
    if (existsSync(p)) return p;
  }
  return undefined; // let playwright resolve its own download
}

let passed = 0, failed = 0;
function check(name, ok, detail){
  if (ok){ passed++; console.log('  PASS  ' + name); }
  else { failed++; console.error('  FAIL  ' + name + (detail ? '\n        ' + detail : '')); }
}

// Parse both documents the same way and compare canonical serializations.
// (Attribute quoting/order normalizes identically on both sides, so any
// difference is a real structural/content difference.)
const NORMALIZE = `(s) => {
  const d = new DOMParser().parseFromString(s, 'text/html');
  return d.documentElement.outerHTML;
}`;

async function loadFixture(page, text, name){
  await page.evaluate(([t, n]) => window.__msedTest.load(t, n), [text, name]);
  await page.waitForFunction(() => window.__msedTest.ready(), null, { timeout: 10000 });
  // let the microsite's own scripts + editor post-load hooks settle
  await page.waitForTimeout(600);
}
async function exportHTML(page){
  return page.evaluate(() => window.__msedTest.export());
}
async function isSame(page, a, b){
  return page.evaluate(([na, nb, normSrc]) => {
    const norm = eval(normSrc);
    return norm(na) === norm(nb);
  }, [a, b, NORMALIZE]);
}
async function diffHint(page, a, b){
  return page.evaluate(([na, nb, normSrc]) => {
    const norm = eval(normSrc);
    const x = norm(na), y = norm(nb);
    let i = 0;
    while (i < x.length && x[i] === y[i]) i++;
    return 'first difference at char ' + i + ': …' +
      JSON.stringify(x.slice(Math.max(0, i - 40), i + 40)) + ' vs …' +
      JSON.stringify(y.slice(Math.max(0, i - 40), i + 40));
  }, [a, b, NORMALIZE]);
}

const browser = await chromium.launch({ executablePath: findChromium() });
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
page.on('pageerror', e => console.error('  [pageerror]', e.message));
await page.goto(editorURL);
// suppress the first-run tips modal so clicks reach the canvas
await page.evaluate(() => { try { localStorage.setItem('msed:tips', '1'); localStorage.clear && null; } catch (e) {} });
await page.evaluate(() => { try { localStorage.setItem('msed:tips', '1'); } catch (e) {} });

console.log('\n1) Clean round-trip (load -> no edits -> export) on all fixtures');
for (const f of fixtures){
  const text = readFileSync(path.join(root, 'fixtures', f), 'utf8');
  await loadFixture(page, text, f);
  const out = await exportHTML(page);
  const okDoctype = /^<!doctype html>/i.test(out.trim());
  const same = await isSame(page, text, out);
  check(f + ' doctype preserved', okDoctype);
  check(f + ' export identical to input', same, same ? '' : await diffHint(page, text, out));
  check(f + ' no editor artifacts', !/msed|contenteditable/i.test(out));
}

console.log('\n2) Selecting + entering/leaving text edit leaves no trace');
{
  const f = 'simple-onepager.html';
  const text = readFileSync(path.join(root, 'fixtures', f), 'utf8');
  await loadFixture(page, text, f);
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(200);
  await page.keyboard.press('Escape'); // end edit session
  await page.keyboard.press('Escape'); // deselect
  const out = await exportHTML(page);
  const same = await isSame(page, text, out);
  check('select/deselect export identical', same, same ? '' : await diffHint(page, text, out));
  check('no contenteditable left behind', !/contenteditable|data-msed/.test(out));
}

console.log('\n3) A real text edit survives export, artifacts do not');
{
  const f = 'simple-onepager.html';
  const text = readFileSync(path.join(root, 'fixtures', f), 'utf8');
  await loadFixture(page, text, f);
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(200);
  await page.keyboard.type(' ZEBRA');
  await page.keyboard.press('Escape');
  const out = await exportHTML(page);
  check('typed text present in export', out.includes('ZEBRA'));
  check('no editor artifacts after edit', !/msed|contenteditable/i.test(out));
  check('dirty flag set after edit', await page.evaluate(() => window.__msedTest.state.dirty));

  console.log('\n4) Undo restores the original exactly');
  await page.click('#btnUndo');
  await page.waitForTimeout(150);
  const out2 = await exportHTML(page);
  const same = await isSame(page, text, out2);
  check('post-undo export identical to input', same, same ? '' : await diffHint(page, text, out2));
}

console.log('\n5) Structural edit (delete section) + undo restores original');
{
  const f = 'cdn-framework.html';
  const text = readFileSync(path.join(root, 'fixtures', f), 'utf8');
  await loadFixture(page, text, f);
  await page.frameLocator('#canvas').locator('.alert').click();
  await page.waitForTimeout(200);
  await page.keyboard.press('Escape'); // end the text-edit session, keep selection
  const stillSelected = await page.evaluate(() => !!window.__msedTest.state.selected);
  check('element selected', stillSelected);
  await page.keyboard.press('Delete');
  await page.waitForTimeout(150);
  const outDel = await exportHTML(page);
  check('deleted element gone from export', !outDel.includes('Projected outcome'));
  await page.click('#btnUndo');
  await page.waitForTimeout(150);
  const out2 = await exportHTML(page);
  const same = await isSame(page, text, out2);
  check('post-undo export identical to input', same, same ? '' : await diffHint(page, text, out2));
}

console.log('\n6) Versioned filename suggestions');
{
  const cases = [
    ['acme.html', 'acme-v2.html'],
    ['acme-v2.html', 'acme-v3.html'],
    ['acme-v9.html', 'acme-v10.html'],
    ['launch plan.htm', 'launch plan-v2.htm'],
    ['site.zip', 'site-v2.zip'],
    ['site-v3.zip', 'site-v4.zip'],
  ];
  for (const [inp, want] of cases){
    const got = await page.evaluate(n => window.__msedTest.suggestFileName(n), inp);
    check(inp + ' -> ' + want, got === want, 'got ' + got);
  }
}

/* ---- minimal node-side zip build/parse (store + deflate-raw) ---- */
import zlib from 'node:zlib';
function nodeCrc32(buf){
  let t = nodeCrc32.t;
  if (!t){
    t = nodeCrc32.t = new Int32Array(256);
    for (let n = 0; n < 256; n++){
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c;
    }
  }
  let c = -1;
  for (const b of buf) c = t[(c ^ b) & 0xFF] ^ (c >>> 8);
  return (c ^ -1) >>> 0;
}
function nodeBuildZip(entries){ // [path, Buffer, method(0|8)][]
  const chunks = [], central = [];
  let offset = 0;
  for (const [path, raw, method] of entries){
    const data = method === 8 ? zlib.deflateRawSync(raw) : raw;
    const name = Buffer.from(path);
    const crc = nodeCrc32(raw);
    const lh = Buffer.alloc(30 + name.length);
    lh.writeUInt32LE(0x04034b50, 0); lh.writeUInt16LE(20, 4); lh.writeUInt16LE(0x0800, 6);
    lh.writeUInt16LE(method, 8); lh.writeUInt32LE(crc, 14);
    lh.writeUInt32LE(data.length, 18); lh.writeUInt32LE(raw.length, 22);
    lh.writeUInt16LE(name.length, 26);
    name.copy(lh, 30);
    chunks.push(lh, data);
    const ch = Buffer.alloc(46 + name.length);
    ch.writeUInt32LE(0x02014b50, 0); ch.writeUInt16LE(20, 4); ch.writeUInt16LE(20, 6);
    ch.writeUInt16LE(0x0800, 8); ch.writeUInt16LE(method, 10); ch.writeUInt32LE(crc, 16);
    ch.writeUInt32LE(data.length, 20); ch.writeUInt32LE(raw.length, 24);
    ch.writeUInt16LE(name.length, 28); ch.writeUInt32LE(offset, 42);
    name.copy(ch, 46);
    central.push(ch);
    offset += lh.length + data.length;
  }
  const cd = Buffer.concat(central);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(entries.length, 8); eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(cd.length, 12); eocd.writeUInt32LE(offset, 16);
  return Buffer.concat([...chunks, cd, eocd]);
}
function nodeParseZip(buf){ // stored entries only (what the editor writes)
  let eocd = -1;
  for (let i = buf.length - 22; i >= Math.max(0, buf.length - 65558); i--){
    if (buf.readUInt32LE(i) === 0x06054b50){ eocd = i; break; }
  }
  const count = buf.readUInt16LE(eocd + 10);
  let off = buf.readUInt32LE(eocd + 16);
  const files = new Map();
  for (let i = 0; i < count; i++){
    const method = buf.readUInt16LE(off + 10);
    const csize = buf.readUInt32LE(off + 20);
    const nameLen = buf.readUInt16LE(off + 28);
    const extraLen = buf.readUInt16LE(off + 30);
    const cmtLen = buf.readUInt16LE(off + 32);
    const lho = buf.readUInt32LE(off + 42);
    const name = buf.subarray(off + 46, off + 46 + nameLen).toString();
    off += 46 + nameLen + extraLen + cmtLen;
    const dataStart = lho + 30 + buf.readUInt16LE(lho + 26) + buf.readUInt16LE(lho + 28);
    if (method !== 0) throw new Error('expected stored entry');
    files.set(name, buf.subarray(dataStart, dataStart + csize));
  }
  return files;
}

console.log('\n7) Zip site: load, render, clean round-trip, edit, rebuild');
{
  const zdir = path.join(root, 'fixtures', 'zip-site');
  const htmlText = readFileSync(path.join(zdir, 'index.html'), 'utf8');
  const cssBuf = readFileSync(path.join(zdir, 'css/style.css'));
  const svgBuf = readFileSync(path.join(zdir, 'img/logo.svg'));
  const pngBuf = readFileSync(path.join(zdir, 'img/chart.png'));
  // mix stored and deflated entries to exercise both read paths
  const inputZip = nodeBuildZip([
    ['index.html', Buffer.from(htmlText), 0],
    ['css/style.css', cssBuf, 8],
    ['img/logo.svg', svgBuf, 8],
    ['img/chart.png', pngBuf, 0],
  ]);
  await page.evaluate(([b64, n]) => window.__msedTest.loadZip(b64, n), [inputZip.toString('base64'), 'wingtip-site.zip']);
  await page.waitForFunction(() => window.__msedTest.ready(), null, { timeout: 10000 });
  await page.waitForTimeout(600);

  check('zip mode active', await page.evaluate(() => window.__msedTest.state.zipMode));
  check('images resolve to blob: URLs', await page.evaluate(() =>
    window.__msedTest.state.idoc.querySelector('img[alt="Weekly sales chart"]').src.startsWith('blob:')));
  check('image bytes actually load', await page.evaluate(() => {
    const img = window.__msedTest.state.idoc.querySelector('img[alt="Weekly sales chart"]');
    return img.complete && img.naturalWidth === 96;
  }));
  check('stylesheet from zip applied', await page.evaluate(() => {
    const st = window.__msedTest.state;
    return st.iwin.getComputedStyle(st.idoc.querySelector('.masthead')).backgroundColor === 'rgb(124, 45, 146)';
  }));
  check('css-relative url(../img) resolved', await page.evaluate(() => {
    const st = window.__msedTest.state;
    return st.iwin.getComputedStyle(st.idoc.querySelector('.masthead')).backgroundImage.includes('blob:');
  }));

  // no-edit export: relative paths restored, DOM identical to input
  const out = await exportHTML(page);
  check('export restores relative paths (no blob:)', !out.includes('blob:'));
  const same = await isSame(page, htmlText, out);
  check('zip html export identical to input', same, same ? '' : await diffHint(page, htmlText, out));

  // no-edit zip rebuild: every asset byte-for-byte identical
  const rebuilt = nodeParseZip(Buffer.from(await page.evaluate(() => window.__msedTest.exportZipB64()), 'base64'));
  check('rebuilt zip has all entries', rebuilt.size === 4);
  check('css bytes untouched', rebuilt.get('css/style.css') && Buffer.compare(rebuilt.get('css/style.css'), cssBuf) === 0);
  check('png bytes untouched', rebuilt.get('img/chart.png') && Buffer.compare(rebuilt.get('img/chart.png'), pngBuf) === 0);
  check('svg bytes untouched', rebuilt.get('img/logo.svg') && Buffer.compare(rebuilt.get('img/logo.svg'), svgBuf) === 0);

  // real edit -> rebuilt zip carries it
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(200);
  await page.keyboard.type(' GIRAFFE');
  await page.keyboard.press('Escape');
  const rebuilt2 = nodeParseZip(Buffer.from(await page.evaluate(() => window.__msedTest.exportZipB64()), 'base64'));
  const editedHtml = rebuilt2.get('index.html').toString();
  check('edit present in rebuilt zip html', editedHtml.includes('GIRAFFE'));
  check('no artifacts in rebuilt zip html', !/msed|contenteditable|blob:/i.test(editedHtml));
  await page.click('#btnUndo');
  await page.waitForTimeout(150);
  const out3 = await exportHTML(page);
  const same3 = await isSame(page, htmlText, out3);
  check('zip post-undo export identical to input', same3, same3 ? '' : await diffHint(page, htmlText, out3));
}

console.log('\n8) Pre-flight check');
{
  const clean = readFileSync(path.join(root, 'fixtures', 'simple-onepager.html'), 'utf8');
  await loadFixture(page, clean, 'clean.html');
  const cleanIssues = await page.evaluate(() => window.__msedTest.preflight());
  check('clean fixture has no issues', cleanIssues.length === 0, JSON.stringify(cleanIssues));

  const messy = `<!DOCTYPE html><html><head><title>t</title></head><body>
    <h1>Welcome [Customer Name]</h1>
    <p>Lorem ipsum dolor sit amet, placeholder copy.</p>
    <a href="#">Book a demo</a>
    <img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=">
  </body></html>`;
  await loadFixture(page, messy, 'messy.html');
  const issues = await page.evaluate(() => window.__msedTest.preflight());
  check('placeholder text flagged', issues.some(t => /Customer Name|Lorem/i.test(t)));
  check('dead link flagged', issues.some(t => /doesn’t go anywhere/.test(t)));
  check('missing alt flagged', issues.some(t => /no description/.test(t)));
  await page.click('#btnSave');
  await page.waitForTimeout(200);
  check('save shows pre-flight modal instead of downloading', await page.evaluate(() =>
    !document.querySelector('#modalRoot').hidden &&
    document.querySelector('#modalRoot .modal-h').textContent.includes('quick look')));
  await page.click('#modalRoot .modal-f .btn'); // "Keep editing"
  await page.waitForTimeout(100);
}

console.log('\n9) Link audit panel');
{
  const text = readFileSync(path.join(root, 'fixtures', 'simple-onepager.html'), 'utf8');
  await loadFixture(page, text, 'links.html');
  await page.click('#btnLinks');
  await page.waitForTimeout(200);
  check('links modal lists the CTA link', await page.evaluate(() =>
    !document.querySelector('#modalRoot').hidden &&
    !!document.querySelector('#modalRoot input[value*="example.com/demo"]')));
  await page.evaluate(() => {
    const inp = document.querySelector('#modalRoot input[value*="example.com/demo"]');
    inp.value = 'https://example.com/new-demo';
    inp.dispatchEvent(new Event('change'));
  });
  await page.click('#modalRoot .btn-primary');
  const out = await exportHTML(page);
  check('link edited from the audit panel', out.includes('https://example.com/new-demo'));
  await page.click('#btnUndo');
  await page.waitForTimeout(120);
  const out2 = await exportHTML(page);
  const same = await isSame(page, text, out2);
  check('link edit undone cleanly', same, same ? '' : await diffHint(page, text, out2));
}

console.log('\n10) Table structure editing');
{
  const text = readFileSync(path.join(root, 'fixtures', 'cdn-framework.html'), 'utf8');
  await loadFixture(page, text, 'table.html');
  await page.frameLocator('#canvas').locator('tbody td').first().click();
  await page.waitForTimeout(200);
  await page.keyboard.press('Escape'); // end text edit, keep selection
  await page.waitForTimeout(120);
  const rowsBefore = (await exportHTML(page)).match(/<tr>/g).length;
  await page.locator('#spBody button', { hasText: '+ Row below' }).click();
  await page.waitForTimeout(150);
  const rowsAfter = (await exportHTML(page)).match(/<tr>/g).length;
  check('row added below', rowsAfter === rowsBefore + 1, rowsBefore + ' -> ' + rowsAfter);
  await page.locator('#spBody button', { hasText: '+ Column right' }).click();
  await page.waitForTimeout(150);
  const out = await exportHTML(page);
  check('column added (header row too)', (out.match(/<th[\s>]/g) || []).length === 4);
  await page.click('#btnUndo');
  await page.click('#btnUndo');
  await page.waitForTimeout(150);
  const out2 = await exportHTML(page);
  const same = await isSame(page, text, out2);
  check('table ops fully undone', same, same ? '' : await diffHint(page, text, out2));
}

console.log('\n11) Snippet library');
{
  await page.evaluate(() => localStorage.removeItem('msed:snippets'));
  const text = readFileSync(path.join(root, 'fixtures', 'cdn-framework.html'), 'utf8');
  await loadFixture(page, text, 'snips.html');
  await page.frameLocator('#canvas').locator('.alert').click();
  await page.waitForTimeout(200);
  await page.keyboard.press('Escape');
  await page.waitForTimeout(120);
  await page.locator('#spBody button', { hasText: 'for reuse' }).click();
  await page.waitForTimeout(150);
  await page.click('#modalRoot .btn-primary'); // Save with default name
  await page.waitForTimeout(150);
  check('snippet stored', await page.evaluate(() => JSON.parse(localStorage.getItem('msed:snippets') || '[]').length === 1));
  // insert it below another element
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(150);
  await page.keyboard.press('Escape');
  await page.locator('#spBody .pbtn[title^="Insert"]').first().click();
  await page.waitForTimeout(150);
  const out = await exportHTML(page);
  check('snippet inserted', (out.match(/Projected outcome/g) || []).length === 2);
  check('no editor artifacts in snippet', !/data-msed|contenteditable/.test(out));
  await page.click('#btnUndo');
  await page.waitForTimeout(120);
  const out2 = await exportHTML(page);
  const same = await isSame(page, text, out2);
  check('snippet insert undone cleanly', same, same ? '' : await diffHint(page, text, out2));
  await page.evaluate(() => localStorage.removeItem('msed:snippets'));
}

console.log('\n12) Video embeds');
{
  const cases = [
    ['https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'https://www.youtube.com/embed/dQw4w9WgXcQ'],
    ['https://youtu.be/dQw4w9WgXcQ', 'https://www.youtube.com/embed/dQw4w9WgXcQ'],
    ['https://vimeo.com/123456789', 'https://player.vimeo.com/video/123456789'],
    ['https://www.loom.com/share/abc123def456', 'https://www.loom.com/embed/abc123def456'],
    ['https://cdn.example.com/demo.mp4', 'https://cdn.example.com/demo.mp4'],
  ];
  for (const [inp, want] of cases){
    const got = await page.evaluate(u => window.__msedTest.parseVideoUrl(u), inp);
    check('parse ' + inp.slice(8, 40), got && got.src === want, 'got ' + JSON.stringify(got));
  }
  check('garbage rejected', await page.evaluate(() => window.__msedTest.parseVideoUrl('not a url') === null));
  const text = readFileSync(path.join(root, 'fixtures', 'simple-onepager.html'), 'utf8');
  await loadFixture(page, text, 'video.html');
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(150);
  await page.keyboard.press('Escape');
  const inserted = await page.evaluate(() => window.__msedTest.insertVideo('https://youtu.be/dQw4w9WgXcQ'));
  check('video block inserted', inserted);
  const out = await exportHTML(page);
  check('embed iframe in export', out.includes('https://www.youtube.com/embed/dQw4w9WgXcQ') && out.includes('allowfullscreen'));
  await page.click('#btnUndo');
  await page.waitForTimeout(120);
  const out2 = await exportHTML(page);
  const same = await isSame(page, text, out2);
  check('video insert undone cleanly', same, same ? '' : await diffHint(page, text, out2));
}

console.log('\n13) Multi-page zip editing');
{
  const zdir = path.join(root, 'fixtures', 'zip-site');
  const htmlText = readFileSync(path.join(zdir, 'index.html'), 'utf8');
  const cssBuf = readFileSync(path.join(zdir, 'css/style.css'));
  const svgBuf = readFileSync(path.join(zdir, 'img/logo.svg'));
  const pngBuf = readFileSync(path.join(zdir, 'img/chart.png'));
  const aboutText = '<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><title>About</title><link rel="stylesheet" href="css/style.css"></head><body><h1>About Wingtip</h1><p>Founded in 1998.</p><a href="index.html">Back home</a></body></html>';
  const inputZip = nodeBuildZip([
    ['index.html', Buffer.from(htmlText), 0],
    ['about.html', Buffer.from(aboutText), 0],
    ['css/style.css', cssBuf, 8],
    ['img/logo.svg', svgBuf, 0],
    ['img/chart.png', pngBuf, 0],
  ]);
  await page.evaluate(([b64, n]) => window.__msedTest.loadZip(b64, n), [inputZip.toString('base64'), 'multi-site.zip']);
  await page.waitForFunction(() => window.__msedTest.ready(), null, { timeout: 10000 });
  await page.waitForTimeout(500);
  check('Pages button visible', await page.evaluate(() => !document.querySelector('#btnPages').hidden));
  // switch to about.html, edit it
  await page.evaluate(() => window.__msedTest.switchZipPage('about.html'));
  await page.waitForFunction(() => window.__msedTest.ready() && window.__msedTest.state.zip.htmlPath === 'about.html');
  await page.waitForTimeout(400);
  check('about page stylesheet applied', await page.evaluate(() => {
    const st = window.__msedTest.state;
    return st.iwin.getComputedStyle(st.idoc.body).backgroundColor === 'rgb(248, 250, 252)';
  }));
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(150);
  await page.keyboard.type(' MOOSE');
  await page.keyboard.press('Escape');
  // switch back to index — the about edit must survive
  await page.evaluate(() => window.__msedTest.switchZipPage('index.html'));
  await page.waitForFunction(() => window.__msedTest.ready() && window.__msedTest.state.zip.htmlPath === 'index.html');
  await page.waitForTimeout(400);
  check('dirty flag survives page switch', await page.evaluate(() => window.__msedTest.state.dirty));
  const rebuilt = nodeParseZip(Buffer.from(await page.evaluate(() => window.__msedTest.exportZipB64()), 'base64'));
  check('about edit lands in rebuilt zip', rebuilt.get('about.html').toString().includes('MOOSE'));
  check('about html has no blob/artifacts', !/blob:|data-msed|contenteditable/.test(rebuilt.get('about.html').toString()));
  const idxOut = rebuilt.get('index.html').toString();
  const sameIdx = await isSame(page, htmlText, idxOut);
  check('untouched index page identical', sameIdx, sameIdx ? '' : await diffHint(page, htmlText, idxOut));
  check('assets still byte-identical', Buffer.compare(rebuilt.get('css/style.css'), cssBuf) === 0 && Buffer.compare(rebuilt.get('img/chart.png'), pngBuf) === 0);
}

console.log('\n14) Change summary');
{
  const text = readFileSync(path.join(root, 'fixtures', 'simple-onepager.html'), 'utf8');
  await loadFixture(page, text, 'summary.html');
  await page.frameLocator('#canvas').locator('h1').click();
  await page.waitForTimeout(150);
  await page.keyboard.type(' EDIT1');
  await page.keyboard.press('Escape');
  await page.frameLocator('#canvas').locator('.quote').click();
  await page.waitForTimeout(150);
  await page.keyboard.press('Escape');
  await page.keyboard.press('Delete');
  await page.waitForTimeout(120);
  const lines = await page.evaluate(() => window.__msedTest.changeSummary());
  check('summary has both edits', lines.length === 2, JSON.stringify(lines));
  check('summary lines are descriptive', lines.some(l => /^Edit heading — “/.test(l)) && lines.some(l => /^Delete \w+ — “/.test(l)), JSON.stringify(lines));
}

await browser.close();
console.log('\n' + passed + ' passed, ' + failed + ' failed');
process.exit(failed ? 1 : 0);
