#!/usr/bin/env python3
"""
Adobe-branded Word document builder.

Usage:
    python scripts/build_doc.py path/to/spec.json output.docx

Produces a .docx with:
  - Red cover block (optional)
  - Adobe header with "Adobe" wordmark text and red underline
  - H1 with red left border
  - Body in Adobe Clean Regular, 10pt, 1.15 line spacing
  - Callout boxes, tables, bullets with brand-correct formatting
  - Footer with copyright + page number
  - Trademark attribution paragraph at end

JSON SCHEMA
-----------
{
  "title":      "Document title",
  "subtitle":   "Optional",
  "doc_type":   "one-pager",       // one-pager | brief | guide | rfp | exec-summary | memo
  "confidential": true,             // default true
  "include_cover_block": true,      // default: true except for memo/rfp
  "include_trademark_page": false,  // append legal attribution at end
  "sections": [
    { "type": "h1",   "text": "..." },
    { "type": "h2",   "text": "..." },
    { "type": "h3",   "text": "..." },
    { "type": "body", "text": "..." },
    { "type": "bullets", "items": [
        { "text": "Top-level bullet", "level": 0 },
        { "text": "Sub-bullet",       "level": 1 }
      ]
    },
    { "type": "callout", "text": "Key insight." },
    { "type": "table",
      "header": ["A", "B", "C"],
      "rows":   [["a1","b1","c1"], ["a2","b2","c2"]] }
  ]
}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Twips, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import brand as B

# Licensed Adobe wordmark for the header (see assets/README.md)
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "logos"
WORDMARK_RED_PNG = ASSETS_DIR / "Adobe_Wordmark_RGB_Red.png"


# ---------------------------------------------------------------------------
# OOXML helpers (python-docx doesn't expose every property we need)
# ---------------------------------------------------------------------------

def _set_paragraph_shading(paragraph, hex_color: str) -> None:
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pPr.append(shd)


def _set_paragraph_border(paragraph, side: str, *, hex_color: str,
                          size: int = 48, space: int = 8,
                          style: str = "single") -> None:
    """side: left | right | top | bottom"""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    border = OxmlElement(f"w:{side}")
    border.set(qn("w:val"), style)
    border.set(qn("w:sz"), str(size))
    border.set(qn("w:space"), str(space))
    border.set(qn("w:color"), hex_color)
    pBdr.append(border)


def _set_cell_shading(cell, hex_color: str) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _set_cell_borders(cell, *, color: str = "CCCCCC", size: int = 4) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), str(size))
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), color)
        tcBorders.append(b)
    tcPr.append(tcBorders)


def _set_run_font(run, *, name: str = B.FONT_BODY, size_hp: int = B.DocxSize.BODY,
                  bold: bool = False, color_hex: str = B.BLACK) -> None:
    run.font.name = name
    # Set east-asian / complex-script font names so Word doesn't substitute on Asia locales
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)
    run.font.size = Pt(size_hp / 2)
    # Heavy families (Adobe Clean Black) carry their own weight — don't faux-bold.
    run.font.bold = bold and not B.is_heavy_font(name)
    run.font.color.rgb = RGBColor.from_string(color_hex)


def _add_page_number_field(paragraph) -> None:
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._element.append(fldChar1)
    run._element.append(instrText)
    run._element.append(fldChar2)
    _set_run_font(run, size_hp=B.DocxSize.FOOTER, color_hex=B.GRAY_FOOTER)


# ---------------------------------------------------------------------------
# Document scaffolding
# ---------------------------------------------------------------------------

def _setup_page(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width  = Twips(B.Docx.PAGE_W)
    section.page_height = Twips(B.Docx.PAGE_H)
    section.top_margin    = Twips(B.Docx.MARGIN_TOP)
    section.right_margin  = Twips(B.Docx.MARGIN_RIGHT)
    section.bottom_margin = Twips(B.Docx.MARGIN_BOTTOM)
    section.left_margin   = Twips(B.Docx.MARGIN_LEFT)

    # Default paragraph style: Adobe Clean 10pt
    style = doc.styles["Normal"]
    style.font.name = B.FONT_BODY
    style.font.size = Pt(10)
    pf = style.paragraph_format
    pf.line_spacing = 1.15
    pf.space_after = Pt(4)


def _setup_header(section, header_text: str = "Adobe") -> None:
    """Header: licensed Adobe wordmark PNG if available, otherwise text fallback.
    Either way, finished with a thin red underline."""
    h = section.header
    p = h.paragraphs[0]
    p.text = ""
    if WORDMARK_RED_PNG.exists():
        run = p.add_run()
        # 0.7" wide wordmark fits comfortably above body content; height auto
        run.add_picture(str(WORDMARK_RED_PNG), width=Inches(0.7))
    else:
        run = p.add_run(header_text)
        _set_run_font(run, name=B.FONT_BODY, size_hp=B.DocxSize.HEADER,
                      bold=True, color_hex=B.ADOBE_RED)
    _set_paragraph_border(p, "bottom", hex_color=B.ADOBE_RED, size=12, space=4)
    p.paragraph_format.space_after = Pt(4)


def _setup_footer(section, confidential: bool) -> None:
    f = section.footer
    p = f.paragraphs[0]
    p.text = ""
    # Top border (subtle separator)
    _set_paragraph_border(p, "top", hex_color=B.GRAY_BORDER, size=6, space=4)
    # Tab stop at right margin for the page number
    p.paragraph_format.tab_stops.add_tab_stop(
        Twips(B.Docx.CONTENT_W),
        alignment=WD_TAB_ALIGNMENT.RIGHT,
    )
    run = p.add_run(B.footer_text(confidential=confidential) + "\t")
    _set_run_font(run, size_hp=B.DocxSize.FOOTER, color_hex=B.GRAY_FOOTER)
    _add_page_number_field(p)


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _add_cover_block(doc: Document, title: str, subtitle: str, *, hero: bool = False) -> None:
    """Red shaded title block at the top of page 1."""
    title_size = B.DocxSize.COVER_TITLE_HERO if hero else B.DocxSize.COVER_TITLE
    # Title paragraph
    p1 = doc.add_paragraph()
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(0)
    p1.paragraph_format.left_indent = Twips(360)
    p1.paragraph_format.right_indent = Twips(360)
    _set_paragraph_shading(p1, B.ADOBE_RED)
    run = p1.add_run(title)
    _set_run_font(run, name=B.FONT_DISPLAY, size_hp=title_size,
                  bold=True, color_hex=B.WHITE)
    # Subtitle paragraph (continues red block)
    if subtitle:
        p2 = doc.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(12)
        p2.paragraph_format.left_indent = Twips(360)
        p2.paragraph_format.right_indent = Twips(360)
        _set_paragraph_shading(p2, B.ADOBE_RED)
        run = p2.add_run(subtitle)
        _set_run_font(run, name=B.FONT_BODY, size_hp=B.DocxSize.COVER_SUBTITLE,
                      color_hex=B.WHITE)
    # Spacer
    doc.add_paragraph()


def _add_heading(doc: Document, text: str, level: int) -> None:
    p = doc.add_paragraph()
    if level == 1:
        size = B.DocxSize.H1
        color = B.BLACK
        bold = True
        name = B.FONT_BODY  # Use Adobe Clean Black weight via bold
        _set_paragraph_border(p, "left", hex_color=B.ADOBE_RED,
                              size=B.Docx.BORDER_RED_SIZE,
                              space=B.Docx.BORDER_RED_SPACE)
        p.paragraph_format.left_indent = Twips(180)
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(6)
    elif level == 2:
        size = B.DocxSize.H2
        color = B.BLACK
        bold = True
        name = B.FONT_BODY
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
    elif level == 3:
        size = B.DocxSize.H3
        color = B.ADOBE_RED
        bold = True
        name = B.FONT_BODY
        p.paragraph_format.space_before = Pt(9)
        p.paragraph_format.space_after = Pt(3)
    elif level == 4:
        size = B.DocxSize.H4
        color = B.GRAY_FOOTER
        bold = True
        name = B.FONT_BODY
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
    else:
        size = B.DocxSize.BODY
        color = B.BLACK
        bold = False
        name = B.FONT_BODY
    run = p.add_run(text)
    _set_run_font(run, name=name, size_hp=size, bold=bold, color_hex=color)


def _add_body(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    _set_run_font(run, size_hp=B.DocxSize.BODY, color_hex=B.BLACK)


def _add_bullets(doc: Document, items: list[dict]) -> None:
    for item in items:
        level = int(item.get("level", 0))
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        indent = {0: 720, 1: 1080, 2: 1440}.get(level, 720)
        p.paragraph_format.left_indent = Twips(indent)
        p.paragraph_format.first_line_indent = Twips(-360)
        marker = {0: "• ", 1: "– ", 2: "— "}.get(level, "• ")
        run = p.add_run(marker + item["text"])
        size = {0: B.DocxSize.BULLET_L0, 1: B.DocxSize.BULLET_L1,
                2: B.DocxSize.BULLET_L2}.get(level, B.DocxSize.BULLET_L0)
        color = B.BLACK if level == 0 else B.GRAY_BODY_DARK
        _set_run_font(run, size_hp=size, color_hex=color)


def _add_callout(doc: Document, text: str) -> None:
    """1-cell table with red left border and gray fill — for key insights."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    table.columns[0].width = Twips(B.Docx.CONTENT_W)
    cell = table.cell(0, 0)
    cell.width = Twips(B.Docx.CONTENT_W)
    _set_cell_shading(cell, B.GRAY_SECTION_BG)

    # Borders: red on left, none elsewhere
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "bottom", "right"):
        b = OxmlElement(f"w:{side}")
        b.set(qn("w:val"), "nil")
        tcBorders.append(b)
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "48")
    left.set(qn("w:space"), "0")
    left.set(qn("w:color"), B.ADOBE_RED)
    tcBorders.append(left)
    tcPr.append(tcBorders)

    # Cell margins
    tcMar = OxmlElement("w:tcMar")
    for side, val in (("top", 120), ("bottom", 120), ("left", 180), ("right", 120)):
        m = OxmlElement(f"w:{side}")
        m.set(qn("w:w"), str(val))
        m.set(qn("w:type"), "dxa")
        tcMar.append(m)
    tcPr.append(tcMar)

    p = cell.paragraphs[0]
    run = p.add_run(text)
    _set_run_font(run, size_hp=B.DocxSize.CALLOUT, bold=True, color_hex=B.BLACK)
    doc.add_paragraph()  # spacer after


def _add_table(doc: Document, header: list[str], rows: list[list[str]]) -> None:
    ncols = len(header)
    table = doc.add_table(rows=1 + len(rows), cols=ncols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    col_w = B.Docx.CONTENT_W // ncols
    for col in table.columns:
        col.width = Twips(col_w)

    # Header row
    for c, h_text in enumerate(header):
        cell = table.rows[0].cells[c]
        cell.width = Twips(col_w)
        _set_cell_shading(cell, B.ADOBE_RED)
        _set_cell_borders(cell, color=B.ADOBE_RED, size=4)
        p = cell.paragraphs[0]
        run = p.add_run(h_text)
        _set_run_font(run, size_hp=B.DocxSize.TABLE_HEADER, bold=True, color_hex=B.WHITE)

    # Body rows
    for r, row in enumerate(rows):
        for c, val in enumerate(row[:ncols]):
            cell = table.rows[r + 1].cells[c]
            cell.width = Twips(col_w)
            fill = B.GRAY_SECTION_BG if r % 2 == 1 else B.WHITE
            _set_cell_shading(cell, fill)
            _set_cell_borders(cell, color=B.GRAY_BORDER, size=4)
            p = cell.paragraphs[0]
            run = p.add_run(str(val))
            _set_run_font(run, size_hp=B.DocxSize.TABLE_BODY, color_hex=B.BLACK)
    doc.add_paragraph()  # spacer after


SECTION_BUILDERS = {
    "h1":      lambda doc, sec: _add_heading(doc, sec["text"], 1),
    "h2":      lambda doc, sec: _add_heading(doc, sec["text"], 2),
    "h3":      lambda doc, sec: _add_heading(doc, sec["text"], 3),
    "h4":      lambda doc, sec: _add_heading(doc, sec["text"], 4),
    "body":    lambda doc, sec: _add_body(doc, sec["text"]),
    "bullets": lambda doc, sec: _add_bullets(doc, sec["items"]),
    "callout": lambda doc, sec: _add_callout(doc, sec["text"]),
    "table":   lambda doc, sec: _add_table(doc, sec["header"], sec["rows"]),
}


def _add_trademark_page(doc: Document) -> None:
    doc.add_page_break()
    p = doc.add_paragraph()
    run = p.add_run("Legal")
    _set_run_font(run, size_hp=B.DocxSize.H2, bold=True, color_hex=B.BLACK)
    _add_body(doc, B.footer_text(confidential=False))
    _add_body(doc, B.trademark_paragraph())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build(spec: dict[str, Any], out_path: Path, *, embed: bool = True) -> None:
    doc = Document()
    _setup_page(doc)
    section = doc.sections[0]

    confidential = bool(spec.get("confidential", True))
    doc_type = spec.get("doc_type", "brief")
    include_cover = spec.get("include_cover_block", doc_type not in ("memo", "rfp"))
    hero = (doc_type == "one-pager")

    _setup_header(section, spec.get("header_text", "Adobe"))
    _setup_footer(section, confidential=confidential)

    # Core properties
    doc.core_properties.title = spec.get("title", "Adobe document")
    doc.core_properties.subject = spec.get("subtitle", "")
    doc.core_properties.author = spec.get("author", "Adobe")

    if include_cover and spec.get("title"):
        _add_cover_block(doc, spec["title"], spec.get("subtitle", ""), hero=hero)

    for sec in spec.get("sections", []):
        builder = SECTION_BUILDERS.get(sec.get("type"))
        if builder is None:
            print(f"  ! Unknown section type '{sec.get('type')}' — skipping")
            continue
        builder(doc, sec)

    if spec.get("include_trademark_page"):
        _add_trademark_page(doc)

    doc.save(out_path)
    print(f"✓ Wrote {out_path}")

    if embed:
        try:
            import embed_fonts
            fonts = embed_fonts.embed_docx_fonts(out_path)
            if fonts:
                print(f"✓ Embedded fonts: {', '.join(fonts)}")
        except Exception as e:  # never let embedding failure lose the doc
            print(f"! Font embedding skipped ({e}). The .docx still names the "
                  f"correct fonts; install Adobe Clean or export to PDF to render.")


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--no-embed"]
    embed = "--no-embed" not in argv
    if len(args) != 2:
        print("Usage: python build_doc.py SPEC.json OUTPUT.docx [--no-embed]")
        return 2
    spec = json.loads(Path(args[0]).read_text())
    build(spec, Path(args[1]), embed=embed)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main(sys.argv))
