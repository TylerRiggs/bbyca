# Adobe Design System — shared brand brain

This skill now carries the Adobe Design System (from the Adobe Brand Guidelines,
Jan 6 2025) so that **every** artifact — `.pptx`, `.docx`, and any HTML mockup
or prototype — comes from one source of truth. The OOXML builders encode these
rules in Python (`scripts/brand.py`); for HTML, use the bundled tokens directly.

> The goal is Claude-Design-level fidelity without Claude Design: authentic
> Adobe look and feel, approved assets, real type, correct colour discipline.

## Bundled assets

| Path | Use |
|---|---|
| `assets/adobe-design-system.css` | All design tokens as CSS variables + `@font-face` for Adobe Clean. Link this in any HTML output. |
| `assets/fonts/` | 21 Adobe Clean OTF cuts (embedded into `.pptx`/`.docx`; `@font-face`'d in HTML). |
| `assets/logos/` | Approved wordmark + icon (Red/White; SVG/PNG/EPS). See `logo-usage.md`. |

## Colour discipline (the thing that most often reads "off-brand")

- **Core palette is only three colours:** Adobe Red `#EB1000`, Black `#000000`, White `#FFFFFF`. Red is the hero — "use it generously," but as accent/structure, not as large fills behind narrative text.
- **Extended palette (14 colours)** = charts, diagrams, icons, illustrations **only**. Never as a layout's primary colour, never behind body copy, **never tinted or transparent** — full saturation only. One accent per chart; the rest in grays.
- **Never** use Adobe Red for body text, for "error/negative" semantics in charts, or as a chart bar colour. Red reads as the brand, not as data.
- Text colour is always white, black, or (sparingly, for labels/subheads) Adobe red.
- Backgrounds: solid **white** or solid **black** — both fully on-brand. No off-whites, no gradients behind content.

### Colour worlds (imagery, when you place photography)
- Brand / Experience Cloud / Acrobat → **red** world
- Photoshop → **blue** world
- Express → **full-spectrum gradient** world

### Red intensity (for imagery/hero treatments)
- **Pop** — a small red accent. **Focus** — a red "lens" frame. **Flood** — a red-dominated image.

## The Lens
Adobe's signature image treatment is a **rounded-rectangle viewport** ("the
Lens") that crops imagery — it represents "Adobe's point of view." When you
place a photo in a hero/cover, crop it into a rounded rectangle rather than a
hard-edged full bleed. (In CSS: a container with `border-radius` ~16–28px and
`overflow:hidden`.)

## Typography
- **Adobe Clean** everywhere. Five brand weights: Black (900), ExtraBold (800), Bold (700), Regular (400), SemiLight (350).
- Hierarchy by weight: Headline → Black • Section head → ExtraBold • Subhead → Bold • Body → Regular • Pull-quote (Experience Cloud only) → SemiLight.
- Headlines: **sentence case**, ending in `.` or `?`; tracking −0.02em, leading ~90%.
- Body: tracking 0, leading 150% on screen (120% print).
- Real family names: body = **`Adobe Clean`**; headline weight = **`Adobe Clean Black`** (NOT "Adobe Clean Display Black" — that family is not in this kit; see `brand-system.md`).

## Voice (one word: conversational)
Human, inspiring, progressive, creative. Sentence case. No buzzwords, no
jargon, no ALL CAPS, no emoji in brand/UI copy. Always "Adobe" (not "Adobe Inc."
/ "Adobe Systems"); no ™/® on marks in body copy. AI is a tool that empowers the
human creator — never "the magic of AI," never AI as a replacement. Full guide
in `voice-and-tone.md`.

## Using the tokens in HTML

```html
<link rel="stylesheet" href="assets/adobe-design-system.css">
<style>
  body { font-family: "Adobe Clean", system-ui, sans-serif; color: var(--fg-1);
         background: var(--bg-1); line-height: 1.5; }
  h1   { font-family: "Adobe Clean Black", "Adobe Clean", sans-serif;
         font-weight: 900; letter-spacing: -.02em; line-height: .92; }
  .thread { border-left: 6px solid var(--adobe-red); }   /* the red thread */
</style>
<img src="assets/logos/Adobe_Wordmark_RGB_Red.svg" alt="Adobe" height="28">
```

### Two ways to produce HTML

1. **Document-style HTML (fastest, portable):** run
   `python scripts/build_html.py spec.json out.html` with the same JSON spec as
   `build_doc.py`. You get **one self-contained file** — Adobe Clean is subset
   and base64-embedded, the wordmark is inlined, the red thread + footer are in
   place. Nothing to ship alongside; it renders on-brand on any machine. This is
   the HTML analog of embedding fonts into a `.pptx`/`.docx`.

2. **Custom layout / prototype:** start from
   `assets/html-templates/adobe-page.html`, link `assets/adobe-design-system.css`,
   and place a logo from `assets/logos/`. When you hand this to the user, either
   **copy the referenced asset files alongside the HTML** so paths resolve, or
   bake it self-contained the way `build_html.py` does (base64 `@font-face` +
   inline wordmark SVG).

Validate any HTML with `python scripts/validate.py out.html` — it flags a
hand-drawn/omitted logo, missing Adobe Clean, and off-brand copy.

See also: `brand-system.md` (exact OOXML values), `slide-layouts.md`,
`document-styles.md`, `dos-and-donts.md`, `logo-usage.md`.
