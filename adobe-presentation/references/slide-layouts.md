# Adobe PPTX Slide Layouts — Full Specification

Source: `templates/adobe-deck-template.pptx` (Adobe Presentation Style Guide Revision 1.7, Jan 2026) — 56 official slide layouts inspected directly from the XML.

This file documents every layout, when to use it, and the exact placeholder positions/sizes. Reference these when constructing the JSON content spec for `scripts/build_deck.py`.

---

## Slide grid (every layout)

```
0.00" ─────────────────────────────────────────────────── 13.33"
│ │                                                              │
│r│   Title area:   x=0.67  y=0.29  w=12.00  h=1.03              │
│e│                                                              │
│d│   Content area: x=0.67  y=1.46  w=12.00  h=5.46              │
│ │                                                              │
│0│   Footer:       x=10.80 y=7.20  Copyright text (6pt #191919) │
│.│                 x=12.95 y=7.20  Slide number  (6pt #191919)  │
│1│                                                              │
│4│ ────────────────────────────────────────────────────────── 7.50"
```

Red thread: `x=0, y=0, w=0.14", h=7.5", fill=#EB1000`. Always present unless background is full red.

---

## Cover slides (title slides)

### Layout 1 — Title Slide (Red default)
**When:** Opening of any external pitch, customer-facing deck, marquee internal kickoff.
- Background: `#EB1000` full bleed (no red thread shape needed)
- Title: white, **Adobe Clean Display Black, 77pt**, at `x=0.67, y=1.23, w=12.00, h=2.61`
- Subtitle/speaker/date: white, **Adobe Clean Regular, 24pt**, at `x=0.67, y=3.94, w=12.00, h=1.81`
- Wordmark: optional, but if used: white, lower-left
- No footer on cover

### Layout 2 — Title Slide White
**When:** Lower-energy openings, technical or analytical content
- Background: white, red thread present
- Title: black, Adobe Clean Display Black, 77pt, same position as Layout 1
- Subtitle: black or `#5F5F5F`, 24pt

### Layout 3 — Title Slide Dark
**When:** Premium/launch/event aesthetic
- Background: black, red thread present
- Title: white, Adobe Clean Display Black, 77pt
- Subtitle: white, 24pt

### Layout 4 — Title Slide with Image (Light)
- Background: white, red thread
- Title: black, **Adobe Clean Display Black, 54pt** (smaller to share space with image)
- Image: right portion (typically right ½)

### Layout 5 — Title Slide with Image (Dark)
- Background: black, red thread, white title, 54pt

---

## Section dividers

### Layout 6 — Section Divider (Light)
**When:** Major section break in a long deck
- Background: white, red thread
- Section title: black, **Adobe Clean Display Black, 72pt**, at `x=0.67, y=2.73, w=12.00, h=2.04` (vertically centered)

### Layout 7 — Section Divider (Dark)
- Background: black, red thread, white title, 72pt

### Layout 52 — Section Divider Alt
- Light bg, red thread, alternative composition (e.g. left-justified small title with eyebrow label)

### Layout 53 — Section Divider Dark Alt
- Dark bg counterpart

---

## Content slides — single column

### Layout 55 — Title and Content (Light Airy) — DEFAULT for body slides
**When:** Standard content slide for the majority of a deck
- Background: white, red thread
- Title: black, **Adobe Clean Display Black or Black, 32pt**, at top placeholder (0.67, 0.29, 12.00, 1.03)
- Content: bullets at 18 / 14 / 12 pt (L1/L2/L3), max 3 levels, max 7 bullets per slide
- Footer: 6pt #191919

### Layout 56 — Title and Content (Dark Airy)
- Black bg, red thread, white text — same structure

### Layout 9 — White Bottom Graphic
- Light bg + bottom graphic accent line. Body text 20pt, captions 11–12pt

### Layout 29 — Black Bottom Graphic
- Dark counterpart

---

## Content slides — image with content

### Layout 10 — Title + Content + ½ Image
**When:** Side-by-side comparison, screenshot + explanation
- Title spans full width
- Content (left half): bullets at 14–16pt
- Image (right half)

### Layout 11 — Title + Content + ⅓ Image
- More content room (⅔), smaller image (⅓)

### Layouts 30 / 31 — Dark variants of 10 / 11

### Layout 48 — Full Image with Thread
**When:** Hero image, end of section
- Full-bleed image
- Red thread preserved
- No title or minimal eyebrow text overlaid

---

## Multi-column layouts

### Light column layouts (white bg)
| Layout | Columns | Use |
|---|---|---|
| 12 | 2 columns content | A vs B comparison, before/after |
| 13 | 3 columns content | 3-pillar overview, feature triad |
| 18 | 4 columns content | Capabilities matrix |
| 14 | 5 columns content | Step-by-step process |
| 15 | 2 cols, image + text | Two products / two case studies |
| 16 | 3 cols, image + text | Three products / three personas |
| 17 | 4 cols, image + text | Product family |
| 19 | 5 cols, image + text | Product full lineup |
| 20 | 2 cols, photo + title | People intro (2 speakers) |
| 22 | 3 cols, photo + title | Team intro (3) |
| 21 | 4 cols, photo + title | Team intro (4) |
| 23 | 5 cols, photo + title | Team intro (5) |

### Dark counterparts: 32, 33, 34, 35 (no-image) / 36–39 (with image) / 40–43 (photo+title)

### Column type sizes (extracted from the layouts)
- **Column header (bold):** 16pt Adobe Clean Bold
- **Body inside columns:** 11–14pt Adobe Clean Regular (smaller as columns get narrower)
- **5-column body:** 10–11pt
- **Maintain consistent type size across columns on a single slide** — never mix 11pt and 14pt in adjacent columns.

---

## Specialty layouts

### Layout 8 — Large Quote (Light)
- Pull-quote, **Adobe Clean Display Black, 54pt** centered or left
- Attribution below: 16pt Regular
- Note: SemiLight allowed for Experience Cloud only

### Layout 28 — Large Quote (Dark)
- Black bg counterpart

### Layout 54 — Agenda
**When:** Front of any deck > 8 slides
- Title: "Agenda" at 32pt
- Table placeholder at `x=0.67, y=1.72, w=12.00, h=4.93`
- Columns: typically Speaker | Section | Time
- Header row: bold 14pt, body 12pt
- Alternating row shading: white / `#F5F5F5`

### Grid layouts (gallery patterns)
| Layout | Grid | Use |
|---|---|---|
| 24 | 1×1 | Hero card |
| 25 | 2×2 | 4-card feature grid |
| 26 | 3×2 | 6-card product/value lineup |
| 27 | 8×4 | Logo wall (32 cells) |
| 44–47 | Dark variants of the above |

## Structured-visual layouts (builder-native)

These layouts don't exist in the 56-layout master — they are drawn by
`build_deck.py` from brand tokens. They exist because the master's text
placeholders flatten structured content into bullets, which reads as generic.
**Prefer these over `content` whenever the content is structured** (pricing,
metrics, options, sequences). All positions respect the standard grid: title
at 0.29", content from 1.46" (1.58" with a kicker), clear of the 7.20" footer.

Every layout below accepts:
- `kicker` — 14pt Adobe Clean Bold, `#EB1000`, eyebrow line under the title
- `notice` — bottom strip: `#F5F5F5` band, 0.07" semantic accent bar
  (default orange `#FFA213`), 11pt bold black text. For deadlines/caveats.

### `table` (alias `pricing-table`)
The pricing/plan/data workhorse.
- Header band: black `#000000`, 0.52" tall, white 13pt Adobe Clean Bold
- Body rows: alternating `#F5F5F5` / white, 13pt (11pt when > 8 rows),
  first column bold, numeric columns auto right-aligned
  (`col_align`/`col_widths` override)
- `total_row`: Adobe red `#EB1000` band, white 14pt bold
- `highlight`: callout box under the table — `#F5F5F5`, 0.07" red accent bar,
  gray 12pt label, 30pt Adobe Clean Black hero value, gray note on the right
- Spec keys: `columns`, `rows`, `total_row?`, `col_widths?`, `col_align?`,
  `highlight? {label, value, note}`, `kicker?`, `notice?`

### `stat-row` (alias `stats`)
2–4 KPI cards for the numbers that matter.
- Card: `#F5F5F5`, 0.08" accent top bar (default red; extended-palette name or
  hex per stat), 40pt Adobe Clean Black value (32pt at 4 cards),
  14pt bold label, 11pt gray note
- Spec: `stats: [{value, label, note?, accent?}]`

### `cards`
2–6 feature/pillar/product cards, ≤3 per row (4 → 2×2, 5–6 → 3×2).
- Card: `#F5F5F5`, 0.07" accent top bar, 15pt bold header,
  11.5pt gray body or 11pt bullets
- Spec: `cards: [{header, body | bullets, accent?}]`

### `comparison`
Two boxed panels for before/after, option A/B, us/them.
- Panel: `#F5F5F5` box, 0.52" header band with white 15pt bold text
- Left band defaults `#191919`, right band `#EB1000` — put the
  recommended/"after" side on the right so red marks the winner
- Spec: `left/right: {header, header_color?, body | bullets}`

### `process` (alias `timeline`)
3–6 numbered steps on a horizontal connector.
- 0.62" Adobe red discs with white Adobe Clean Black numerals, `#C4C4C4`
  connector line, optional 11pt gray label above each disc (dates/phases),
  14pt bold step title, 11pt gray description — all centered per column
- Spec: `steps: [{title, desc?, label?}]`

### Layout 49 — Blank (Light) / 50 — Blank (Dark)
**When:** Custom slide where you place content from scratch.
- Background only, red thread present (light) or full black with thread (dark)
- No placeholders — Claude positions content manually using the brand-system positions

### Layout 51 — Gray End Slide
**When:** Final slide of the deck (thank you, contact, Q&A)
- Light gray background with subtle Adobe wordmark

---

## Choosing the right layout — decision tree

```
Is it the first slide?
├── Yes → Layout 1 (red) by default. Layout 3 (dark) for premium. Layout 2 (white) for technical.
└── No → continue

Is it a section break?
├── Yes → Layout 6 (light) or 7 (dark)
└── No → continue

Is it the agenda?
├── Yes → Layout 54
└── No → continue

Is the content STRUCTURED? (check BEFORE counting columns)
├── rows × columns data (pricing, plans)  → `table`
├── 2–4 hero numbers (totals, ROI)        → `stat-row`
├── A vs B (before/after, options)        → `comparison`
├── 2–6 features/pillars/products         → `cards`
├── phases / timeline / how-it-works      → `process`
└── No, it's narrative → continue

How many parallel ideas / columns?
├── 1     → Layout 55 (light airy) — the workhorse
├── 1+img → Layout 10 (½ image) or 11 (⅓ image)
├── 2     → Layout 12 (text only), 15 (img+text), 20 (photo+name)
├── 3     → Layout 13 / 16 / 22
├── 4     → Layout 18 / 17 / 21
├── 5     → Layout 14 / 19 / 23
└── grid  → Layout 25 (2×2), 26 (3×2), 27 (8×4 logo wall)

Is it a pull-quote?
├── Yes → Layout 8 (light) / 28 (dark)
└── No

Is it the closing slide?
└── Layout 51 (gray) — or repeat Layout 1 styling with a "Thank you" title
```

---

## Edge cases

### Long titles
- Hard cap: **3 lines on Layout 1 (77pt)**, 4 lines on doc-style covers (65pt). If it overflows, the title is too long — rewrite, don't shrink the font.
- Adobe's Brand Guidelines explicitly say "Title should be no longer than four lines" for documents.

### Dense data slides
- Tables: 11–12pt body, 14pt headers, alternating row shading `#F5F5F5` / white. Header row red `#EB1000` with white text.
- Charts: most series in grayscale (`#191919`, `#5F5F5F`, `#919191`, `#C4C4C4`); highlight one critical series in ONE extended-palette color. Never `#EB1000` for chart data.
- Maximum 7 data points per series in a presentation chart. If more, summarize or use small multiples.

### Image-heavy slides
- Image area: should never overlap the red thread.
- Image credit: 9pt Adobe Clean Regular, color `#191919` or white, bottom-right of the image.
- Devices around screenshots: light gray on light bg, dark gray on dark bg.

### Bullets — max 3 levels
| Level | Size | Marker |
|---|---|---|
| L1 | 18pt | round bullet `•` |
| L2 | 14pt | en-dash `–` |
| L3 | 12pt | em-dash `—` or hollow circle |

If a slide needs more than 3 levels, restructure into a multi-column layout instead.

### Cover with subtitle wraps
- Subtitle is allowed to wrap to 2 lines max at 24pt.
- If speaker + role + date all needed: use the format `Speaker Name | Speaker Title` on line 1, date on line 2.

---

## Build invocation reminder

To produce a slide from a layout, the JSON spec uses the `layout` key with the layout NAME (not number):

```json
{
  "slides": [
    {"layout": "title-red", "title": "...", "subtitle": "..."},
    {"layout": "agenda", "rows": [...]},
    {"layout": "section-light", "title": "..."},
    {"layout": "content", "title": "...", "bullets": [...]},
    {"layout": "two-col-img", "title": "...", "left": {...}, "right": {...}},
    {"layout": "quote", "quote": "...", "attribution": "..."},
    {"layout": "thank-you", "title": "Thank you", "contact": "..."}
  ]
}
```

The script maps these names to the official layout numbers. See `scripts/build_deck.py` for the full schema.
