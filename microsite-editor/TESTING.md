# Testing checklist

## Automated round-trip cleanliness test

```
cd microsite-editor
npm i playwright-core     # once (uses the system Chromium; set CHROMIUM_PATH if needed)
node test/roundtrip.test.mjs
```

The suite must end `0 failed`. It verifies, for **all four fixtures**:

- [ ] Load → no edits → export parses to a DOM **identical** to the input
      (no editor artifacts of any kind, doctype preserved).
- [ ] Selecting text / entering and leaving an edit session leaves no trace.
- [ ] A real text edit survives export; `data-msed-*`, `#msed-style` and
      `contenteditable` never appear in exports.
- [ ] Undo after a text edit or a section delete restores a byte-identical
      export.
- [ ] Versioned filename suggestion increments (`x.html` → `x-v2.html` →
      `x-v3.html`, and `x.zip` → `x-v2.zip`).
- [ ] **Zip sites** (`fixtures/zip-site/`, zipped by the test with a mix of
      stored and deflated entries): renders with its stylesheet and images
      (blob URLs), a no-edit export restores the original relative paths
      and parses to an identical DOM, the rebuilt zip keeps every asset
      byte-for-byte identical, an edit lands in the rebuilt zip's HTML with
      no artifacts, and undo restores an identical export.
- [ ] **Pre-flight**: clean fixtures yield zero issues; placeholder text,
      dead links and missing alt are flagged; Save shows the check modal
      instead of downloading when issues exist.
- [ ] **Link audit**: modal lists links, edits apply and undo cleanly.
- [ ] **Tables**: add row/column below/right of the selected cell; both
      operations undo to an identical export.
- [ ] **Snippets**: save a section, insert it elsewhere, no artifacts,
      undo restores an identical export.
- [ ] **Video**: YouTube/Vimeo/Loom/.mp4 URLs parse to the right embed;
      insertion lands in the export and undoes cleanly.
- [ ] **Multi-page zip**: Pages button appears, switching pages keeps
      edits and the dirty flag, the rebuilt zip carries the edited page
      while untouched pages and assets stay identical.
- [ ] **Change summary**: descriptive per-edit lines are produced.

## Manual verification (per release)

Load each fixture in `fixtures/` and run through:

### Core loop (every fixture)
- [ ] File opens by drag-drop **and** by the file picker (.html and .zip).
- [ ] Zip a copy of `fixtures/zip-site/` and open it: page renders with its
      images and styles; Save downloads `…-v2.zip`; unzip it and open
      `index.html` directly in a browser — it looks identical.
- [ ] Page renders identically to opening the fixture directly in a browser.
- [ ] Save downloads `<name>-v2.html`; the saved file opens standalone and
      looks identical (fixture 3 needs network for its CDN CSS).
- [ ] Re-open the saved file in the editor and edit again (round-trip).

### Text editing (fixture 1: simple-onepager)
- [ ] Click a paragraph → caret appears where clicked; toolbar shows.
- [ ] Bold/italic/underline/strike, text colour, highlight, size presets,
      bigger/smaller, alignment, bullet + numbered lists all apply and undo.
- [ ] Add a link via the toolbar; edit it; remove it; undo each step.
- [ ] Paste from Word/Docs inserts plain text; `Ctrl+Shift+V` keeps
      formatting.
- [ ] Esc commits; `Ctrl+Z` after committing reverts the whole edit.

### Structure (fixtures 1 & 3)
- [ ] Hover shows friendly labels ("Heading", "Section"…) — never CSS soup.
- [ ] Breadcrumb chips select ancestors ("select the whole section").
- [ ] Move up/down, duplicate, hide (ghosted in Edit, gone in Preview),
      delete (undoable, toast offers Undo).
- [ ] Drag handle reorders sections with a drop indicator; Esc cancels a
      drag; dragging the only child shows a friendly message.

### Images (fixtures 1 & 4)
- [ ] Replace image embeds the new image (saved file works offline).
- [ ] A large photo triggers the shrink offer; both choices work.
- [ ] Alt text, size presets, corner handles drag-resize, alignment,
      corners, link-wrap — all undoable.
- [ ] Section background photo can be added, replaced, removed.

### Tabs (fixture 2: tabbed-spa)
- [ ] Tabs switch normally on single click in Edit mode.
- [ ] Tab button label edits via double-click or "Edit text" without
      firing navigation mid-edit.
- [ ] Top-bar **Tabs** lists all four tabs; jump/rename/reorder work, and
      reorder moves button + panel together (check in Preview).
- [ ] Find & replace finds text inside non-active tabs and switches to
      them when stepping through matches.

### New-feature spot checks
- [ ] Save with a leftover "[Customer Name]" on the page → pre-flight modal
      appears; "Show me" jumps to the element; "Save anyway" downloads.
- [ ] Links (top bar) lists every link; editing a URL there changes the
      saved file; `#` links show a warning marker.
- [ ] Click a cell in fixture 3's table → Table panel adds/removes rows and
      columns; a Bootstrap-styled table keeps its look.
- [ ] Save a section to My library, open a different fixture, insert it.
- [ ] Add content → Video with a YouTube link: selectable box in Edit,
      playable in Preview and in the saved file.
- [ ] Zip with two pages: Pages button switches; in Preview, clicking an
      in-zip link opens that page in the editor.
- [ ] Page settings shows "Changes this session"; Copy puts a readable
      list on the clipboard.

### Robustness
- [ ] Fixture 3 (Bootstrap CDN) loads and edits with no network.
- [ ] Preview mode is fully interactive: tabs, accordions, hover styles;
      external links open in a new browser tab, never navigate the canvas.
- [ ] Mobile preview width toggle.
- [ ] Unsaved-changes dot + browser warning on close; draft restore offer
      after reload; drafts cleared on save.
- [ ] First-run tips show once; `?` opens the cheat-sheet.
