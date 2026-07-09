# Examples

Each subfolder is a worked example: a JSON spec → a brand-compliant Adobe `.pptx` or `.docx`.

## How to run an example

```bash
# From the adobe-presentation/ root
python scripts/build_deck.py examples/customer-pitch-deck/input.json out.pptx
python scripts/build_doc.py  examples/discovery-one-pager/input.json   out.docx
python scripts/build_doc.py  examples/exec-summary-doc/input.json      summary.docx

# Validate
python scripts/validate.py out.pptx
python scripts/validate.py out.docx
```

## What each example demonstrates

### `customer-pitch-deck/`
A 14-slide external customer pitch:
- **Cover** (full red) → **agenda** → **section dividers** (light + dark)
- **Standard content** slide with lead paragraph + bullets
- **`comparison`** "before / after" boxed panels
- **`cards`** capability overview
- **Pull-quote** with attribution
- **`stat-row`** proof-point KPI cards
- **`process`** 90-day path timeline
- **Thank you / contact** closing slide

Covers the workhorse layouts you'll use 80% of the time.

### `pricing-proposal-deck/`
A 7-slide commercial proposal built almost entirely from the
**structured-visual layouts** (see SKILL.md Step 2a):
- **`table`** — pricing grid with black header band, alternating row shading,
  red total band, a `highlight` callout with the 3-year hero number, and a
  `notice` strip for the signature deadline
- **`stat-row`** — three KPI cards (total, savings, product count)
- **`comparison`** — standalone vs. bundled panels (red band = recommended)
- **`process`** — dated path-to-signature timeline
- **`cards`** — what's-included product cards

This is the reference for "how do I make a money/metrics deck look designed,
not like a bullet list." If your deck has pricing, KPIs, options, or a
timeline, start here.

### `discovery-one-pager/`
A multi-page discovery readout produced as a Word doc:
- **Red cover block** with title + subtitle
- **H1 / H2 / H3** hierarchy
- **Body prose** + **callout boxes** for key insights
- **Tabular** capabilities/timeline
- **Bullets** at multiple levels

Covers the post-meeting leave-behind format.

### `exec-summary-doc/`
A short executive summary with:
- Red cover block
- Recommendation up front
- KPI table with baseline / 12-week / 12-month targets
- Risks/mitigations bullets
- **Trademark attribution page** appended at the end (legal compliance)

Covers the decision-document format used for operating-committee asks.

## Building your own spec

Start from the closest example and modify. Key JSON conventions:

- **Layout names** (PPTX): see `references/slide-layouts.md` or `scripts/brand.py:LAYOUT_INDEX`.
- **Section types** (DOCX): `h1`, `h2`, `h3`, `h4`, `body`, `bullets`, `callout`, `table`.
- **Voice:** sentence-case headlines ending with `.` or `?`. See `references/voice-and-tone.md`.
- **Length:** title slide titles ≤ 3 lines, section dividers ≤ 4 words, bullets ≤ 7 per slide.

Run `validate.py` before delivering to the user. Fix every issue it reports.
