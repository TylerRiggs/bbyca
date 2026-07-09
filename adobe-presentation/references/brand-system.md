# Adobe Brand System — Full Spec

Source: Adobe Brand Guidelines (Jan 6, 2025, internal) + Adobe Presentation Style Guide Revision 1.7 (Jan 2026 master slide).

This document is the canonical reference for every color value, font, dimension, and mark rule used by this skill. **Never approximate. Never substitute.**

---

## 1. Core color palette

> "Our palette is simple — red, black, and white." (Brand Guidelines p.44)

### Adobe red — the single most important brand asset
| Spec | Value |
|---|---|
| HEX | `#EB1000` |
| RGB | 235, 16, 0 |
| CMYK | 0, 96, 100, 0 |
| PMS | 2347 C |
| RAL | 3020 |

Use generously. It is the primary brand color. **Reserved for:** the red thread, wordmark/lockups, category labels, section identifiers, structural accents. Not for body text, not for chart data (red reads as "error" in a data context).

### Black
| Spec | Value |
|---|---|
| HEX | `#000000` |
| RGB | 0, 0, 0 |
| CMYK | 60, 40, 40, 100 |
| PMS | Black 3 C / RAL 9005 |

### White
| Spec | Value |
|---|---|
| HEX | `#FFFFFF` |
| RGB | 255, 255, 255 |
| CMYK | 0, 0, 0, 0 |
| RAL | 9016 |

---

## 2. Extended palette (charts, diagrams, accents only)

> "Use colors from this set for graphics, diagrams, icons, illustrations, and backgrounds. Don't use tones or transparencies of the colors." (Brand Guidelines p.46)

| Name | HEX | RGB | PMS |
|---|---|---|---|
| Pink | `#FF4885` | 255 72 133 | 1915 |
| Magenta | `#F24CB8` | 242 76 184 | 806 |
| Violet | `#C844DC` | 200 68 220 | 252 |
| Purple | `#9A47E2` | 154 71 226 | 2582 |
| Indigo | `#7155FA` | 113 85 250 | 2725 |
| Blue | `#3B62FB` | 59 98 251 | 2727 |
| Cyan | `#1D95E7` | 29 149 231 | 2925 |
| Teal | `#0FB1C0` | 15 177 192 | 7466 |
| Mint | `#0DB595` | 13 181 149 | 3275 |
| Green | `#0BA45D` | 11 164 93 | 3405 |
| Lime | `#5DB41F` | 93 180 31 | 361 |
| Olive | `#A3C400` | 163 196 0 | 390 |
| Yellow | `#F5C700` | 245 199 0 | 7406 |
| Orange | `#FFA213` | 255 162 19 | 1375 |

### Rules for the extended palette
1. **Never use as tones/transparencies.** Solid full-saturation only.
2. **Avoid stereotypes.** Don't use pink to represent women, blue for men, etc.
3. **Semantic mapping** (when applicable): blue = informative, green = positive, orange = notice. But never use red (`#EB1000`) for negative — the brand red is sacred.
4. **One accent per chart.** Most data should be grayscale; reserve color for the single most important data point.
5. **Avoid competitor palettes.** If the local market reads a particular color as a competitor, choose another.

### Functional grays (from the official Adobe master slide theme)
| Hex | Used for |
|---|---|
| `#191919` | Footer text, copyright line, slide number, secondary on-dark labels — **the only acceptable "gray" for footer-style text** |
| `#5F5F5F` | Mid-gray body text alternative |
| `#919191` | Tertiary text, captions on light bg |
| `#C4C4C4` | Disabled / subtle separators / on-dark body |
| `#F5F5F5` | Section background blocks, alternating table rows |

---

## 3. Typography

> "Adobe Clean is for Adobe use only and it's the only typeface we use for all external and internal Adobe communications." (Brand Guidelines p.35)

### The two-font system
Adobe's official theme uses TWO typefaces, not one:
| Font name (in code) | Role |
|---|---|
| `Adobe Clean Display Black` | Major (headlines, slide titles, section dividers). Heaviest weight, optimized for display. |
| `Adobe Clean` | Minor (body, subheads, bullets, footers). Use Regular, Bold, ExtraBold, Black, or SemiLight weights. |

If `Adobe Clean Display Black` is not installed, fall back to `Adobe Clean` Black weight (still proprietary; Adobe employees have both).

### Weights — official set
Only these weights represent the brand:
- Adobe Clean **Black**
- Adobe Clean **ExtraBold**
- Adobe Clean **Bold**
- Adobe Clean **Regular**
- Adobe Clean **SemiLight** (Experience Cloud pull-quotes only)

> Black/ExtraBold/Bold are display weights — use for headlines, section heads, subheads. Body copy = Regular. SemiLight is reserved.

### Hierarchy by weight
| Tier | Weight | Use |
|---|---|---|
| Headline | Adobe Clean Display Black (or Black) | Slide titles, document covers |
| Section headline | Adobe Clean ExtraBold | Sub-titles on covers |
| Subhead | Adobe Clean Bold | In-content sub-headers, column heads |
| Body | Adobe Clean Regular | All running text |
| Pull-quote | Adobe Clean SemiLight | Experience Cloud only |

### Hierarchy by size — formula from Brand Guidelines p.38
Let `C = cap height`. The vertical rhythm between elements is:
- Subhead size = `C/3` of headline
- Body size = `C/4` of headline
- Pull-quote size = `C/4`

### Type alterations
Headlines and subheads only:
- **Tracking: -20** (Adobe XD/Express use -31)
- **Kerning: Optical**
- **Leading:** 90% type size for headlines; 110% for subheads
- **Alignment:** Center or Left
- **Use stylistic alternate lowercase `g`** ("alt g glyph")

> Spacing rule: distance between headline and subhead = ⅓ headline pt size. Distance between subhead and body = 1.5× that figure.

### Capitalization
- **Sentence case** for headlines and subheads (NOT ALL CAPS, NOT Title Case)
- End with period or question mark
- Body copy: standard sentence punctuation

### Color rules for text
- White on dark/red backgrounds
- Black on light backgrounds
- Adobe red (`#EB1000`) for **subheads and category labels only** (limited use)
- Never red for body copy

### Accessibility (WCAG 2.1 Level AAA)
- Body text contrast ratio: ≥ 7:1
- Large text contrast ratio: ≥ 4.5:1
- Large text = ≥ 18pt regular or ≥ 14pt bold

---

## 4. Marks — wordmark and icon

### What they are
| Mark | Attribution |
|---|---|
| **Adobe wordmark** | "Adobe (Stylized)" — primary identifier, has the icon integrated into the "A" |
| **Adobe icon** | "the Adobe icon" — secondary identifier; only when another Adobe identifier is already present (e.g. social avatars) |
| **Limited use corporate logo** | "the Adobe logo" — in-product About screens + building signage only |

> Do NOT recreate the wordmark or icon. Download approved files from Brand Center. Do not alter, crop, recolor (outside approved color combos), or add elements.

### Color rules for marks
| Background | Use |
|---|---|
| Light | Red wordmark `#EB1000` |
| Dark / saturated imagery | White wordmark `#FFFFFF` |
| Warm-toned imagery | White wordmark (for contrast) |
| Merchandise / B&W-only contexts | Black wordmark allowed (secondary usage) |

**Never on imagery:** black wordmark. **Never:** more than one color in the wordmark, gradient fills, drop shadows, bevels, image-fills.

### Clear space
Around the wordmark/icon: leave clear space equal to **½ the icon width** on all sides.

### Minimum size
| Mark | Screen | Print |
|---|---|---|
| Wordmark | 16 px height | 0.75 in / 19 mm width |
| Icon | 16 px height | 0.25 in / 7 mm width |

---

## 5. Layout — the red thread

The left-edge red rule is THE structural brand element. Every layout the Adobe Presentation Style Guide ships includes it.

### PPTX dimensions (extracted from Adobe's master)
```
shape:  rectangle
fill:   #EB1000, solid, no border, no transparency
x:      0.00"
y:      0.00"
w:      0.14"
h:      7.50"  (full slide height)
```

**Exception:** On full-red title slides where the entire background is `#EB1000`, omit the thread (it would be invisible anyway).

### DOCX equivalent
Left paragraph border on:
- The cover/title block paragraphs
- H1 headings

Spec: `style=single, size=48 (= 6pt in eighths-of-a-point), color=EB1000, space=8`

---

## 6. Footer — exact wording and placement

### Wording
```
© [current year] Adobe. All Rights Reserved. Adobe Confidential.
```
(For external materials drop "Adobe Confidential" — confirm with the user.)

### PPTX footer (from Adobe master slide)
| Element | Spec |
|---|---|
| Copyright text | x=10.80", y=7.20", w=1.87", h=0.10" |
| Slide number | x=12.95", y=7.20" |
| Footer placeholder (optional date/context) | x=1.80", y=7.20", w=8.58" |
| Font | Adobe Clean Regular |
| Size | **6pt** (NOT 8pt) |
| Color | **`#191919`** (NOT `#999999`) |
| Alignment | Right |

### DOCX footer
| Element | Spec |
|---|---|
| Wording | `© [year] Adobe. All Rights Reserved. Adobe Confidential.` + tab + page number |
| Font | Adobe Clean Regular, 8pt |
| Color | `#191919` |
| Top border | `single, size=6, color=CCCCCC, space=4` (subtle separator) |

---

## 7. Slide dimensions (PPTX)

Adobe ships in **16:9 widescreen**:
| Spec | Value |
|---|---|
| Width | 13.33" (12,192,000 EMU) |
| Height | 7.50" (6,858,000 EMU) |
| Aspect | 16:9 widescreen |

### Safe content area
Inside the red thread (which occupies x=0 to x=0.14):
- **Left content margin:** 0.67"
- **Right content margin:** ~0.67" (content ends ~12.67")
- **Top margin:** 0.29" (title baseline)
- **Bottom safe area:** 7.10" (above the footer at 7.20")

### Standard placeholder positions (from Adobe master)
| Placeholder | x | y | w | h |
|---|---|---|---|---|
| Title | 0.67" | 0.29" | 12.00" | 1.03" |
| Body / content | 0.67" | 1.46" | 12.00" | 5.46" |
| Footer text | 1.80" | 7.20" | 8.58" | 0.10" |
| Copyright text | 10.80" | 7.20" | 1.87" | 0.10" |
| Slide number | 12.95" | 7.20" | 0.10" | 0.10" |
| Red thread | 0.00" | 0.00" | 0.14" | 7.50" |

---

## 8. Page dimensions (DOCX)

Adobe business documents use **US Letter** with a slightly wider left margin (the template's "left red border" zone).

| Spec | Value (DXA = 1/1440 inch) |
|---|---|
| Width | 12240 (8.5") |
| Height | 15840 (11") |
| Top margin | 1440 (1.0") |
| Right margin | 1440 (1.0") |
| Bottom margin | 1440 (1.0") |
| Left margin | 1584 (1.1") |

Line spacing for body: **1.15 multiple** (276 in twentieths). Body size: **10pt** (per Brand Guidelines p.79 template).

---

## 9. Trademark and copyright attribution

### Always include
1. Copyright line at end of document/deck footer.
2. Trademark attribution paragraph in legal/end matter for any Adobe mark referenced.

### Templates
```
© 2026 Adobe. All rights reserved.
```

```
Adobe, Adobe (Stylized), [other Adobe marks in alphabetical order]
are either registered trademarks or trademarks of Adobe in the
United States and/or other countries.
```

Optional catch-all:
```
All other trademarks are the property of their respective owners.
```

### Never
- Do NOT use ™ or ® bugs on Adobe marks anywhere
- Do NOT write "Adobe Inc." in body copy (legal/contract only)
- Do NOT write "Adobe Systems" or "Adobe Systems Incorporated"
- Do NOT localize Adobe cloud names or product names

---

## 10. Photography & imagery (high level)

Imagery is supplied — do not generate or scrape Adobe-style imagery yourself.

### Style preferences
- Full-spectrum vibrant color via content (not via the brand palette)
- The "lens" (Adobe's circular brand device) only on imagery supplied with it; do not add the lens to other images
- Devices (laptops/phones) shown clutter-free: white/light gray devices on light backgrounds, dark gray on dark backgrounds
- Containers (UI screenshots in simplified frames) only for marketing/feature work, not internal business docs

### Hard rule
> "Images throughout this guide are for inspiration only. Adobe may not have the rights to use them elsewhere. Using any image without permission can result in lawsuits, costly penalties, and very unhappy artists." (Brand Guidelines, contents page)

If the user asks for an Adobe-branded deck with imagery and does not provide images, leave clean image placeholders. Do not pull stock or AI-generated art unless explicitly authorized.
