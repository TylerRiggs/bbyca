# Assets

This folder contains the licensed Adobe wordmark and icon files. The builder scripts pick them up automatically.

## What's present

| File | Used by | When |
|---|---|---|
| `logos/Adobe_Wordmark_RGB_Red.png` | `build_deck.py`, `build_doc.py` | Light-background covers, thank-you slides, document header |
| `logos/Adobe_Wordmark_RGB_White.png` | `build_deck.py` | Red and dark-background covers |
| `logos/Adobe_Wordmark_RGB_Red.svg` | (available for vector use) | — |
| `logos/Adobe_Wordmark_RGB_White.svg` | (available for vector use) | — |
| `logos/Adobe_Wordmark_RGB_Red.eps` | (high-res print) | — |
| `logos/Adobe_Wordmark_RGB_White.eps` | (high-res print) | — |
| `logos/Adobe_icon_RGB_red.png` | (secondary identifier, currently unused — see below) | — |
| `logos/Adobe_icon_RGB_white.png` | (secondary identifier, currently unused) | — |
| `logos/Adobe_icon_RGB_red.svg` / `.eps` | (vector / print) | — |
| `logos/Adobe_icon_RGB_white.svg` / `.eps` | (vector / print) | — |

The PNGs are 3151×763 (wordmark) and 1004×889 (icon), high enough for any common output size.

## How the wordmark is placed

### PPTX (`build_deck.py`)
- **Title slides** (`title-red`, `title-white`, `title-dark`): wordmark in lower-left at 1.30" wide, x=0.67" (clear of the red thread), y just above the footer. White wordmark on red/dark backgrounds; red wordmark on light.
- **Thank-you / closing slide**: red wordmark, same position.
- **Content / section / multi-col slides**: no wordmark — the red thread and footer text provide identity, per the official Adobe deck convention.

### DOCX (`build_doc.py`)
- **Page header**: red wordmark at 0.70" wide above a thin red rule. Appears on every page.

## Brand-compliance rules baked in

- Clear space around the wordmark ≥ ½ icon width (~0.15" at default size) — enforced by leaving x=0.67" margin (which is well clear of the 0.14" red thread, giving ~0.53" of breathing room).
- Minimum size: wordmark 0.75" wide print / 16px screen. The 0.70" used in the header is **just under print minimum** — acceptable for screen-first docs that will export to PDF and be read at ≥100% zoom. If you'll print at original size, bump to 1.0" by editing `_setup_header` in `build_doc.py`.
- Color rule: red on light, white on dark/red. Never black on imagery.

## Fonts (bundled + embedded)

The 21 Adobe Clean OTF cuts ship in `assets/fonts/`. The builder scripts:
1. **Name** the real families in every run — body `Adobe Clean`, headline `Adobe Clean Black` (NOT "Adobe Clean Display Black", which isn't in this kit and would silently fall back).
2. **Embed** Adobe Clean into the output via `scripts/embed_fonts.py`:
   - PPTX → raw OpenType in `ppt/fonts/*.fntdata` + `<p:embeddedFontLst>`.
   - DOCX → OTF converted to TrueType (fontTools + cu2qu), obfuscated, in `word/fonts/*.odttf`.

So the file renders correctly even on machines without Adobe Clean installed.
The fonts carry `fsType=8` (editable embedding permitted), so this is
licence-compatible for internal Adobe use. For an external, pixel-perfect
handoff, export to PDF — the embedded font travels inside the PDF.

## Hard rule

Adobe Clean and the wordmark files are licensed assets. **Do not commit them to any public repository.** This skill folder should remain inside the user's local `~/.claude/skills/` or an internal-only git remote.
