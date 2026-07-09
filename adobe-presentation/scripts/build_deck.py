#!/usr/bin/env python3
"""
Adobe-branded PowerPoint builder.

Usage:
    python scripts/build_deck.py path/to/spec.json output.pptx

Builds an on-brand deck from scratch: every slide is drawn at the exact Adobe
master coordinates defined in brand.py (red thread, footers, placeholder
positions), the approved wordmark is placed on covers/closings, and Adobe Clean
is embedded into the output. No template file is required — the builder starts
from a blank widescreen presentation, so there is no dependency on the (large,
reference-only) templates/ folder.

JSON SCHEMA
-----------
{
  "title":     "Deck title (used for file metadata)",
  "subtitle":  "Optional",
  "author":    "Optional — for file metadata",
  "confidential": true,                     // default true; controls footer
  "slides": [
    { "layout": "title-red",
      "title": "Personalize at scale.",
      "subtitle": "How leading brands use Adobe Experience Cloud" },

    { "layout": "agenda",
      "title": "Agenda",
      "rows": [
        ["1.", "Where you are today",    "5 min"],
        ["2.", "What's possible",         "15 min"],
        ["3.", "How Adobe helps",         "20 min"],
        ["4.", "Next steps",              "5 min"]
      ] },

    { "layout": "section-light",
      "title": "Where you are today" },

    { "layout": "content",
      "title": "The four signals we hear most.",
      "bullets": [
        { "text": "Personalization stalled at landing-page level.",  "level": 0 },
        { "text": "Cross-channel orchestration is brittle.",          "level": 0 },
        { "text": "Data is rich, decisioning is poor.",               "level": 0 },
        { "text": "AI investments lack measurable ROI.",              "level": 0 }
      ] },

    { "layout": "two-col",
      "title": "Before / After",
      "left":  { "header": "Before",
                 "body":   "Manual segmentation, batch campaigns, weeks to launch." },
      "right": { "header": "After",
                 "body":   "Real-time segments, AI-suggested journeys, hours to launch." } },

    { "layout": "quote",
      "quote": "Adobe gave us a 7x lift in conversion in the first quarter.",
      "attribution": "VP, Digital — Acme Co." },

    { "layout": "thank-you",
      "title": "Thank you.",
      "contact": "First Last  |  first.last@adobe.com" }
  ]
}

LAYOUT NAMES (see scripts/brand.py LAYOUT_INDEX for the full mapping):
  title-red, title-white, title-dark, title-img-light, title-img-dark
  section-light, section-dark, section-light-alt, section-dark-alt
  content, content-dark, content-img-half, content-img-third
  two-col, three-col, four-col, five-col
  two-col-img, three-col-img, four-col-img, five-col-img
  quote, quote-dark, agenda, thank-you, end-gray, blank
  grid-1, grid-2x2, grid-3x2, logo-wall, full-image

STRUCTURED-VISUAL LAYOUTS (prefer these over 'content' bullets whenever the
content is structured — pricing, metrics, options, sequences):
  table / pricing-table   styled table: black header band, shaded rows,
                          red total band, highlight callout, notice strip
  stat-row / stats        2-4 KPI cards with hero numbers
  cards                   2-6 feature/pillar cards in a grid
  comparison              two boxed panels (before/after, option A/B)
  process / timeline      3-6 numbered steps on a connector line
All of them accept optional "kicker" (red eyebrow line under the title) and
"notice" (bottom caveat strip). Example — the slide a designer would build
for a pricing option:

    { "layout": "table",
      "title": "Option 1: Bundled package.",
      "kicker": "LLM Optimizer + Semrush AIO + Brand Concierge",
      "columns": ["Product / Service", "Year 1", "Year 2", "Year 3"],
      "rows": [["LLM Optimizer + Semrush AIO", "$95,000", "$95,000", "$95,000"],
               ["Brand Concierge", "$55,000", "$55,000", "$55,000"]],
      "total_row": ["Total annual investment", "$150,000", "$150,000", "$150,000"],
      "highlight": {"label": "3-year total investment", "value": "$450,000",
                    "note": "Consistent pricing across all contract years."},
      "notice": "Pricing is contingent upon contract execution by July 30, 2026." }
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

import brand as B

# Path to the licensed Adobe wordmark/icon PNGs (dropped in by the user — see
# assets/README.md). If a file is missing, the slide falls back to text-only.
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "logos"
WORDMARK_RED   = ASSETS_DIR / "Adobe_Wordmark_RGB_Red.png"
WORDMARK_WHITE = ASSETS_DIR / "Adobe_Wordmark_RGB_White.png"
ICON_RED       = ASSETS_DIR / "Adobe_icon_RGB_red.png"
ICON_WHITE     = ASSETS_DIR / "Adobe_icon_RGB_white.png"

# Wordmark image aspect ratio (width / height). PNG: 3151x763 ≈ 4.13.
WORDMARK_ASPECT = 4.13


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hex_rgb(hex_str: str) -> RGBColor:
    """'EB1000' -> RGBColor."""
    return RGBColor.from_string(hex_str.lstrip("#"))


def flat(shape):
    """Strip the theme <p:style> reference from an autoshape. The theme's
    effectRef carries a default drop shadow that some renderers (LibreOffice)
    apply even when an empty <a:effectLst/> is present. Brand rule: flat
    color only — no shadows, bevels, or gradients — so remove the reference.
    """
    el = shape._element.find(qn("p:style"))
    if el is not None:
        shape._element.remove(el)
    return shape


def add_red_thread(slide) -> None:
    """The mandatory left-edge brand element. x=0, y=0, w=0.14", h=7.5"."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(B.Pptx.THREAD_X),
        Inches(B.Pptx.THREAD_Y),
        Inches(B.Pptx.THREAD_W),
        Inches(B.Pptx.THREAD_H),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_rgb(B.ADOBE_RED)
    shape.line.fill.background()  # no border
    shape.shadow.inherit = False  # no shadow
    flat(shape)
    return shape


def add_text_box(slide, text: str, x: float, y: float, w: float, h: float,
                 *, font_name: str = B.FONT_BODY, size_pt: int = 14,
                 bold: bool = False, color_hex: str = B.BLACK,
                 align: str = "left", anchor: str = "top") -> None:
    """Place a styled text box at absolute inch coordinates."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = {
        "top":    MSO_ANCHOR.TOP,
        "middle": MSO_ANCHOR.MIDDLE,
        "bottom": MSO_ANCHOR.BOTTOM,
    }[anchor]

    p = tf.paragraphs[0]
    p.alignment = {
        "left":   PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right":  PP_ALIGN.RIGHT,
    }[align]
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    # Heavy families (Adobe Clean Black) already carry their weight — applying
    # synthetic bold on top produces off-brand faux-bold.
    run.font.bold = bold and not B.is_heavy_font(font_name)
    run.font.color.rgb = hex_rgb(color_hex)
    return tb


def add_footer(slide, slide_no: int, total: int, *, confidential: bool = True,
               on_dark: bool = False) -> None:
    """Add the standard Adobe footer: copyright + slide number."""
    color = B.WHITE if on_dark else B.GRAY_FOOTER
    add_text_box(
        slide,
        B.footer_text(confidential=confidential),
        B.Pptx.COPYRIGHT_X, B.Pptx.COPYRIGHT_Y, B.Pptx.COPYRIGHT_W, B.Pptx.COPYRIGHT_H,
        font_name=B.FONT_BODY, size_pt=B.PptxSize.FOOTER,
        color_hex=color, align="right",
    )
    add_text_box(
        slide,
        f"{slide_no} / {total}",
        B.Pptx.SLIDENO_X, B.Pptx.SLIDENO_Y, B.Pptx.SLIDENO_W, B.Pptx.SLIDENO_H,
        font_name=B.FONT_BODY, size_pt=B.PptxSize.FOOTER,
        color_hex=color, align="right",
    )


def add_wordmark(slide, *, on_dark: bool, width_in: float = 1.30,
                 x_in: float | None = None, y_in: float | None = None) -> None:
    """Insert the licensed Adobe wordmark PNG at lower-left.

    Args:
        on_dark: True for dark or red backgrounds → use white wordmark.
                 False for light backgrounds → use red wordmark.
        width_in: target wordmark width in inches. Height is auto from aspect.
        x_in, y_in: override placement. Defaults to lower-left clear of the
                    red thread (x=0.67) and just above the footer (y=6.80 for
                    a 0.30" tall mark — gives ~0.10" breathing room).
    """
    path = WORDMARK_WHITE if on_dark else WORDMARK_RED
    if not path.exists():
        return  # gracefully skip — text covers identity in fallback
    h_in = width_in / WORDMARK_ASPECT
    if x_in is None:
        x_in = B.Pptx.MARGIN_L  # 0.67 — clears the red thread
    if y_in is None:
        # Place just above the footer area (footer text at y=7.20)
        y_in = 7.10 - h_in
    slide.shapes.add_picture(str(path), Inches(x_in), Inches(y_in),
                             width=Inches(width_in), height=Inches(h_in))


def set_solid_bg(slide, hex_color: str) -> None:
    """Set the slide background to a solid color via a full-bleed rectangle
    placed before all other shapes."""
    bg = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0), Inches(0),
        Inches(B.Pptx.SLIDE_W), Inches(B.Pptx.SLIDE_H),
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = hex_rgb(hex_color)
    bg.line.fill.background()
    # Move to back
    spTree = bg._element.getparent()
    spTree.remove(bg._element)
    spTree.insert(2, bg._element)
    return bg


def add_rect(slide, x: float, y: float, w: float, h: float, fill_hex: str,
             *, line_hex: str | None = None, line_w_pt: float = 0.75):
    """Flat rectangle — the building block for bands, cards, and accents."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_rgb(fill_hex)
    if line_hex:
        shape.line.color.rgb = hex_rgb(line_hex)
        shape.line.width = Pt(line_w_pt)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    flat(shape)
    return shape


def add_kicker(slide, text: str, *, y: float = 1.10,
               color_hex: str = B.ADOBE_RED) -> None:
    """Category/eyebrow line under the slide title (red bold, sentence case)."""
    add_text_box(
        slide, text,
        B.Pptx.MARGIN_L, y, B.Pptx.CONTENT_W, 0.35,
        font_name=B.FONT_BODY, size_pt=14, bold=True,
        color_hex=color_hex, align="left",
    )


def add_notice(slide, text: str, *, accent_hex: str | None = None,
               y: float | None = None) -> None:
    """Bottom notice strip — light gray band with a semantic accent bar.
    Use for deadlines, caveats, legal conditions ('Pricing contingent upon…')."""
    accent = (accent_hex or B.SEMANTIC["notice"]).lstrip("#")
    h = 0.44
    if y is None:
        y = 6.58
    add_rect(slide, B.Pptx.MARGIN_L, y, B.Pptx.CONTENT_W, h, B.GRAY_SECTION_BG)
    add_rect(slide, B.Pptx.MARGIN_L, y, 0.07, h, accent)
    add_text_box(
        slide, text,
        B.Pptx.MARGIN_L + 0.25, y, B.Pptx.CONTENT_W - 0.45, h,
        font_name=B.FONT_BODY, size_pt=11, bold=True,
        color_hex=B.BLACK, align="left", anchor="middle",
    )


_NUMERIC_CELL = re.compile(
    r"^[\s\d$€£¥%+,.\-–—/xX×:]*\d[\s\d$€£¥%+,.\-–—/xX×:]*$")


def _guess_align(rows: list, col_idx: int) -> str:
    """Right-align columns that are mostly numeric ($, %, counts)."""
    cells = [str(r[col_idx]) for r in rows
             if col_idx < len(r) and str(r[col_idx]).strip()]
    if not cells:
        return "left"
    numeric = sum(1 for c in cells if _NUMERIC_CELL.match(c.strip()))
    return "right" if numeric >= max(1, len(cells) // 2 + 1) else "left"


# ---------------------------------------------------------------------------
# Slide builders — one per layout family
# ---------------------------------------------------------------------------

def _blank_slide(prs: Presentation):
    """Use the first blank layout (we build everything manually for control)."""
    return prs.slides.add_slide(prs.slide_layouts[6])  # blank layout in default master


def build_title_red(prs, spec):
    s = _blank_slide(prs)
    set_solid_bg(s, B.ADOBE_RED)
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.COVER_TITLE_X, B.Pptx.COVER_TITLE_Y, B.Pptx.COVER_TITLE_W, B.Pptx.COVER_TITLE_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.TITLE_COVER,
        bold=True, color_hex=B.WHITE, align="left", anchor="bottom",
    )
    if spec.get("subtitle"):
        add_text_box(
            s, spec["subtitle"],
            B.Pptx.COVER_SUB_X, B.Pptx.COVER_SUB_Y, B.Pptx.COVER_SUB_W, B.Pptx.COVER_SUB_H,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.SUBTITLE_COVER,
            color_hex=B.WHITE, align="left", anchor="top",
        )
    add_wordmark(s, on_dark=True)
    return s


def build_title_light(prs, spec, *, dark: bool = False):
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
        title_color = B.WHITE
        sub_color = B.GRAY_SUBTLE
    else:
        title_color = B.BLACK
        sub_color = B.GRAY_BODY_DARK
    add_red_thread(s)
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.COVER_TITLE_X, B.Pptx.COVER_TITLE_Y, B.Pptx.COVER_TITLE_W, B.Pptx.COVER_TITLE_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.TITLE_COVER,
        bold=True, color_hex=title_color, align="left", anchor="bottom",
    )
    if spec.get("subtitle"):
        add_text_box(
            s, spec["subtitle"],
            B.Pptx.COVER_SUB_X, B.Pptx.COVER_SUB_Y, B.Pptx.COVER_SUB_W, B.Pptx.COVER_SUB_H,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.SUBTITLE_COVER,
            color_hex=sub_color, align="left", anchor="top",
        )
    add_wordmark(s, on_dark=dark)
    return s


def build_section(prs, spec, *, dark: bool = False):
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
        color = B.WHITE
    else:
        color = B.BLACK
    add_red_thread(s)
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.SECTION_X, B.Pptx.SECTION_Y, B.Pptx.SECTION_W, B.Pptx.SECTION_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.SECTION_DIVIDER,
        bold=True, color_hex=color, align="left", anchor="middle",
    )
    return s


def build_content(prs, spec, *, dark: bool = False):
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
        title_color = B.WHITE
        body_color = B.WHITE
    else:
        title_color = B.BLACK
        body_color = B.BLACK
    add_red_thread(s)

    start_y = _title_kicker_top(s, spec, dark=dark)

    if spec.get("lead"):
        add_text_box(
            s, spec["lead"],
            B.Pptx.BODY_X, start_y, B.Pptx.BODY_W, 0.9,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.LEAD_PARAGRAPH,
            color_hex=body_color, align="left",
        )
        body_top = start_y + 1.1
    else:
        body_top = start_y
    body_h = _CONTENT_BOTTOM - _notice_reserve(spec) - body_top

    bullets = spec.get("bullets") or []
    if bullets:
        tb = s.shapes.add_textbox(
            Inches(B.Pptx.BODY_X), Inches(body_top),
            Inches(B.Pptx.BODY_W), Inches(body_h),
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        for i, b in enumerate(bullets):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            lvl = int(b.get("level", 0))
            p.level = min(max(lvl, 0), 2)
            size = {0: B.PptxSize.BULLET_L1, 1: B.PptxSize.BULLET_L2,
                    2: B.PptxSize.BULLET_L3}[p.level]
            marker = {0: "•  ", 1: "–  ", 2: "—  "}[p.level]
            run = p.add_run()
            run.text = marker + b["text"]
            run.font.name = B.FONT_BODY
            run.font.size = Pt(size)
            run.font.color.rgb = hex_rgb(body_color)
            p.alignment = PP_ALIGN.LEFT
    _maybe_notice(s, spec)
    return s


def build_quote(prs, spec, *, dark: bool = False):
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
        color = B.WHITE
    else:
        color = B.BLACK
    add_red_thread(s)
    add_text_box(
        s, f"“{spec.get('quote', '')}”",
        B.Pptx.BODY_X, 1.5, B.Pptx.BODY_W, 4.0,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.QUOTE_LARGE,
        bold=True, color_hex=color, align="left", anchor="middle",
    )
    if spec.get("attribution"):
        add_text_box(
            s, "— " + spec["attribution"],
            B.Pptx.BODY_X, 6.0, B.Pptx.BODY_W, 0.4,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.SUBTITLE_COVER,
            color_hex=color, align="left",
        )
    return s


def build_agenda(prs, spec):
    s = _blank_slide(prs)
    add_red_thread(s)
    add_text_box(
        s, spec.get("title", "Agenda"),
        B.Pptx.TITLE_X, B.Pptx.TITLE_Y, B.Pptx.TITLE_W, B.Pptx.TITLE_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.CONTENT_TITLE,
        bold=True, color_hex=B.BLACK, align="left",
    )
    rows = spec.get("rows") or []
    if not rows:
        return s
    ncols = max(len(r) for r in rows)
    table_top = 1.72
    table_h = 4.93
    row_h = table_h / max(len(rows), 1)
    col_w = B.Pptx.BODY_W / ncols
    for r_idx, row in enumerate(rows):
        if r_idx % 2 == 1:
            # alt row background
            bg = s.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(B.Pptx.BODY_X), Inches(table_top + r_idx * row_h),
                Inches(B.Pptx.BODY_W), Inches(row_h),
            )
            bg.fill.solid()
            bg.fill.fore_color.rgb = hex_rgb(B.GRAY_SECTION_BG)
            bg.line.fill.background()
        for c_idx, cell in enumerate(row):
            add_text_box(
                s, str(cell),
                B.Pptx.BODY_X + c_idx * col_w + 0.15,
                table_top + r_idx * row_h + 0.10,
                col_w - 0.2, row_h - 0.2,
                font_name=B.FONT_BODY,
                size_pt=14 if r_idx == 0 else 12,
                bold=(r_idx == 0),
                color_hex=B.BLACK, align="left", anchor="middle",
            )
    return s


def build_two_col(prs, spec, *, dark: bool = False):
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
        color = B.WHITE
    else:
        color = B.BLACK
    add_red_thread(s)
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.TITLE_X, B.Pptx.TITLE_Y, B.Pptx.TITLE_W, B.Pptx.TITLE_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.CONTENT_TITLE,
        bold=True, color_hex=color, align="left",
    )
    col_w = B.Pptx.BODY_W / 2 - 0.2
    for i, key in enumerate(("left", "right")):
        col = spec.get(key, {})
        col_x = B.Pptx.BODY_X + i * (B.Pptx.BODY_W / 2 + 0.1)
        add_text_box(
            s, col.get("header", ""),
            col_x, B.Pptx.BODY_Y, col_w, 0.5,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.COLUMN_HEADER,
            bold=True, color_hex=B.ADOBE_RED if not dark else B.WHITE, align="left",
        )
        add_text_box(
            s, col.get("body", ""),
            col_x, B.Pptx.BODY_Y + 0.6, col_w, B.Pptx.BODY_H - 0.6,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.BULLET_L1,
            color_hex=color, align="left",
        )
    return s


def build_n_col(prs, spec, n: int, *, dark: bool = False):
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
        color = B.WHITE
    else:
        color = B.BLACK
    add_red_thread(s)
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.TITLE_X, B.Pptx.TITLE_Y, B.Pptx.TITLE_W, B.Pptx.TITLE_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.CONTENT_TITLE,
        bold=True, color_hex=color, align="left",
    )
    cols = spec.get("columns") or []
    gap = 0.2
    col_w = (B.Pptx.BODY_W - gap * (n - 1)) / n
    body_size = {2: 16, 3: 14, 4: 12, 5: 11}.get(n, 12)
    for i, col in enumerate(cols[:n]):
        col_x = B.Pptx.BODY_X + i * (col_w + gap)
        add_text_box(
            s, col.get("header", ""),
            col_x, B.Pptx.BODY_Y, col_w, 0.5,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.COLUMN_HEADER,
            bold=True, color_hex=B.ADOBE_RED if not dark else B.WHITE, align="left",
        )
        add_text_box(
            s, col.get("body", ""),
            col_x, B.Pptx.BODY_Y + 0.6, col_w, B.Pptx.BODY_H - 0.6,
            font_name=B.FONT_BODY, size_pt=body_size,
            color_hex=color, align="left",
        )
    return s


def build_thank_you(prs, spec):
    s = _blank_slide(prs)
    set_solid_bg(s, B.GRAY_SECTION_BG)
    add_red_thread(s)
    add_text_box(
        s, spec.get("title", "Thank you."),
        B.Pptx.SECTION_X, B.Pptx.SECTION_Y, B.Pptx.SECTION_W, B.Pptx.SECTION_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.SECTION_DIVIDER,
        bold=True, color_hex=B.BLACK, align="left", anchor="middle",
    )
    if spec.get("contact"):
        add_text_box(
            s, spec["contact"],
            B.Pptx.SECTION_X, B.Pptx.SECTION_Y + B.Pptx.SECTION_H + 0.2,
            B.Pptx.SECTION_W, 0.5,
            font_name=B.FONT_BODY, size_pt=B.PptxSize.SUBTITLE_COVER,
            color_hex=B.GRAY_BODY_DARK, align="left",
        )
    add_wordmark(s, on_dark=False)
    return s


# ---------------------------------------------------------------------------
# Structured-visual layouts — tables, stat cards, card grids, comparisons,
# process flows. These are the "best of both worlds" layouts: the graphical
# structure a designer would build (header bands, shaded rows, callout boxes,
# accent bars) rendered strictly in Adobe brand tokens. Use them whenever the
# content is structured — pricing, metrics, options, sequences — instead of
# flattening it into bullets.
# ---------------------------------------------------------------------------

_CONTENT_BOTTOM = 7.02   # keep visual blocks clear of the 7.20 footer line


def _resolve_accent(name_or_hex: str | None, default: str = B.ADOBE_RED) -> str:
    """Accept an extended-palette name ('blue') or a hex string."""
    if not name_or_hex:
        return default
    key = str(name_or_hex).lower().lstrip("#")
    return B.EXTENDED_PALETTE.get(key, key if len(key) == 6 else default)


def _title_kicker_top(slide, spec, *, dark: bool = False) -> float:
    """Render title (+ optional kicker) and return the y where content starts."""
    color = B.WHITE if dark else B.BLACK
    add_text_box(
        slide, spec.get("title", ""),
        B.Pptx.TITLE_X, B.Pptx.TITLE_Y, B.Pptx.TITLE_W, B.Pptx.TITLE_H,
        font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.CONTENT_TITLE,
        bold=True, color_hex=color, align="left", anchor="top",
    )
    if spec.get("kicker"):
        add_kicker(slide, spec["kicker"],
                   color_hex=B.ADOBE_RED if not dark else B.WHITE)
        return 1.58
    return 1.46


def _notice_reserve(spec) -> float:
    """Vertical space to reserve at the bottom when a notice strip is present."""
    return 0.62 if spec.get("notice") else 0.0


def _maybe_notice(slide, spec) -> None:
    if spec.get("notice"):
        add_notice(slide, spec["notice"],
                   accent_hex=spec.get("notice_accent"),
                   y=_CONTENT_BOTTOM - 0.44)


def build_table_slide(prs, spec):
    """Styled data table: black header band (white bold), alternating row
    shading, optional red total band, optional highlight callout box and
    notice strip. The layout for pricing, plans, and any row/column data.

    Spec:
      title: str            kicker: str (optional eyebrow under the title)
      columns: [str]        header labels
      rows: [[cell]]        body rows
      total_row: [cell]     optional — rendered as a red band, white bold
      col_widths: [float]   optional relative widths (default: first col 2.4x)
      col_align: [l|c|r]    optional per-column ('left'/'center'/'right');
                            numeric columns auto-right-align when omitted
      highlight: {label, value, note}   optional callout box under the table
      notice: str           optional bottom strip (deadline/caveat)
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    top = _title_kicker_top(s, spec)

    columns = [str(c) for c in spec.get("columns", [])]
    rows = spec.get("rows", [])
    total_row = spec.get("total_row")
    ncols = max([len(columns)] + [len(r) for r in rows] +
                ([len(total_row)] if total_row else [0]))
    if ncols == 0:
        return s

    # Column geometry — first column wide for labels unless specified
    rel = spec.get("col_widths") or [2.4] + [1.0] * (ncols - 1)
    rel = (list(rel) + [1.0] * ncols)[:ncols]
    unit = B.Pptx.CONTENT_W / sum(rel)
    col_w = [r * unit for r in rel]
    col_x = [B.Pptx.MARGIN_L + sum(col_w[:i]) for i in range(ncols)]

    align = spec.get("col_align") or [
        "left" if i == 0 else _guess_align(rows, i) for i in range(ncols)]
    align = (list(align) + ["left"] * ncols)[:ncols]
    align = [{"l": "left", "c": "center", "r": "right"}.get(a, a) for a in align]

    # Row geometry — fit within the content area
    bottom = _CONTENT_BOTTOM - _notice_reserve(spec)
    highlight = spec.get("highlight")
    if highlight:
        bottom -= 1.25   # highlight box (1.05) + gap
    n_body = len(rows)
    header_h = 0.52
    total_h = 0.56 if total_row else 0.0
    avail = bottom - top - header_h - total_h
    row_h = max(0.34, min(0.60, avail / max(n_body, 1)))

    pad = 0.16
    body_size = 13 if row_h >= 0.44 else 11

    def _cell(text, x, y, w, h, *, size, bold, color, a):
        add_text_box(s, str(text), x + pad, y, w - 2 * pad, h,
                     font_name=B.FONT_BODY, size_pt=size, bold=bold,
                     color_hex=color, align=a, anchor="middle")

    # Header band — black, white bold text
    add_rect(s, B.Pptx.MARGIN_L, top, B.Pptx.CONTENT_W, header_h, B.BLACK)
    for i, cname in enumerate(columns):
        _cell(cname, col_x[i], top, col_w[i], header_h,
              size=13, bold=True, color=B.WHITE, a=align[i])

    # Body rows — alternating white / #F5F5F5
    y = top + header_h
    for r_idx, row in enumerate(rows):
        if r_idx % 2 == 0:
            add_rect(s, B.Pptx.MARGIN_L, y, B.Pptx.CONTENT_W, row_h,
                     B.GRAY_SECTION_BG)
        for c_idx in range(min(len(row), ncols)):
            _cell(row[c_idx], col_x[c_idx], y, col_w[c_idx], row_h,
                  size=body_size, bold=(c_idx == 0),
                  color=B.BLACK, a=align[c_idx])
        y += row_h

    # Total band — Adobe red, white bold
    if total_row:
        add_rect(s, B.Pptx.MARGIN_L, y, B.Pptx.CONTENT_W, total_h, B.ADOBE_RED)
        for c_idx in range(min(len(total_row), ncols)):
            _cell(total_row[c_idx], col_x[c_idx], y, col_w[c_idx], total_h,
                  size=14, bold=True, color=B.WHITE, a=align[c_idx])
        y += total_h

    # Highlight callout — gray box, red accent bar, hero number
    if highlight:
        hy = y + 0.20
        hh = 1.05
        add_rect(s, B.Pptx.MARGIN_L, hy, B.Pptx.CONTENT_W, hh, B.GRAY_SECTION_BG)
        add_rect(s, B.Pptx.MARGIN_L, hy, 0.07, hh, B.ADOBE_RED)
        add_text_box(s, highlight.get("label", ""),
                     B.Pptx.MARGIN_L + 0.30, hy + 0.12, 5.6, 0.30,
                     font_name=B.FONT_BODY, size_pt=12, bold=True,
                     color_hex=B.GRAY_BODY_DARK, align="left")
        add_text_box(s, highlight.get("value", ""),
                     B.Pptx.MARGIN_L + 0.30, hy + 0.38, 5.6, 0.60,
                     font_name=B.FONT_DISPLAY, size_pt=30, bold=True,
                     color_hex=B.BLACK, align="left", anchor="middle")
        if highlight.get("note"):
            add_text_box(s, highlight["note"],
                         B.Pptx.MARGIN_L + 6.10, hy, B.Pptx.CONTENT_W - 6.40, hh,
                         font_name=B.FONT_BODY, size_pt=12,
                         color_hex=B.GRAY_BODY_DARK, align="left",
                         anchor="middle")

    _maybe_notice(s, spec)
    return s


def build_stat_row(prs, spec):
    """2–4 KPI stat cards: hero number in Adobe Clean Black on a light gray
    card with a red top accent bar. For metrics, outcomes, proof points.

    Spec:
      title, kicker, notice: as build_table_slide
      stats: [{value: "$450K", label: "3-year total", note: "...",
               accent: "red" | extended-palette name | hex (optional)}]
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    top = _title_kicker_top(s, spec)

    stats = spec.get("stats", [])[:4]
    n = max(len(stats), 1)
    gap = 0.28
    card_w = (B.Pptx.CONTENT_W - gap * (n - 1)) / n
    card_h = min(2.9, _CONTENT_BOTTOM - _notice_reserve(spec) - top - 0.2)
    cy = top + 0.15

    for i, st in enumerate(stats):
        cx = B.Pptx.MARGIN_L + i * (card_w + gap)
        accent = _resolve_accent(st.get("accent"))
        add_rect(s, cx, cy, card_w, card_h, B.GRAY_SECTION_BG)
        add_rect(s, cx, cy, card_w, 0.08, accent)
        add_text_box(s, st.get("value", ""),
                     cx + 0.25, cy + 0.35, card_w - 0.5, 0.95,
                     font_name=B.FONT_DISPLAY, size_pt=40 if n <= 3 else 32,
                     bold=True, color_hex=B.BLACK, align="left", anchor="middle")
        add_text_box(s, st.get("label", ""),
                     cx + 0.25, cy + 1.40, card_w - 0.5, 0.40,
                     font_name=B.FONT_BODY, size_pt=14, bold=True,
                     color_hex=B.BLACK, align="left")
        if st.get("note"):
            add_text_box(s, st["note"],
                         cx + 0.25, cy + 1.82, card_w - 0.5, card_h - 1.95,
                         font_name=B.FONT_BODY, size_pt=11,
                         color_hex=B.GRAY_BODY_DARK, align="left")

    _maybe_notice(s, spec)
    return s


def build_cards(prs, spec):
    """2–6 feature/pillar cards in a grid (≤3 per row). Light gray card,
    accent top bar, bold header, body text or bullets.

    Spec:
      title, kicker, notice: as build_table_slide
      cards: [{header: str, body: str | bullets: [str],
               accent: extended-palette name | hex (optional, default red)}]
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    top = _title_kicker_top(s, spec)

    cards = spec.get("cards", [])[:6]
    n = len(cards)
    if n == 0:
        return s
    per_row = n if n <= 3 else (2 if n == 4 else 3)
    n_rows = (n + per_row - 1) // per_row
    gap = 0.25
    card_w = (B.Pptx.CONTENT_W - gap * (per_row - 1)) / per_row
    avail_h = _CONTENT_BOTTOM - _notice_reserve(spec) - top - 0.15
    card_h = (avail_h - gap * (n_rows - 1)) / n_rows

    for i, card in enumerate(cards):
        r, c = divmod(i, per_row)
        cx = B.Pptx.MARGIN_L + c * (card_w + gap)
        cy = top + 0.15 + r * (card_h + gap)
        accent = _resolve_accent(card.get("accent"))
        add_rect(s, cx, cy, card_w, card_h, B.GRAY_SECTION_BG)
        add_rect(s, cx, cy, card_w, 0.07, accent)
        add_text_box(s, card.get("header", ""),
                     cx + 0.25, cy + 0.25, card_w - 0.5, 0.45,
                     font_name=B.FONT_BODY, size_pt=15, bold=True,
                     color_hex=B.BLACK, align="left")
        body_y = cy + 0.78
        body_h = card_h - 0.95
        if card.get("bullets"):
            _add_bulleted_textbox(s, card["bullets"],
                                  cx + 0.25, body_y, card_w - 0.5, body_h,
                                  size_pt=11, color_hex=B.BLACK)
        elif card.get("body"):
            add_text_box(s, card["body"],
                         cx + 0.25, body_y, card_w - 0.5, body_h,
                         font_name=B.FONT_BODY, size_pt=11.5,
                         color_hex=B.GRAY_BODY_DARK, align="left")

    _maybe_notice(s, spec)
    return s


def build_comparison(prs, spec):
    """Two boxed panels with colored header bands — before/after, option A/B,
    us/them. Left band defaults to near-black, right band to Adobe red (the
    'after'/recommended side).

    Spec:
      title, kicker, notice: as build_table_slide
      left / right: {header: str, header_color: hex (optional),
                     body: str | bullets: [str]}
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    top = _title_kicker_top(s, spec)

    gap = 0.30
    panel_w = (B.Pptx.CONTENT_W - gap) / 2
    panel_h = _CONTENT_BOTTOM - _notice_reserve(spec) - top - 0.15
    band_h = 0.52
    defaults = {"left": B.GRAY_FOOTER, "right": B.ADOBE_RED}

    for i, key in enumerate(("left", "right")):
        panel = spec.get(key, {})
        px = B.Pptx.MARGIN_L + i * (panel_w + gap)
        py = top + 0.15
        band = _resolve_accent(panel.get("header_color"), defaults[key])
        add_rect(s, px, py, panel_w, panel_h, B.GRAY_SECTION_BG)
        add_rect(s, px, py, panel_w, band_h, band)
        add_text_box(s, panel.get("header", ""),
                     px + 0.22, py, panel_w - 0.44, band_h,
                     font_name=B.FONT_BODY, size_pt=15, bold=True,
                     color_hex=B.WHITE, align="left", anchor="middle")
        body_y = py + band_h + 0.20
        body_h = panel_h - band_h - 0.40
        if panel.get("bullets"):
            _add_bulleted_textbox(s, panel["bullets"],
                                  px + 0.22, body_y, panel_w - 0.44, body_h,
                                  size_pt=13, color_hex=B.BLACK)
        elif panel.get("body"):
            add_text_box(s, panel["body"],
                         px + 0.22, body_y, panel_w - 0.44, body_h,
                         font_name=B.FONT_BODY, size_pt=13,
                         color_hex=B.BLACK, align="left")

    _maybe_notice(s, spec)
    return s


def build_process(prs, spec):
    """3–6 numbered steps on a horizontal connector line — phases, timelines,
    'how it works'. Red numbered discs, bold step titles, gray descriptions.

    Spec:
      title, kicker, notice: as build_table_slide
      steps: [{title: str, desc: str, label: str (optional, e.g. 'Q1 2026')}]
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    top = _title_kicker_top(s, spec)

    steps = spec.get("steps", [])[:6]
    n = len(steps)
    if n == 0:
        return s
    col_w = B.Pptx.CONTENT_W / n
    disc_d = 0.62
    disc_y = top + 0.55

    # Connector line behind the discs
    if n > 1:
        line_x0 = B.Pptx.MARGIN_L + col_w / 2
        line_x1 = B.Pptx.MARGIN_L + B.Pptx.CONTENT_W - col_w / 2
        add_rect(s, line_x0, disc_y + disc_d / 2 - 0.015,
                 line_x1 - line_x0, 0.03, B.GRAY_SUBTLE)

    for i, st in enumerate(steps):
        cx = B.Pptx.MARGIN_L + i * col_w
        disc_x = cx + col_w / 2 - disc_d / 2
        disc = s.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(disc_x), Inches(disc_y),
            Inches(disc_d), Inches(disc_d))
        disc.fill.solid()
        disc.fill.fore_color.rgb = hex_rgb(B.ADOBE_RED)
        disc.line.fill.background()
        disc.shadow.inherit = False
        flat(disc)
        tf = disc.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = str(i + 1)
        run.font.name = B.FONT_DISPLAY
        run.font.size = Pt(20)
        run.font.color.rgb = hex_rgb(B.WHITE)

        pad = 0.12
        if st.get("label"):
            add_text_box(s, st["label"],
                         cx + pad, disc_y - 0.42, col_w - 2 * pad, 0.30,
                         font_name=B.FONT_BODY, size_pt=11, bold=True,
                         color_hex=B.GRAY_BODY_DARK, align="center")
        add_text_box(s, st.get("title", ""),
                     cx + pad, disc_y + disc_d + 0.22, col_w - 2 * pad, 0.65,
                     font_name=B.FONT_BODY, size_pt=14, bold=True,
                     color_hex=B.BLACK, align="center")
        if st.get("desc"):
            add_text_box(s, st["desc"],
                         cx + pad, disc_y + disc_d + 0.92, col_w - 2 * pad,
                         _CONTENT_BOTTOM - _notice_reserve(spec)
                         - (disc_y + disc_d + 0.95),
                         font_name=B.FONT_BODY, size_pt=11,
                         color_hex=B.GRAY_BODY_DARK, align="center")

    _maybe_notice(s, spec)
    return s


# ---------------------------------------------------------------------------
# Catalyst POV layouts — Adobe Amplify sales artifact format
# Three dense slides: Title/Big Idea | Objectives-Challenges-Solution | Path-to-Power
# ---------------------------------------------------------------------------

def _add_bulleted_textbox(slide, items, x, y, w, h, *,
                          size_pt: int = 10, color_hex: str = "000000",
                          font_name: str = B.FONT_BODY) -> None:
    """Render a list of bullets in a textbox. Each item may be {'text': '...',
    'bold_lead': '...'} where bold_lead is rendered in bold at the start of the
    bullet (used for Adobe product names like 'Real-Time CDP:')."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(3)
        # Bullet marker
        marker_run = p.add_run()
        marker_run.text = "•  "
        marker_run.font.name = font_name
        marker_run.font.size = Pt(size_pt)
        marker_run.font.color.rgb = hex_rgb(color_hex)
        # Bold lead-in (e.g. "Real-Time CDP: ")
        if isinstance(item, dict) and item.get("bold_lead"):
            br = p.add_run()
            br.text = item["bold_lead"]
            br.font.name = font_name
            br.font.size = Pt(size_pt)
            br.font.bold = True
            br.font.color.rgb = hex_rgb(color_hex)
        # Body text
        text = item["text"] if isinstance(item, dict) else str(item)
        body_run = p.add_run()
        body_run.text = text
        body_run.font.name = font_name
        body_run.font.size = Pt(size_pt)
        body_run.font.color.rgb = hex_rgb(color_hex)


def build_catalyst_title(prs, spec):
    """Slide 1 of a Catalyst POV. Full red background. Customer name + Business
    Issue + Big Idea blocks. No red thread (full red bg)."""
    s = _blank_slide(prs)
    set_solid_bg(s, B.ADOBE_RED)
    customer = spec.get("customer", "")
    business_issue = spec.get("business_issue", "")
    big_idea = spec.get("big_idea", "")

    # Customer name — large, top-left below margin
    add_text_box(
        s, customer,
        0.67, 0.55, 12.00, 1.20,
        font_name=B.FONT_DISPLAY, size_pt=54,
        bold=True, color_hex=B.WHITE, align="left", anchor="top",
    )
    # Business Issue label + body
    add_text_box(
        s, "Business issue",
        0.67, 1.95, 12.00, 0.35,
        font_name=B.FONT_BODY, size_pt=12, bold=True,
        color_hex=B.WHITE, align="left",
    )
    add_text_box(
        s, business_issue,
        0.67, 2.30, 12.00, 1.50,
        font_name=B.FONT_BODY, size_pt=22,
        color_hex=B.WHITE, align="left", anchor="top",
    )
    # Big Idea label + body
    add_text_box(
        s, "Big idea",
        0.67, 4.00, 12.00, 0.35,
        font_name=B.FONT_BODY, size_pt=12, bold=True,
        color_hex=B.WHITE, align="left",
    )
    add_text_box(
        s, big_idea,
        0.67, 4.35, 12.00, 2.40,
        font_name=B.FONT_BODY, size_pt=16,
        color_hex=B.WHITE, align="left", anchor="top",
    )
    # Wordmark — white on red, lower-left
    add_wordmark(s, on_dark=True, width_in=1.20)
    return s


def build_catalyst_3col(prs, spec):
    """Slide 2 of a Catalyst POV. Three columns with per-column header color
    and per-column bullet lists. Used for Objectives / Challenges / Solution.

    Spec:
      title: str
      columns: [
        {header: str, header_color: '#hex', bullets: [{text, bold_lead?}]},
        ...
      ]
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    # Slide title
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.MARGIN_L, 0.35, B.Pptx.CONTENT_W, 0.55,
        font_name=B.FONT_DISPLAY, size_pt=22, bold=True,
        color_hex=B.BLACK, align="left",
    )
    cols = spec.get("columns", [])[:3]
    gap = 0.17
    col_w = (B.Pptx.CONTENT_W - gap * 2) / 3  # ~4.12"
    header_y = 1.05
    header_h = 0.48
    body_y = header_y + header_h + 0.08
    body_h = 7.5 - body_y - 0.40  # leave room for footer
    for i, col in enumerate(cols):
        col_x = B.Pptx.MARGIN_L + i * (col_w + gap)
        header_color = col.get("header_color", B.ADOBE_RED).lstrip("#")
        # Header bar (filled rectangle with white text)
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(col_x), Inches(header_y),
            Inches(col_w), Inches(header_h),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_rgb(header_color)
        bar.line.fill.background()
        bar.shadow.inherit = False
        flat(bar)
        # Header text on top of bar
        add_text_box(
            s, col.get("header", ""),
            col_x + 0.12, header_y, col_w - 0.24, header_h,
            font_name=B.FONT_BODY, size_pt=13, bold=True,
            color_hex=B.WHITE, align="left", anchor="middle",
        )
        # Bullet body
        _add_bulleted_textbox(
            s, col.get("bullets", []),
            col_x, body_y, col_w, body_h,
            size_pt=10, color_hex=B.BLACK,
        )
    return s


def build_catalyst_path_value(prs, spec):
    """Slide 3 of a Catalyst POV. Two columns: Path-to-Power on left (executive
    cards with accent bars), Business Value + Why Now on right (value cards
    + dark navy Why Now banner at bottom).

    Spec:
      title: str
      left:  {header, header_color?, execs: [{name, title, mandate, accent_color}]}
      right: {header, header_color?,
              values: [{heading, body}],
              why_now: {label, body, bg_color?}}
    """
    s = _blank_slide(prs)
    add_red_thread(s)
    # Slide title
    add_text_box(
        s, spec.get("title", ""),
        B.Pptx.MARGIN_L, 0.35, B.Pptx.CONTENT_W, 0.55,
        font_name=B.FONT_DISPLAY, size_pt=22, bold=True,
        color_hex=B.BLACK, align="left",
    )

    left = spec.get("left", {})
    right = spec.get("right", {})

    # Geometry
    left_x, left_w = 0.22, 5.70
    right_x, right_w = 6.12, 6.96
    header_y, header_h = 1.05, 0.48
    cards_y = header_y + header_h + 0.10

    # Left column header
    lheader_color = left.get("header_color", B.ADOBE_RED).lstrip("#")
    bar_l = s.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left_x), Inches(header_y),
        Inches(left_w), Inches(header_h),
    )
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = hex_rgb(lheader_color)
    bar_l.line.fill.background()
    bar_l.shadow.inherit = False
    flat(bar_l)
    add_text_box(
        s, left.get("header", ""),
        left_x + 0.12, header_y, left_w - 0.24, header_h,
        font_name=B.FONT_BODY, size_pt=13, bold=True,
        color_hex=B.WHITE, align="left", anchor="middle",
    )

    # Right column header
    rheader_color = right.get("header_color", "1A1A1A").lstrip("#")
    bar_r = s.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(right_x), Inches(header_y),
        Inches(right_w), Inches(header_h),
    )
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = hex_rgb(rheader_color)
    bar_r.line.fill.background()
    bar_r.shadow.inherit = False
    flat(bar_r)
    add_text_box(
        s, right.get("header", ""),
        right_x + 0.12, header_y, right_w - 0.24, header_h,
        font_name=B.FONT_BODY, size_pt=13, bold=True,
        color_hex=B.WHITE, align="left", anchor="middle",
    )

    # Executive cards on left
    execs = left.get("execs", [])[:4]
    card_h = 1.10
    card_gap = 0.06
    accent_w = 0.06
    for i, e in enumerate(execs):
        cy = cards_y + i * (card_h + card_gap)
        accent_color = e.get("accent_color", B.ADOBE_RED).lstrip("#")
        # Accent bar
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(left_x), Inches(cy),
            Inches(accent_w), Inches(card_h),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_rgb(accent_color)
        bar.line.fill.background()
        bar.shadow.inherit = False
        flat(bar)
        # Card content
        text_x = left_x + accent_w + 0.10
        text_w = left_w - accent_w - 0.20
        # Name (line 1)
        add_text_box(
            s, e.get("name", ""),
            text_x, cy + 0.02, text_w, 0.24,
            font_name=B.FONT_BODY, size_pt=11.5, bold=True,
            color_hex=B.BLACK, align="left",
        )
        # Title (line 2, in accent color)
        add_text_box(
            s, e.get("title", ""),
            text_x, cy + 0.26, text_w, 0.20,
            font_name=B.FONT_BODY, size_pt=8.5, bold=True,
            color_hex=accent_color, align="left",
        )
        # Mandate (lines 3+)
        add_text_box(
            s, e.get("mandate", ""),
            text_x, cy + 0.46, text_w, card_h - 0.48,
            font_name=B.FONT_BODY, size_pt=8.5,
            color_hex=B.BLACK, align="left", anchor="top",
        )

    # Value cards on right
    values = right.get("values", [])[:3]
    why_now = right.get("why_now")
    # Reserve space for Why Now banner at bottom (if present)
    bottom_reserve = 1.15 if why_now else 0.0
    avail_h = 7.5 - cards_y - 0.40 - bottom_reserve  # 0.40 for footer
    val_h = (avail_h - card_gap * (len(values) - 1 if values else 0)) / max(len(values), 1)
    for i, v in enumerate(values):
        cy = cards_y + i * (val_h + card_gap)
        # Red accent bar
        bar = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(right_x), Inches(cy),
            Inches(accent_w), Inches(val_h),
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = hex_rgb(B.ADOBE_RED)
        bar.line.fill.background()
        bar.shadow.inherit = False
        flat(bar)
        # Card body
        text_x = right_x + accent_w + 0.12
        text_w = right_w - accent_w - 0.20
        # Heading
        add_text_box(
            s, v.get("heading", ""),
            text_x, cy + 0.02, text_w, 0.28,
            font_name=B.FONT_BODY, size_pt=11.5, bold=True,
            color_hex=B.BLACK, align="left",
        )
        # Body
        add_text_box(
            s, v.get("body", ""),
            text_x, cy + 0.30, text_w, val_h - 0.32,
            font_name=B.FONT_BODY, size_pt=9,
            color_hex=B.BLACK, align="left", anchor="top",
        )

    # Why Now banner at bottom of right column
    if why_now:
        wn_bg = why_now.get("bg_color", "1A1A2E").lstrip("#")
        wn_y = cards_y + (len(values) * (val_h + card_gap)) + 0.05
        wn_h = 7.5 - wn_y - 0.40
        if wn_h < 0.6:
            wn_y = 7.5 - 0.40 - 1.05
            wn_h = 1.05
        banner = s.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(right_x), Inches(wn_y),
            Inches(right_w), Inches(wn_h),
        )
        banner.fill.solid()
        banner.fill.fore_color.rgb = hex_rgb(wn_bg)
        banner.line.fill.background()
        banner.shadow.inherit = False
        flat(banner)
        # Label
        add_text_box(
            s, why_now.get("label", "Why now"),
            right_x + 0.18, wn_y + 0.10, right_w - 0.30, 0.30,
            font_name=B.FONT_BODY, size_pt=12, bold=True,
            color_hex=B.WHITE, align="left",
        )
        # Body
        add_text_box(
            s, why_now.get("body", ""),
            right_x + 0.18, wn_y + 0.40, right_w - 0.30, wn_h - 0.45,
            font_name=B.FONT_BODY, size_pt=9,
            color_hex=B.WHITE, align="left", anchor="top",
        )

    # Small wordmark per Catalyst convention (every slide)
    add_wordmark(s, on_dark=False, width_in=0.80, x_in=0.22, y_in=7.08)
    return s


def build_blank(prs, spec, *, dark: bool = False):
    """Escape hatch — title only, no content. User may overlay shapes after."""
    s = _blank_slide(prs)
    if dark:
        set_solid_bg(s, B.BLACK)
    add_red_thread(s)
    if spec.get("title"):
        add_text_box(
            s, spec["title"],
            B.Pptx.TITLE_X, B.Pptx.TITLE_Y, B.Pptx.TITLE_W, B.Pptx.TITLE_H,
            font_name=B.FONT_DISPLAY, size_pt=B.PptxSize.CONTENT_TITLE,
            bold=True,
            color_hex=B.WHITE if dark else B.BLACK, align="left",
        )
    return s


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

BUILDERS = {
    "title-red":       lambda p, s: build_title_red(p, s),
    "title-white":     lambda p, s: build_title_light(p, s, dark=False),
    "title-dark":      lambda p, s: build_title_light(p, s, dark=True),
    "section-light":   lambda p, s: build_section(p, s, dark=False),
    "section-dark":    lambda p, s: build_section(p, s, dark=True),
    "content":         lambda p, s: build_content(p, s, dark=False),
    "content-dark":    lambda p, s: build_content(p, s, dark=True),
    "quote":           lambda p, s: build_quote(p, s, dark=False),
    "quote-dark":      lambda p, s: build_quote(p, s, dark=True),
    "agenda":          lambda p, s: build_agenda(p, s),
    "two-col":         lambda p, s: build_two_col(p, s, dark=False),
    "two-col-dark":    lambda p, s: build_two_col(p, s, dark=True),
    "three-col":       lambda p, s: build_n_col(p, s, 3, dark=False),
    "three-col-dark":  lambda p, s: build_n_col(p, s, 3, dark=True),
    "four-col":        lambda p, s: build_n_col(p, s, 4, dark=False),
    "four-col-dark":   lambda p, s: build_n_col(p, s, 4, dark=True),
    "five-col":        lambda p, s: build_n_col(p, s, 5, dark=False),
    "five-col-dark":   lambda p, s: build_n_col(p, s, 5, dark=True),
    "thank-you":       lambda p, s: build_thank_you(p, s),
    "end-gray":        lambda p, s: build_thank_you(p, s),
    # Structured-visual layouts (light bg) — use for structured content
    "table":           lambda p, s: build_table_slide(p, s),
    "pricing-table":   lambda p, s: build_table_slide(p, s),   # alias
    "stat-row":        lambda p, s: build_stat_row(p, s),
    "stats":           lambda p, s: build_stat_row(p, s),      # alias
    "cards":           lambda p, s: build_cards(p, s),
    "comparison":      lambda p, s: build_comparison(p, s),
    "process":         lambda p, s: build_process(p, s),
    "timeline":        lambda p, s: build_process(p, s),       # alias
    "blank":           lambda p, s: build_blank(p, s, dark=False),
    "blank-dark":      lambda p, s: build_blank(p, s, dark=True),
    # Catalyst POV (Adobe Amplify sales artifact)
    "catalyst-title":      lambda p, s: build_catalyst_title(p, s),
    "catalyst-3col":       lambda p, s: build_catalyst_3col(p, s),
    "catalyst-path-value": lambda p, s: build_catalyst_path_value(p, s),
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build(spec: dict[str, Any], out_path: Path, *, embed: bool = True) -> None:
    # Start from a blank widescreen presentation. We don't use the template's
    # slide masters directly because python-pptx's layout cloning is brittle
    # across versions; instead, we build slides at the exact coordinates the
    # Adobe master uses (see brand.py / Pptx class).
    prs = Presentation()
    prs.slide_width  = Inches(B.Pptx.SLIDE_W)
    prs.slide_height = Inches(B.Pptx.SLIDE_H)

    # Document properties
    cp = prs.core_properties
    cp.title    = spec.get("title", "Adobe presentation")
    cp.subject  = spec.get("subtitle", "")
    cp.author   = spec.get("author", "Adobe")
    cp.comments = "Generated with the adobe-presentation skill."

    slides_spec = spec.get("slides", [])
    confidential = bool(spec.get("confidential", True))
    total = len(slides_spec)

    for idx, slide_spec in enumerate(slides_spec, start=1):
        layout = slide_spec.get("layout", "content")
        builder = BUILDERS.get(layout)
        if builder is None:
            print(f"  ! Unknown layout '{layout}' on slide {idx} — using 'content'")
            builder = BUILDERS["content"]
        s = builder(prs, slide_spec)
        # No footer on the very first cover slide (per Adobe convention).
        # Catalyst POVs DO want a footer on the title slide per the brief.
        is_cover = (idx == 1 and layout in ("title-red", "title-white", "title-dark"))
        if not is_cover:
            on_dark = (layout.endswith("-dark") or layout == "title-red"
                       or layout == "catalyst-title")
            add_footer(s, idx, total, confidential=confidential, on_dark=on_dark)

    prs.save(out_path)
    print(f"✓ Wrote {out_path}  ({total} slides)")

    if embed:
        try:
            import embed_fonts
            fonts = embed_fonts.embed_pptx_fonts(out_path)
            if fonts:
                print(f"✓ Embedded fonts: {', '.join(fonts)}")
        except Exception as e:  # never let embedding failure lose the deck
            print(f"! Font embedding skipped ({e}). The .pptx still names the "
                  f"correct fonts; install Adobe Clean to render them.")


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--no-embed"]
    embed = "--no-embed" not in argv
    if len(args) != 2:
        print("Usage: python build_deck.py SPEC.json OUTPUT.pptx [--no-embed]")
        return 2
    spec_path = Path(args[0])
    out_path  = Path(args[1])
    spec = json.loads(spec_path.read_text())
    build(spec, out_path, embed=embed)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main(sys.argv))
