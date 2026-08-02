# Microsite Editor

A single-file, no-install WYSIWYG editor for the HTML microsites we build for
customers. Open `editor.html` in any modern browser — there is nothing to
install, no server, no build step.

---

## For sellers — how to use it

1. **Open** — double-click `editor.html`. Drag your microsite onto the
   window, or click **Choose a file**. Both kinds of microsite work:
   - a single `.html` file, or
   - a `.zip` of a site folder (the page plus its images, styles and
     scripts). The editor opens the main page; when you save, you get a
     new `.zip` with your edits and every other file untouched.
2. **Edit** — click anything on the page:
   - **Text**: click it and start typing. A small toolbar appears for bold,
     colour, size, alignment, lists and links. Paste is always clean text;
     use `Ctrl+Shift+V` if you want to keep formatting.
   - **Buttons, links and tabs**: a single click behaves normally (so tabs
     still switch). To change the label, double-click it or use the
     **Edit text** button that appears.
   - **Images**: click one to replace it, resize it, round its corners or
     link it. Big photos are shrunk automatically (you'll be asked first).
   - **Sections**: use the breadcrumb chips in the right panel (or the
     ⤢ button) to select the whole section, then change its background,
     colours and spacing — or drag it with the dotted handle to reorder.
   - The dark toolbar on every selection has **move up/down, duplicate,
     hide and delete**. Everything is undoable with `Ctrl+Z`.
   - **Tables**: click a cell to edit its text, and use the Table panel to
     add or remove rows and columns.
   - **Add content** includes a **Video** block — paste a YouTube, Vimeo,
     Loom or .mp4 link.
   - **My library**: save any section for reuse ("our security blurb",
     "standard footer") and drop it into any microsite you open later.
   - **Find** (`Ctrl+F`) finds and replaces text across the whole page —
     including inside every tab and the browser-tab title. Great for
     swapping customer names.
   - **Tabs** in the top bar lists the page's tabs so you can jump to,
     rename or reorder them.
   - **Links** in the top bar shows every link on the page in one list so
     you can check and fix them all at once (dead `#` links are flagged).
   - **Pages** appears for zips with more than one page — switch between
     them; edits on every page go into the saved zip.
   - **Page** edits the page title, description and icon, shows a summary
     of everything you've changed (copy it for Claude or a teammate), and
     holds this session's saved versions.
3. **Preview** — the toggle in the top bar shows the page exactly as your
   customer will see it (with a phone-width option).
4. **Save** — click **Save** (or `Ctrl+S`). Before downloading, the editor
   runs a quick check for things that are easy to miss — leftover
   placeholder text, links that go nowhere, placeholder images — and shows
   you anything it finds (nothing blocks saving). You get a new file like
   `yourfile-v2.html` (or `yourfile-v2.zip`); the original is never touched.
   Send that file to the customer, host it, or hand it back to Claude for
   bigger changes.

If your browser crashes, reopen the same file — the editor keeps a draft and
offers to restore it. Press `?` any time for the shortcut cheat-sheet.

---

## For maintainers

### Architecture

Everything lives in `editor.html` (vanilla JS, no dependencies, no network).

- The microsite renders in a **same-origin iframe** (`srcdoc`), so its
  CSS/JS cannot touch the editor chrome and vice-versa. The runtime attaches
  at DOM-ready (not window `load`) so unreachable CDN assets never block
  editing.
- The **iframe's live DOM is the source of truth**. All editor UI (outlines,
  toolbars, drag indicators, panels) lives in the *parent* document,
  absolutely positioned over the iframe and re-synced every animation frame.
  Only three things ever exist inside the loaded document:
  1. one `<style id="msed-style">` element,
  2. `contenteditable` + `data-msed-ce` on the element currently being
     text-edited,
  3. `data-msed-hidden` markers for elements the user hid.
- **Undo/redo is command-based**, not snapshot-based: every edit records
  do/undo closures over real node references. Removed nodes keep their
  identity (and any listeners the microsite's scripts attached), so undoing
  a delete or a move never breaks tab/accordion scripts. Text edits are one
  command per editing session; while a session is active the browser's
  native undo handles keystrokes.
- **Interactive elements** (links, buttons, `role=tab`, `data-tab`, etc.):
  single click performs their normal behaviour and selects them; editing is
  entered via the "Edit text" affordance or double-click. External links are
  suppressed in Edit mode and opened in a new tab in Preview mode so the
  canvas can never navigate away (the iframe sandbox also blocks
  top-navigation).
- **Tab detection** (`detectTabs`) recognises three patterns: ARIA
  (`role=tablist/tab` + `aria-controls`), data attributes
  (`data-tab`/`data-target`), and navs of same-page `#links` whose targets
  include hidden panels. Reordering moves the button and its panel together
  and is disabled when buttons/panels don't share parents.
- **Zipped sites**: `.zip` inputs are unpacked entirely in memory by a
  vanilla zip reader (stored entries + deflate via the browser-native
  `DecompressionStream`). The active HTML page is rewritten so relative
  references — `src`/`href`/`srcset`, inline `style="url(…)"`, `<style>`
  blocks, and `url()`/`@import` inside `.css` files (resolved relative to
  each stylesheet, with circular-import protection) — point at blob URLs;
  the iframe renders those. On export the substitution is reversed
  string-for-string (blob URLs are globally unique), and Save rebuilds the
  zip (stored entries) with each edited page's updated HTML while all other
  files stay byte-for-byte identical.
- **Multi-page zips**: every `.html` entry is editable via the Pages menu
  (`switchZipPage`). Switching pages parks the current page's exported HTML
  in `App.zipPages`; Save and version snapshots merge all visited pages.
  Links between the zip's pages open the target page in Preview mode (and
  point at the Pages menu in Edit mode). Undo history is per page — it
  resets on switch, though intra-page undo remains command-based.
- **Pre-flight check** (`runPreflight`): runs on every save; flags likely
  placeholder text (lorem/TODO/`[Customer …]` plus this editor's own
  insert-block defaults), placeholder images, dead links (`#`/empty/
  `javascript:void(0)`), missing alt text, and hidden elements — each with
  a "Show me" jump that reveals the element (activating its tab if
  needed). Purely advisory; "Save anyway" is always available.
- **Change summary**: because undo is command-based, every command carries
  a human-readable label ("Edit heading — \"…\"", "Replace image — x.png").
  `changeSummary()` collapses the live undo stack into a plain-English list
  the seller can copy (from the Page settings modal or the post-save toast)
  and paste into Claude as context for further AI edits.
- **Snippet library**: stored in `localStorage` (`msed:snippets`, capped at
  30). Snippets are captured with editor markers stripped and (for zips)
  blob URLs reversed to relative paths; on insert, ids are removed and, in
  zip mode, asset references are re-resolved against the current zip.
- **Video blocks**: `parseVideoUrl` maps YouTube/Vimeo/Loom share links to
  their embed URLs, direct media files to `<video>`, and any other https
  URL to a plain iframe embed. In Edit mode all iframes/videos get
  `pointer-events:none` (via the injected style) so embeds are selectable
  rather than swallowing clicks; Preview restores full interactivity.

### How export cleanup works

`buildExportHTML()` clones `<html>`, removes `#msed-style`, strips
`contenteditable`/`spellcheck` where `data-msed-ce` marks them as ours,
converts `data-msed-hidden` to a real `display:none` (hiding *is* a user
edit), removes every remaining `data-msed-*` attribute, and prepends the
original doctype. Because nothing else is ever injected into the document,
a load→export cycle with no edits parses to a DOM identical to the input —
`test/roundtrip.test.mjs` asserts exactly this on all four fixtures.

### Testing

```
cd microsite-editor
npm i playwright-core        # once; browsers via CHROMIUM_PATH or /opt/pw-browsers
node test/roundtrip.test.mjs
```

See `TESTING.md` for the manual checklist. Fixtures in `fixtures/` cover a
plain one-pager, a JS-tabbed SPA page, a Bootstrap-from-CDN page, a page
with base64-embedded images, and `zip-site/` (a folder site the test zips
up — mixing stored and deflated entries — to exercise the .zip path
end-to-end).

### Known limitations

- Serialization is structural, not byte-faithful: attribute quoting and
  entity encoding are normalised by the browser. Content, structure,
  comments, scripts and styles are preserved.
- Pages that build their DOM at load time with scripts are edited in their
  *rendered* state; a warning toast appears when the rendered text is much
  larger than the static markup.
- Find & replace matches within single text nodes — a name split across
  nested `<span>`s won't match.
- Hidden elements become inline `display:none` on export; re-opening that
  exported file cannot distinguish them from elements the page hides itself
  (e.g. inactive tab panels), so they can't be un-hidden in a later session.
- Draft autosave uses `localStorage` and silently degrades (with one
  warning) for very large files that exceed the storage quota.
- Zipped sites: draft autosave is off in zip mode (assets only live in
  memory, so a draft restored in a fresh session couldn't rebuild the
  zip), and undo history resets when switching pages. Assets referenced
  only from JavaScript at runtime (e.g. `fetch('data.json')`) aren't
  rewritten and won't load in the canvas, though they're preserved in the
  saved zip. A replaced image is embedded as a data URI; the original asset
  file stays in the zip unused. Zip64 archives (>4 GB / >65k entries) are
  not supported.
- Tables with merged cells (colspan/rowspan) allow text editing only — the
  row/column tools are disabled there by design.
- Library snippets store asset references as relative paths; a snippet
  saved from one zip won't carry its images into a different site (images
  embedded as data URIs travel fine).
- The change summary reflects the current page's session (it resets when
  a zip page is switched or a file is reloaded).
