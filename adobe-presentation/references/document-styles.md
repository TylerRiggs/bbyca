# Adobe DOCX Document Styles — Full Specification

Source: Adobe Brand Guidelines p.79 ("Business documents" template) + p.78–80 templates section, validated against the Adobe Clean type hierarchy.

This file documents document patterns. Reference it when constructing the JSON content spec for `scripts/build_doc.py`.

---

## Page setup

| Spec | Value |
|---|---|
| Paper | US Letter (8.5" × 11") |
| Top margin | 1.0" (1440 DXA) |
| Right margin | 1.0" (1440 DXA) |
| Bottom margin | 1.0" (1440 DXA) |
| **Left margin** | **1.1" (1584 DXA)** — slightly wider to accommodate the red left border on H1s |
| Default font | Adobe Clean Regular, 10pt |
| Line spacing | 1.15 multiple (276 in twentieths) |
| Paragraph spacing | 8pt after, 0pt before (except headings) |

---

## Section / paragraph styles

### Cover block (page 1 only)
A solid red shaded block at the top of the first page containing the document title and subtitle.

| Element | Spec |
|---|---|
| Background fill | `#EB1000` |
| Title | Adobe Clean Display Black, **32pt** (size=64 in half-points), white, indent left 360, right 360 |
| Subtitle | Adobe Clean Regular, **14pt** (size=28 in half-points), white |
| Spacing after subtitle | 480 (24pt blank before body) |

**Note on cover sizing:** the Brand Guidelines presentation cover uses 65pt for very short titles; for document covers (Word docs), 32pt is more legible at letter-sheet scale. If the title is ≤4 words and the doc is a hero one-pager, use 48pt.

### Headings

| Style | Font | Size | Weight | Color | Notes |
|---|---|---|---|---|---|
| **Heading 1** | Adobe Clean | **24pt** (size=48) | Black | `#000000` | Red left border: single, size=48 (=6pt), color `EB1000`, space=8 |
| **Heading 2** | Adobe Clean | **16pt** (size=32) | Bold | `#000000` | No border |
| **Heading 3** | Adobe Clean | **14pt** (size=28) | Bold | `#EB1000` | Red is OK here — category-label use |
| **Heading 4** | Adobe Clean | **12pt** (size=24) | Bold | `#191919` | Subtle, for nested sub-sections |

Heading spacing (vertical rhythm):
- H1: 18pt before / 6pt after
- H2: 12pt before / 4pt after
- H3: 9pt before / 3pt after
- H4: 6pt before / 2pt after

### Body
- Font: Adobe Clean Regular
- Size: **10pt** (per Brand Guidelines p.79 template)
- Color: `#000000`
- Line spacing: 1.15 multiple
- After: 8pt (creates the blank line between paragraphs that the template recommends)

### Bullets
> "Try to avoid bullets in your communications. When they are necessary, use the bullet formatting in Microsoft Word." (Brand Guidelines p.79)

Use sparingly. When used:

| Level | Indent | Hanging | Marker | Size |
|---|---|---|---|---|
| 0 | 720 (0.5") | 360 (0.25") | `•` | 10pt |
| 1 | 1080 (0.75") | 360 | `–` | 10pt, color `#5F5F5F` |
| 2 | 1440 (1.0") | 360 | `—` | 9pt, color `#5F5F5F` |

**Two levels max in documents.** If you need three, restructure with H3 sub-headings.

### Call-out / highlight box
For key insights, statistics, customer quotes. Implemented as a 1-cell table:

| Element | Spec |
|---|---|
| Background fill | `#F5F5F5` |
| Left border | single, size=48 (6pt), color `EB1000` |
| Top/bottom/right borders | none |
| Inner margins | top 120 (6pt), bottom 120, left 180 (9pt), right 120 |
| Text | Adobe Clean Bold, 12pt, color `#000000` |
| Width | full content width (typically 9360 DXA = 6.5") |

### Tables (comparison grids, feature tables)
| Element | Spec |
|---|---|
| Width | DXA only (never percentage) |
| Column widths | sum must equal table width |
| Header row | fill `#EB1000`, text white, Adobe Clean Bold, 10pt |
| Body rows | alternate `#FFFFFF` / `#F5F5F5` |
| Cell borders | single, size=1, color `#CCCCCC` |
| Header borders | single, size=1, color `#EB1000` |
| Cell padding | top 80, bottom 80, left 120, right 120 |

### Code / monospace (rare in Adobe content, but supported)
- Font: SF Mono / Consolas / Menlo fallback
- Size: 9pt
- Background: `#F5F5F5`
- No syntax coloring (keep it brand-neutral)

---

## Header and footer

### Header (page 1 and beyond)
A single-line treatment:
| Element | Spec |
|---|---|
| Text | `Adobe` |
| Font | Adobe Clean Bold, 14pt (size=28) |
| Color | `#EB1000` |
| Bottom border | single, size=12 (1.5pt), color `EB1000`, space=4 |
| Spacing after | 80 |

For documents with the red cover block on page 1, the header begins on page 2.

### Footer
Two-element line: legal text (left) + tab + page number (right).
| Element | Spec |
|---|---|
| Legal text | `© [year] Adobe. All Rights Reserved. Adobe Confidential.` |
| Font | Adobe Clean Regular |
| Size | **8pt** (size=16) |
| Color | `#191919` |
| Tab stop | right-aligned at `TabStopPosition.MAX` |
| Page number | as second TextRun, same style |
| Top border | single, size=6, color `#CCCCCC`, space=4 |

---

## Document types — pattern library

| Document type | Cover | Structure | When to use |
|---|---|---|---|
| **One-pager / leave-behind** | Red cover block, single page | Tight H1 sections with red left border, body, optional callout box | Post-meeting summary, account-team handoff, single asset for a deal |
| **Discovery brief** | Red cover, multi-page | Optional TOC, H1 sections per discovery theme, mix of body + bullets + tables | Captures findings from a discovery call/workshop |
| **Advisory guide** | Red cover, multi-page | Long-form prose with H2/H3 subheads, callouts for key tips | Strategic recommendations, how-to playbooks |
| **RFP response** | Minimal header (no red block needed) | Numbered top-level sections, mix of prose + comparison tables | Formal procurement responses |
| **Executive summary** | Red cover block | Short H1 sections, prominent callout boxes for key stats | Read-in for execs preceding a meeting |
| **Memo / letter** | No cover; just header | Address block, body paragraphs, closing | Internal communications |
| **Customer case study** | Red cover with customer name | H1 = "Challenge / Solution / Result" sections | Sales enablement |
| **Battle card** | No cover | 2-column layout via table; "Their pitch / Our response" rows | Sales enablement, 1–2 pages |

---

## Document JSON spec shape

```json
{
  "title": "Document title",
  "subtitle": "Optional subtitle on the cover",
  "doc_type": "one-pager",        // controls cover treatment
  "header_text": "Adobe",          // default: "Adobe"
  "confidential": true,            // controls footer wording
  "sections": [
    {
      "type": "h1",
      "text": "First section"
    },
    {
      "type": "body",
      "text": "Paragraph of running prose..."
    },
    {
      "type": "h2",
      "text": "Sub-section"
    },
    {
      "type": "bullets",
      "items": [
        {"text": "Top-level bullet", "level": 0},
        {"text": "Sub-bullet", "level": 1}
      ]
    },
    {
      "type": "callout",
      "text": "Key insight or statistic — high-contrast."
    },
    {
      "type": "table",
      "header": ["Column A", "Column B", "Column C"],
      "rows": [
        ["a1", "b1", "c1"],
        ["a2", "b2", "c2"]
      ]
    }
  ]
}
```

See `scripts/build_doc.py` for the authoritative schema and `examples/discovery-one-pager/input.json` for a worked example.

---

## Font substitution reminder

Adobe Clean is proprietary and not bundled with the .docx. Always include this note when delivering:

> **Open in Word.** If Adobe Clean is installed (Brand Center), it will render automatically. If your fonts have substituted, select all (⌘/Ctrl+A), set the font to Adobe Clean (or its closest installed substitute — Calibri Bold for headlines / Calibri for body), then File → Export → PDF.

Never write the substitute font name into the file itself. Always specify `Adobe Clean` / `Adobe Clean Display Black` so the file renders correctly on systems with those fonts installed.
