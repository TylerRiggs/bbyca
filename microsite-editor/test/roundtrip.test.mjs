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
  ];
  for (const [inp, want] of cases){
    const got = await page.evaluate(n => window.__msedTest.suggestFileName(n), inp);
    check(inp + ' -> ' + want, got === want, 'got ' + got);
  }
}

await browser.close();
console.log('\n' + passed + ' passed, ' + failed + ' failed');
process.exit(failed ? 1 : 0);
