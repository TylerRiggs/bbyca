---
name: adobe-presentation
description: Use this skill whenever creating or editing an Adobe-branded PowerPoint (.pptx) or Word (.docx) document. Triggers on any mention of "deck," "slides," "presentation," "pptx," "Word doc," "document," "one-pager," "leave-behind," "brief," "RFP response," "executive summary," ".docx," or any sales, customer-facing, or internal Adobe collateral that must look authentically Adobe. Covers the Adobe red (#EB1000) + black + white core palette, the 14-color extended chart palette with PMS values, the two-font Adobe Clean system (Adobe Clean Black for headlines + Adobe Clean for body), exact slide dimensions and placeholder positions extracted from Adobe's official 56-layout template, the mandatory left red thread, footer line, voice-and-tone rules, and ready-to-run Python builder scripts — including structured-visual layouts (styled tables with header/total bands, KPI stat cards, feature-card grids, comparison panels, process timelines, callout and notice strips) so structured content is never flattened into generic bullet slides.
---

# Adobe Presentation & Document Skill

You are producing Adobe-branded collateral. **Authentic Adobe output is non-negotiable.** Wrong red, wrong font, wrong stripe width, wrong footer wording — or a **made-up logo** — is a brand-compliance failure, not a stylistic preference. The goal is Claude-Design-level fidelity: output that looks authentically Adobe, not "Claude-generated."

> ## ⛔ RULE ZERO — never recreate the Adobe logo
> Place the **approved files** from `assets/logos/` (wordmark or icon, red or white). **Never draw, trace, approximate, recolor, re-letter, or "build" an Adobe logo** — not with shapes, SVG paths, a CSS triangle, a font glyph, an image model, or by typing "Adobe" in a bold font. If no approved file fits the context, place **no logo** and say why. **This applies to every output path** — the builder scripts, the PowerPoint/Word MCP tools, HTML mockups, canvas artifacts, and anything you render in chat. Full rules: `references/logo-usage.md`.

This skill ships:
1. The official Adobe slide template (`templates/adobe-deck-template.pptx`) with all 56 master layouts baked in.
2. Python builder scripts that produce on-brand `.pptx` and `.docx` files from a JSON content spec — and **embed Adobe Clean into the output** so it renders correctly for recipients who don't have the font.
3. The approved Adobe **wordmark + icon** (red + white; SVG/PNG/EPS) in `assets/logos/` — placed automatically on cover slides, thank-you slides, and document headers.
4. The full **Adobe Design System** — 21 Adobe Clean OTF cuts (`assets/fonts/`), all design tokens as CSS (`assets/adobe-design-system.css`), and an HTML starter (`assets/html-templates/`) — so HTML mockups share the same brand brain. See `references/design-system.md`.
5. Reference files with exact extracted values (colors, type sizes, positions) from the Adobe Brand Guidelines and the official Adobe Presentation Style Guide.

## Step 0 — Which path are you on?

| You are building… | Do this |
|---|---|
| A `.pptx` or `.docx` | Use the **builder scripts** (Steps 1–7 below). They embed fonts + place the approved logo automatically. |
| An **HTML document** (report, one-pager, brief, leave-behind) | Run **`scripts/build_html.py spec.json out.html`** — same JSON spec as `.docx`. It produces a **single self-contained file** with Adobe Clean subset+base64-embedded and the wordmark inlined. Renders on-brand anywhere, nothing to ship alongside. |
| A **custom HTML layout / prototype / canvas** | Read `references/design-system.md`; start from `assets/html-templates/adobe-page.html`, link `assets/adobe-design-system.css`, and place a logo from `assets/logos/`. Copy the asset files alongside the HTML so paths resolve (or bake to self-contained — see design-system.md). |
| A deck/doc via the PowerPoint/Word MCP tools | Prefer the builder scripts for full fidelity. If you must use the MCP tools, still **insert the approved logo image file** (never a drawn one) and specify Adobe Clean fonts. |

Whatever the path: **Rule Zero and the colour/type/voice rules always apply.**

---

## Step 1 — Pick the output format

| User says | Output | Script |
|---|---|---|
| "deck," "slides," "presentation," "pitch," ".pptx," "PowerPoint," "Keynote" | PPTX | `scripts/build_deck.py` |
| "Word doc," "document," "one-pager," "leave-behind," "brief," "RFP," "exec summary," ".docx" | DOCX | `scripts/build_doc.py` |

If the user is ambiguous ("can you write this up for X"), default to **DOCX** for read-along content (memos, briefs, summaries) and **PPTX** for meeting/screen-share content (pitches, reviews).

---

## Step 2 — Build the content spec, then run the script

**Do not hand-author OOXML or hand-place every shape.** Instead:

1. Read `references/brand-system.md` (always — this is the source of truth for colors/type/logo rules).
2. Read the layout reference for the chosen format:
   - PPTX → `references/slide-layouts.md`
   - DOCX → `references/document-styles.md`
3. Construct a JSON content spec matching the schema in the script's docstring.
4. Run the script with `python scripts/build_deck.py spec.json output.pptx` (or `build_doc.py`).
5. Validate with `python scripts/validate.py output.pptx` — confirms red thread, footer, and font on every slide.

A worked example is in `examples/customer-pitch-deck/input.json`.

---

## Step 2a — Structured content gets a structured layout (never a bullet wall)

**The #1 failure mode of this skill is flattening rich content into plain
bullets.** A pricing option, a metrics summary, or a before/after comparison
rendered as text-only bullets looks generic and unfinished — a designer would
build bands, cards, and callout boxes. The builder has those layouts; use them.

Map the content to the layout **before** writing the spec:

| The slide's content is… | Use layout | Never |
|---|---|---|
| Pricing, plans, anything rows × columns | `table` (header band, shaded rows, `total_row`, `highlight`, `notice`) | bullets with dollar figures |
| 2–4 key numbers (totals, savings, ROI, counts) | `stat-row` (hero-number KPI cards) | bullets like "Total: $450,000" |
| Options, before/after, us vs. them | `comparison` (two boxed panels, red = recommended side) | two plain text columns |
| 2–6 features, pillars, products, workstreams | `cards` (accent-bar card grid) | a bullet list of names + descriptions |
| Phases, timeline, "how it works", next steps | `process` (numbered discs on a connector line) | numbered bullets |
| A deadline, caveat, or legal condition | `notice` key on any of the above (bottom accent strip) | burying it in a sub-bullet |
| Genuinely narrative prose (an argument, a story) | `content` — bullets are correct here | — |

Extras available on every structured layout (and `content`):
- `kicker` — red bold eyebrow line under the title (category/context label)
- `notice` — bottom caveat strip with a semantic accent bar

**Self-check before building:** if more than half your body slides are
`content` bullet slides, you have almost certainly under-designed the deck.
`validate.py` warns on this. Full layout specs: `references/slide-layouts.md`
(§ "Structured-visual layouts") and the schema examples in
`scripts/build_deck.py`'s docstring. A worked pricing example:
`examples/pricing-proposal-deck/input.json`.

---

## Step 3 — Authoritative brand values (memorize these)

These are extracted from page 43 of the Adobe Brand Guidelines and the master slide of the official Adobe Presentation Style Guide. Do not approximate or substitute.

### Core palette (structural — backgrounds, type, accents)
| Color | Hex | RGB | CMYK | PMS |
|---|---|---|---|---|
| **Adobe red** | `#EB1000` | 235 16 0 | 0 96 100 0 | 2347 C |
| **Black** | `#000000` | 0 0 0 | 60 40 40 100 | Black 3 C |
| **White** | `#FFFFFF` | 255 255 255 | 0 0 0 0 | — |

### Functional grays (from the official Adobe master slide)
| Use | Hex |
|---|---|
| Footer text, copyright, slide number | `#191919` (NOT `#999999`) |
| Light section background, table alt rows | `#F5F5F5` |
| Secondary body text on dark slides | `#C4C4C4` |

### Typography — two-font system (NOT one)
| Font name | Use | Notes |
|---|---|---|
| **Adobe Clean Black** | All headlines, slide titles, section dividers, cover titles | The real family that ships in `assets/fonts/` (`AdobeClean-Black.otf`). **Do not use "Adobe Clean Display Black"** — that is a different Adobe typeface that is NOT in this kit, so naming it makes every headline silently fall back. The weight is built into the family: do not also apply synthetic bold. |
| **Adobe Clean** | Body, subheads, captions, bullets, footers | Use Regular, Bold, or SemiLight weight. SemiLight only for Experience Cloud pull-quotes. |

Both families are **bundled** in `assets/fonts/` and **embedded into the output** by the builder scripts, so the file renders correctly even if the recipient hasn't installed Adobe Clean. Never substitute Arial/Calibri in code — always specify the real Adobe font name.

### Type sizes (extracted directly from the official Adobe deck and brand guidelines)

**PPTX (13.33" × 7.5" widescreen):**
| Element | Size |
|---|---|
| Cover/title slide title | **77pt** Adobe Clean Black |
| Cover subtitle / speaker / date | **24pt** Adobe Clean Regular |
| Section divider title | **72pt** Adobe Clean Black |
| Content slide title | **32pt** Adobe Clean (Black or Bold weight) |
| Lead paragraph (intro) | **32pt** Adobe Clean Regular |
| Body bullets — L1 / L2 / L3 | **18pt / 14pt / 12pt** Adobe Clean Regular |
| Column header (multi-col layouts) | **16pt** Adobe Clean Bold |
| Caption / image credit | **9pt** Adobe Clean Regular |
| Footer (legal + page #) | **6pt** Adobe Clean Regular, color `#191919` |

**DOCX (US Letter, 1" margins, slightly wider 1.1" left):**
| Element | Size |
|---|---|
| Cover title (red block) | **65pt** Adobe Clean Black, white |
| Cover subtitle | **24pt** Adobe Clean Regular, white |
| H1 | **24pt** Adobe Clean Black, black, w/ red left border |
| H2 | **16pt** Adobe Clean Bold, black |
| H3 | **14pt** Adobe Clean Bold, Adobe red |
| Body | **10pt** Adobe Clean Regular, line spacing 1.15 |
| Footer | **8pt** Adobe Clean Regular, gray `#191919` |

### The left red thread (mandatory)
| Format | Spec |
|---|---|
| PPTX | Rectangle: `x=0", y=0", w=0.14", h=7.5"`, fill `#EB1000`, no border. **On every slide except full-red title slides.** |
| DOCX | Paragraph border: `left, single, size 48 (8th-of-pt), color EB1000, space 8`. On H1 headings and the cover block. |

### Footer wording (exact, do not paraphrase)
```
© [current year] Adobe. All Rights Reserved. Adobe Confidential.
```
Right-aligned, 6pt PPTX / 8pt DOCX, color `#191919`. Page number appears right of the legal line.

---

## Step 4 — Hard rules (these break the brand)

| ❌ Never | ✅ Always |
|---|---|
| Use `#999999`, `#666666`, or any "gray-ish" for footer | Use `#191919` — extracted from Adobe's master |
| Make the red thread 0.10" or 0.12" wide | `0.14"` exactly, x=0, y=0, h=7.5 |
| Color chart bars `#EB1000` | Gray bars + ONE extended-palette highlight. Red reads as error in data context |
| Use ALL CAPS headlines | Sentence case. End with `.` or `?` |
| Use red for body text | Red is reserved for: wordmark, thread, category labels, structural accents |
| Use tones/transparencies of brand colors | Solid full saturation only |
| Use any font other than Adobe Clean / Adobe Clean Black | Specify the real font in code; fonts are embedded automatically. |
| Use "Adobe Systems" or "Adobe Inc." in copy | Use just "Adobe" |
| Add ™ or ® to "Adobe" or product names | Adobe does not bug its marks |
| Use legacy logos, "A" icon-substitution, or self-built lockups | Marks come from Brand Center only |
| Place wordmark on busy imagery without checking contrast | Red wordmark on saturated/dark imagery; white wordmark on warm/light imagery; never black on imagery |
| Use stock gradients, drop shadows, bevels, or 3D effects | Flat color only |
| Exceed 3 bullet levels | Restructure |
| Flatten pricing, metrics, options, or timelines into plain bullets | Use the structured layouts: `table`, `stat-row`, `cards`, `comparison`, `process` (Step 2a) |

For the full list see `references/dos-and-donts.md`.

---

## Step 5 — Voice (every word you write goes here)

- **Conversational, human, not corporate.** "People talking to people."
- **Confident but not arrogant.** "Creativity is everywhere. Now Photoshop is too." (good) vs. "Experience the power of creativity, transforming your ideas into art." (bad — corporate AI-marketing-speak)
- **Sentence case headlines.** End with period or question mark.
- **AI framing:** AI is a tool that empowers humans. Never personify AI; never frame it as a replacement for creative judgment. Say "Imagine what you can do with AI" — not "the magic of AI."
- **Company name in copy:** always `Adobe`. Never `Adobe Inc.`, `Adobe Systems`, etc., except in legal/contract context.

Full voice guide: `references/voice-and-tone.md`.

---

## Step 6 — Build the file

**For PPTX:**
```bash
python scripts/build_deck.py path/to/spec.json output.pptx
```
The script builds slides at the exact Adobe master coordinates, places the approved wordmark on covers/closings, and **embeds Adobe Clean** into the file.

**For DOCX:**
```bash
python scripts/build_doc.py path/to/spec.json output.docx
```

**For HTML** (same spec as DOCX — sections of `h1`/`h2`/`h3`/`body`/`bullets`/`callout`/`table`):
```bash
python scripts/build_html.py path/to/spec.json output.html
```
Produces one self-contained `.html` — Adobe Clean subset+base64-embedded, wordmark inlined, red thread, Adobe footer. No external assets to ship.

Both Office scripts embed Adobe Clean automatically (it carries `fsType=8`, embedding-permitted). Pass `--no-embed` to skip embedding (smaller file; relies on the recipient having the font). To embed into a file built another way:
```bash
python scripts/embed_fonts.py output.pptx   # or output.docx
```

**File naming:** `adobe-[account-or-topic]-[type].(pptx|docx)` — e.g. `adobe-acmecorp-discovery-deck.pptx`, `adobe-q1-leave-behind.docx`.

---

## Step 7 — Validate before delivering

```bash
python scripts/validate.py output.pptx     # or .docx or .html
```
Checks all three formats: a real logo asset is present (catches drawn/omitted logos), red thread on every non-full-red slide, correct footer, Adobe Clean fonts only, no placeholder/lorem text, no disallowed body colors, no banned phrases — and **warns if Adobe Clean isn't embedded** (`.pptx`/`.docx`) or not loaded via `@font-face`/base64 (`.html`).

Because fonts are embedded, the output renders correctly on machines without Adobe Clean. For a guaranteed-pixel-perfect handoff (e.g. external recipients), export to PDF — fonts travel inside the PDF:

> Open in PowerPoint/Word → File → Export → PDF. The embedded Adobe Clean renders identically everywhere.

---

## File map

```
adobe-presentation/
├── SKILL.md                         (this file — entry point)
├── references/
│   ├── brand-system.md              colors, type, logo, marks — full spec
│   ├── design-system.md             Adobe Design System brain (HTML + OOXML)
│   ├── logo-usage.md                ⛔ approved-logo rules (Rule Zero)
│   ├── slide-layouts.md             every PPTX layout with exact dims
│   ├── document-styles.md           DOCX section patterns
│   ├── dos-and-donts.md             explicit anti-patterns
│   └── voice-and-tone.md            writing voice + AI framing
├── scripts/
│   ├── brand.py                     shared constants (colors, fonts, sizes)
│   ├── build_deck.py                python-pptx builder (auto-embeds fonts)
│   ├── build_doc.py                 python-docx builder (auto-embeds fonts)
│   ├── build_html.py                self-contained on-brand HTML (embeds fonts)
│   ├── embed_fonts.py               embed Adobe Clean into .pptx/.docx
│   └── validate.py                  QA: logo / red thread / footer / fonts (pptx, docx, html)
├── templates/                       (OPTIONAL reference only — NOT used by the
│   ├── adobe-deck-template.pptx      scripts, which build from scratch at exact
│   └── adobe-doc-template.docx       Adobe coordinates. Omitted from the shared zip.)
├── assets/
│   ├── logos/                       approved wordmark + icon (Red/White, SVG/PNG/EPS)
│   ├── fonts/                       21 Adobe Clean OTF cuts (bundled, embedded)
│   ├── adobe-design-system.css      all design tokens + @font-face (for HTML)
│   ├── html-templates/              on-brand HTML starter (adobe-page.html)
│   └── README.md
└── examples/
    ├── customer-pitch-deck/         sample deck spec → output
    ├── discovery-one-pager/         sample one-pager spec
    └── exec-summary-doc/            sample exec summary spec
```

---

## Packaging & distribution

This skill is self-contained — fonts, logos, tokens, and scripts all travel
inside the folder — so it can be shared with teammates who don't have Claude
Design. To distribute: zip the `adobe-presentation/` folder and have the
recipient drop it in `~/.claude/skills/` (or `~/.agents/skills/`).

**Licensing:** Adobe Clean and the logo files are licensed, internal-only Adobe
assets (the fonts carry `fsType=8`, editable-embedding-permitted). **Do not commit
this skill to any public repository.** Keep it on internal-only remotes or local
skill folders. The first-run dependency is `python-pptx`, `python-docx`,
`fonttools`, and `cu2qu` (the last two only for `.docx` font embedding).
