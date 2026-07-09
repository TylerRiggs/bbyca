"""
Adobe brand constants — single source of truth for the builder scripts.

Values extracted from:
  - Adobe Brand Guidelines (Jan 6, 2025)
  - Adobe Presentation Style Guide Revision 1.7 (Jan 2026) — master slide XML

Do not approximate. Do not substitute. If a value is wrong here, fix it here
rather than in the builder scripts.
"""
from __future__ import annotations
from datetime import datetime

# ---------------------------------------------------------------------------
# CORE PALETTE
# ---------------------------------------------------------------------------

ADOBE_RED = "EB1000"   # hex without #, RGB(235,16,0), PMS 2347 C
BLACK     = "000000"
WHITE     = "FFFFFF"

# Functional grays extracted from the official Adobe master slide theme
GRAY_FOOTER      = "191919"  # footer, copyright, slide number
GRAY_BODY_DARK   = "5F5F5F"  # mid-gray body alternative on light bg
GRAY_BODY_LIGHT  = "919191"  # tertiary text / captions
GRAY_SUBTLE      = "C4C4C4"  # disabled / separators / on-dark body
GRAY_SECTION_BG  = "F5F5F5"  # light section bg, alt table rows
GRAY_BORDER      = "CCCCCC"  # subtle separators (e.g. footer top border)

# ---------------------------------------------------------------------------
# EXTENDED PALETTE — charts/diagrams/accents only. Never as backgrounds for
# narrative content. Never for body text. One accent per chart.
# ---------------------------------------------------------------------------

EXTENDED_PALETTE = {
    "pink":     "FF4885",  # PMS 1915
    "magenta":  "F24CB8",  # PMS 806
    "violet":   "C844DC",  # PMS 252
    "purple":   "9A47E2",  # PMS 2582
    "indigo":   "7155FA",  # PMS 2725
    "blue":     "3B62FB",  # PMS 2727
    "cyan":     "1D95E7",  # PMS 2925
    "teal":     "0FB1C0",  # PMS 7466
    "mint":     "0DB595",  # PMS 3275
    "green":    "0BA45D",  # PMS 3405
    "lime":     "5DB41F",  # PMS 361
    "olive":    "A3C400",  # PMS 390
    "yellow":   "F5C700",  # PMS 7406
    "orange":   "FFA213",  # PMS 1375
}

# Semantic mapping (per Brand Guidelines): use as accents only.
SEMANTIC = {
    "informative": EXTENDED_PALETTE["blue"],
    "positive":    EXTENDED_PALETTE["green"],
    "notice":      EXTENDED_PALETTE["orange"],
    # NOTE: never use ADOBE_RED for "negative"; the brand red is sacred.
    "negative":    EXTENDED_PALETTE["magenta"],
}

# ---------------------------------------------------------------------------
# TYPOGRAPHY
# ---------------------------------------------------------------------------

# IMPORTANT — these names must match the *actual* font families that ship in
# assets/fonts/ (and that Brand Center installs), or every headline silently
# falls back even on machines that have Adobe Clean. The headline weight is the
# "Adobe Clean Black" family (AdobeClean-Black.otf), NOT "Adobe Clean Display
# Black" — the latter is a separate Adobe typeface that is not in this kit.
FONT_DISPLAY = "Adobe Clean Black"  # major: headlines, titles, dividers (900)
FONT_BODY    = "Adobe Clean"         # minor: body, subheads, footers, bullets

# Older specs referenced this name; kept so validators don't flag legacy files.
FONT_DISPLAY_LEGACY = "Adobe Clean Display Black"

# True when a font name already carries its weight in the family (so the
# builders must NOT also apply synthetic bold, which produces faux-bold).
HEAVY_FONTS = {FONT_DISPLAY.lower(), FONT_DISPLAY_LEGACY.lower(),
               "adobe clean black"}

def is_heavy_font(name: str) -> bool:
    return (name or "").lower() in HEAVY_FONTS

# Fallback chain (used only in font specs; we still write the real names into
# the file so they render correctly when the user has them installed).
FONT_FALLBACK_SERIF = "Times New Roman"
FONT_FALLBACK_SANS  = "Calibri"

# Type sizes (points) — extracted from Adobe templates
class PptxSize:
    TITLE_COVER       = 77   # cover/title slide titles (layouts 1-3)
    TITLE_COVER_IMG   = 54   # title slide with image (layouts 4-5)
    SECTION_DIVIDER   = 72   # section break (layouts 6-7)
    CONTENT_TITLE     = 32   # standard content slide title
    LEAD_PARAGRAPH    = 32   # intro paragraph on a content slide
    SUBTITLE_COVER    = 24   # cover subtitle / speaker / date
    QUOTE_LARGE       = 54   # large pull-quote
    COLUMN_HEADER     = 16   # multi-column header (bold)
    BULLET_L1         = 18
    BULLET_L2         = 14
    BULLET_L3         = 12
    BODY_DEFAULT      = 14
    CAPTION           = 9
    FOOTER            = 6    # 6pt — extracted from master, NOT 8pt

class DocxSize:
    """All sizes in half-points (Word's native unit). Multiply pt × 2."""
    COVER_TITLE       = 64   # 32pt
    COVER_TITLE_HERO  = 96   # 48pt — for 1-pager hero
    COVER_SUBTITLE    = 28   # 14pt
    H1                = 48   # 24pt
    H2                = 32   # 16pt
    H3                = 28   # 14pt
    H4                = 24   # 12pt
    BODY              = 20   # 10pt — per Brand Guidelines p.79 template
    BULLET_L0         = 20   # 10pt
    BULLET_L1         = 20
    BULLET_L2         = 18   # 9pt
    CALLOUT           = 24   # 12pt
    HEADER            = 28   # 14pt
    FOOTER            = 16   # 8pt
    TABLE_HEADER      = 20
    TABLE_BODY        = 20

# ---------------------------------------------------------------------------
# DIMENSIONS — PPTX (16:9 widescreen, in inches)
# ---------------------------------------------------------------------------

class Pptx:
    SLIDE_W = 13.33
    SLIDE_H = 7.50

    # Red thread (mandatory on every non-full-red slide)
    THREAD_X = 0.00
    THREAD_Y = 0.00
    THREAD_W = 0.14
    THREAD_H = 7.50

    # Content margins (inside the thread)
    MARGIN_L = 0.67
    MARGIN_R = 0.67
    CONTENT_W = SLIDE_W - MARGIN_L - MARGIN_R  # ~12.00"

    # Standard placeholder positions (from Adobe master slide)
    TITLE_X, TITLE_Y, TITLE_W, TITLE_H = 0.67, 0.29, 12.00, 1.03
    BODY_X,  BODY_Y,  BODY_W,  BODY_H  = 0.67, 1.46, 12.00, 5.46

    # Cover title positions (layouts 1-3)
    COVER_TITLE_X, COVER_TITLE_Y, COVER_TITLE_W, COVER_TITLE_H = 0.67, 1.23, 12.00, 2.61
    COVER_SUB_X,   COVER_SUB_Y,   COVER_SUB_W,   COVER_SUB_H   = 0.67, 3.94, 12.00, 1.81

    # Section divider title (layouts 6-7)
    SECTION_X, SECTION_Y, SECTION_W, SECTION_H = 0.67, 2.73, 12.00, 2.04

    # Footer positions
    FOOTER_TEXT_X, FOOTER_TEXT_Y, FOOTER_TEXT_W, FOOTER_TEXT_H = 1.80, 7.20, 8.58, 0.10
    COPYRIGHT_X,   COPYRIGHT_Y,   COPYRIGHT_W,   COPYRIGHT_H   = 8.80, 7.20, 3.87, 0.16
    SLIDENO_X,     SLIDENO_Y,     SLIDENO_W,     SLIDENO_H     = 12.85, 7.20, 0.40, 0.16

# ---------------------------------------------------------------------------
# DIMENSIONS — DOCX (US Letter, in DXA = 1/1440 inch)
# ---------------------------------------------------------------------------

class Docx:
    PAGE_W = 12240    # 8.5"
    PAGE_H = 15840    # 11"
    MARGIN_TOP    = 1440   # 1.0"
    MARGIN_RIGHT  = 1440
    MARGIN_BOTTOM = 1440
    MARGIN_LEFT   = 1584   # 1.1" — slightly wider for red border

    # Content width inside margins
    CONTENT_W = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT  # 9216 DXA ≈ 6.4"

    # Red border on H1 + cover
    BORDER_RED_SIZE = 48   # eighths-of-a-point = 6pt visual rule
    BORDER_RED_SPACE = 8

    # Body line spacing
    LINE_SPACING = 276     # 1.15 multiple (1 multiple = 240)

# ---------------------------------------------------------------------------
# COPY — exact footer / copyright wording
# ---------------------------------------------------------------------------

def current_year() -> int:
    return datetime.now().year

def footer_text(confidential: bool = True) -> str:
    """Exact wording per Brand Guidelines copyright section."""
    year = current_year()
    if confidential:
        return f"© {year} Adobe. All Rights Reserved. Adobe Confidential."
    return f"© {year} Adobe. All rights reserved."

def trademark_paragraph(marks: list[str] | None = None) -> str:
    """Trademark attribution paragraph for legal/end matter."""
    marks = marks or ["Adobe", "Adobe (Stylized)"]
    marks_str = ", ".join(marks)
    return (f"{marks_str} are either registered trademarks or trademarks of "
            "Adobe in the United States and/or other countries. "
            "All other trademarks are the property of their respective owners.")

# ---------------------------------------------------------------------------
# LAYOUT NAME → official master layout index (1-based)
# Maps friendly names used in the JSON spec to the layout XML number in
# templates/adobe-deck-template.pptx
# ---------------------------------------------------------------------------

LAYOUT_INDEX = {
    # Title slides
    "title-red":       1,
    "title-white":     2,
    "title-dark":      3,
    "title-img-light": 4,
    "title-img-dark":  5,
    # Section dividers
    "section-light":   6,
    "section-dark":    7,
    "section-light-alt": 52,
    "section-dark-alt":  53,
    # Content
    "content":         55,   # Light Airy — primary workhorse
    "content-dark":    56,
    "content-img-half":     10,
    "content-img-third":    11,
    "content-img-half-dark":  30,
    "content-img-third-dark": 31,
    # Columns (light)
    "two-col":         12,
    "three-col":       13,
    "four-col":        18,
    "five-col":        14,
    "two-col-img":     15,
    "three-col-img":   16,
    "four-col-img":    17,
    "five-col-img":    19,
    "two-col-photo":   20,
    "three-col-photo": 22,
    "four-col-photo":  21,
    "five-col-photo":  23,
    # Columns (dark)
    "two-col-dark":    32,
    "three-col-dark":  33,
    "four-col-dark":   34,
    "five-col-dark":   35,
    # Grid
    "grid-1":          24,
    "grid-2x2":        25,
    "grid-3x2":        26,
    "logo-wall":       27,
    "grid-1-dark":     44,
    "grid-2x2-dark":   45,
    "grid-3x2-dark":   46,
    "logo-wall-dark":  47,
    # Specialty
    "quote":           8,
    "quote-dark":      28,
    "agenda":          54,
    "full-image":      48,
    "blank":           49,
    "blank-dark":      50,
    "end-gray":        51,
    "thank-you":       51,
}
