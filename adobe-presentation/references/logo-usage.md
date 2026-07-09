# Adobe logo & identity — approved assets only

> **The single most important rule in this skill.** The Adobe wordmark and the
> Adobe icon (the red triangular "A") are legally controlled marks. You must
> place the **supplied files** from `assets/logos/`. You must **never** draw,
> redraw, trace, approximate, recolor, restyle, re-letter, or "build" an Adobe
> logo — not with shapes, not with SVG paths, not with a CSS triangle, not with
> a font glyph, not by typing "Adobe" in a bold typeface. A recreated mark is a
> brand-compliance failure even if it looks close.

This applies to **every** way you might produce output: the builder scripts,
the PowerPoint/Word MCP tools, HTML mockups/prototypes, canvas artifacts, or
anything you render directly in chat. If you cannot place one of the approved
files, place **no logo at all** and tell the user why — do not substitute an
approximation.

---

## The approved files (in `assets/logos/`)

| File | What it is | Use |
|---|---|---|
| `Adobe_Wordmark_RGB_Red.svg` / `.png` / `.eps` | Full "Adobe" wordmark, red | Light backgrounds |
| `Adobe_Wordmark_RGB_White.svg` / `.png` / `.eps` | Full "Adobe" wordmark, white | Dark / red / photographic backgrounds |
| `Adobe_icon_RGB_red.svg` / `.png` / `.eps` | The triangular "A" icon, red | Light backgrounds, when a compact mark is needed |
| `Adobe_icon_RGB_white.svg` / `.png` / `.eps` | The triangular "A" icon, white | Dark / red backgrounds |

- **Prefer the wordmark** for document/slide identity (covers, headers, closings).
- Use the **icon** only as a small secondary device (e.g. a favicon-scale mark, a slide-corner accent) — never as a replacement for the wordmark on a cover.
- **SVG** for HTML/vector contexts; **PNG** for Office/raster contexts; **EPS** for high-res print.
- There is **no black wordmark** in this kit. Black is only ever a single-colour print fallback per Brand Center; do not invent one.

The PNGs are high-resolution (wordmark 3151×763 ≈ 4.13:1; icon ≈ 1004×889). The
builder scripts read these automatically (`build_deck.py`, `build_doc.py`).

---

## Choosing red vs white

| Background | Mark |
|---|---|
| White / light / `#F5F5F5` | **Red** wordmark or icon |
| Black / dark / Adobe red `#EB1000` | **White** wordmark or icon |
| Busy or photographic | White on dark/saturated imagery; red on warm/light imagery. **Never black on imagery.** Check contrast first. |

---

## Clear space & minimum size

- **Clear space** ≥ the height of the icon (the "A") on all four sides. Nothing — text, rules, other logos, image edges — intrudes into that zone.
- **Minimum size:** wordmark ≥ 0.75" wide in print / 16 px on screen. Below that, use the icon instead.
- Never stretch, condense, rotate, add effects (shadow/bevel/glow/gradient), outline, or place inside a box/lozenge.

---

## Hard "never" list

- ❌ Drawing the triangular "A" with shapes, polygons, SVG `<path>`, CSS borders, or `clip-path`.
- ❌ Setting the word "Adobe" in Adobe Clean (or any font) and calling it the logo.
- ❌ Recoloring the supplied files to any colour other than the red/white variants provided.
- ❌ Using an old/legacy Adobe logo, a product logo (Photoshop "Ps", etc.), or a self-made lockup.
- ❌ Generating a logo with an image model or "recreating it from memory."
- ❌ Placing the wordmark as live/selectable text.

## Always

- ✅ Place `assets/logos/<approved file>` as an image (Office) or `<img>`/inline `<svg>` from the file (HTML).
- ✅ Pick red/white by background; respect clear space and minimum size.
- ✅ If no approved file fits the context, omit the logo and say so — never approximate.

---

## How each generation path places the mark

### Builder scripts (PPTX/DOCX) — already correct
`build_deck.py` calls `add_wordmark()` (white on red/dark covers + closings,
red on light); `build_doc.py` places the red wordmark in the page header. No
action needed beyond running them.

### PowerPoint / Word MCP tools
After creating the slide/doc, **insert the image** from the absolute path to the
approved file, e.g. `assets/logos/Adobe_Wordmark_RGB_White.png` on a red cover.
Do not type "Adobe" as a title-styled stand-in for the logo.

### HTML mockups / prototypes / canvas
Reference the file directly — never inline a hand-built path:

```html
<!-- correct: the approved asset -->
<img src="assets/logos/Adobe_Wordmark_RGB_Red.svg" alt="Adobe" height="28">
```

```html
<!-- WRONG: a hand-drawn approximation -->
<svg viewBox="0 0 40 36"><path d="M..."/></svg>   <!-- never do this -->
<div class="adobe-a"></div>                          <!-- never do this -->
```

The validator (`scripts/validate.py`) fails any `.pptx`/`.docx` that contains no
placed image on its slides/header, on the assumption a logo was drawn or omitted.
