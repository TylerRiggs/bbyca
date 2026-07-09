#!/usr/bin/env python3
"""
Adobe-branded HTML document builder.

Usage:
    python scripts/build_html.py path/to/spec.json output.html

Takes the SAME JSON content spec as build_doc.py and renders a single,
**self-contained** on-brand HTML file:
  - Adobe Clean subset + base64-embedded as @font-face (no external font files)
  - the approved Adobe wordmark inlined from assets/logos/ (never drawn)
  - design tokens + semantic type classes from assets/adobe-design-system.css
  - the mandatory left red thread, sentence-case headings, Adobe footer

Because everything is inlined, the output is one portable .html that renders
authentically Adobe on any machine — the HTML equivalent of embedding fonts
into a .pptx/.docx. Hand it to the user as-is.

JSON SCHEMA  (identical to build_doc.py)
----------------------------------------
{
  "title": "...", "subtitle": "...", "doc_type": "one-pager",
  "confidential": true, "include_trademark_page": false,
  "sections": [
    {"type":"h1","text":"..."}, {"type":"h2","text":"..."},
    {"type":"h3","text":"..."}, {"type":"body","text":"..."},
    {"type":"bullets","items":[{"text":"...","level":0}]},
    {"type":"callout","text":"..."},
    {"type":"table","header":["A","B"],"rows":[["1","2"]]}
  ]
}
"""
from __future__ import annotations

import base64
import html
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

import brand as B

SKILL = Path(__file__).resolve().parent.parent
FONTS_DIR = SKILL / "assets" / "fonts"
CSS_PATH = SKILL / "assets" / "adobe-design-system.css"
LOGO_RED_SVG = SKILL / "assets" / "logos" / "Adobe_Wordmark_RGB_Red.svg"
LOGO_WHITE_SVG = SKILL / "assets" / "logos" / "Adobe_Wordmark_RGB_White.svg"

# Brand weights to embed (family "Adobe Clean"). Keeps the file small while
# covering the full doc hierarchy: body 400, bold 700, section 800, headline 900.
FONT_FACES = [
    ("AdobeClean-Regular.otf",   400, "normal"),
    ("AdobeClean-It.otf",        400, "italic"),
    ("AdobeClean-Bold.otf",      700, "normal"),
    ("AdobeClean-BoldIt.otf",    700, "italic"),
    ("AdobeClean-ExtraBold.otf", 800, "normal"),
    ("AdobeClean-Black.otf",     900, "normal"),
    ("AdobeClean-BlackIt.otf",   900, "italic"),
]

# Glyphs to keep when subsetting — Latin text + the punctuation Adobe copy uses.
_KEEP_UNICODES = (
    list(range(0x20, 0x7F)) +        # basic Latin
    list(range(0xA0, 0x100)) +       # Latin-1 (©, accents, ®)
    [0x2018, 0x2019, 0x201C, 0x201D,  # ' ' " "
     0x2013, 0x2014,                  # – —
     0x2026, 0x2022, 0x00B7,          # … • ·
     0x2192, 0x2190, 0x2191, 0x2193,  # → ← ↑ ↓
     0x20AC, 0x00A3, 0x00A5,          # € £ ¥
     0x2122, 0x00AE, 0x00A9]          # ™ ® ©
)


def _subset_b64(otf_path: Path) -> str:
    """Subset an OTF to the kept glyph set and return base64 of the bytes."""
    from fontTools.subset import Subsetter, Options
    from fontTools.ttLib import TTFont

    font = TTFont(str(otf_path))
    opts = Options()
    opts.layout_features = ["*"]      # keep kerning / ligatures
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables = []
    ss = Subsetter(options=opts)
    ss.populate(unicodes=_KEEP_UNICODES)
    ss.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _font_face_css() -> str:
    blocks = []
    for fname, weight, style in FONT_FACES:
        p = FONTS_DIR / fname
        if not p.exists():
            continue
        b64 = _subset_b64(p)
        blocks.append(
            '@font-face{font-family:"Adobe Clean";'
            f'font-weight:{weight};font-style:{style};font-display:swap;'
            f'src:url("data:font/otf;base64,{b64}") format("opentype");}}'
        )
    return "\n".join(blocks)


def _tokens_css() -> str:
    """The bundled token + semantic-class CSS, minus its url()-based @font-face
    blocks (we replace those with base64 ones so the file is self-contained)."""
    css = CSS_PATH.read_text()
    css = re.sub(r"@font-face\s*\{[^}]*\}", "", css)  # strip url()-based faces
    return css


def _inline_logo(white: bool = False) -> str:
    path = LOGO_WHITE_SVG if white else LOGO_RED_SVG
    svg = path.read_text()
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    # constrain height; preserve aspect via viewBox already in the file
    svg = re.sub(r"<svg ", '<svg class="adobe-wordmark" role="img" aria-label="Adobe" ', svg, count=1)
    return svg


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _esc(t: str) -> str:
    return html.escape(t, quote=False)


def _render_section(sec: dict) -> str:
    t = sec.get("type")
    if t == "h1":
        return f'<h1 class="thread-h1">{_esc(sec.get("text",""))}</h1>'
    if t == "h2":
        return f"<h2>{_esc(sec.get('text',''))}</h2>"
    if t == "h3":
        return f"<h3>{_esc(sec.get('text',''))}</h3>"
    if t == "body":
        return f"<p>{_esc(sec.get('text',''))}</p>"
    if t == "bullets":
        # support up to 2 nested levels
        out, cur_level = [], 0
        out.append("<ul>")
        for it in sec.get("items", []):
            lvl = int(it.get("level", 0))
            while lvl > cur_level:
                out.append("<ul>"); cur_level += 1
            while lvl < cur_level:
                out.append("</ul>"); cur_level -= 1
            out.append(f"<li>{_esc(it.get('text',''))}</li>")
        while cur_level >= 0:
            out.append("</ul>"); cur_level -= 1
        return "".join(out)
    if t == "callout":
        return f'<aside class="callout">{_esc(sec.get("text",""))}</aside>'
    if t == "table":
        header = sec.get("header", [])
        rows = sec.get("rows", [])
        thead = "".join(f"<th>{_esc(str(h))}</th>" for h in header)
        body = "".join(
            "<tr>" + "".join(f"<td>{_esc(str(c))}</td>" for c in r) + "</tr>"
            for r in rows
        )
        return f"<table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table>"
    return ""


PAGE_CSS = """
*{box-sizing:border-box}
body{margin:0;line-height:1.5}
.page{position:relative;max-width:860px;margin:0 auto;padding:56px 72px 96px}
.page::before{content:"";position:fixed;left:0;top:0;bottom:0;width:10px;background:var(--adobe-red)}
.doc-header{display:flex;align-items:center;justify-content:space-between;
  padding-bottom:18px;border-bottom:2px solid var(--adobe-red);margin-bottom:40px}
.adobe-wordmark{height:24px;width:auto;display:block}
.doc-header .eyebrow{font-weight:700;font-size:13px;color:var(--fg-3)}
.cover h1{font-weight:900;letter-spacing:-.02em;line-height:.92;
  font-size:clamp(36px,5.5vw,56px);max-width:18ch;margin:8px 0 0}
.cover .subtitle{font-size:20px;color:var(--fg-2);margin-top:16px;max-width:60ch}
h1.thread-h1{font-weight:900;letter-spacing:-.02em;font-size:30px;line-height:1.05;
  margin:48px 0 12px;padding-left:14px;border-left:6px solid var(--adobe-red)}
h2{font-weight:800;font-size:21px;margin:32px 0 6px;letter-spacing:-.01em}
h3{font-weight:700;font-size:16px;color:var(--adobe-red);margin:22px 0 4px}
p{font-size:15px;color:var(--fg-2);margin:10px 0;max-width:70ch}
ul{margin:10px 0 10px 0;padding-left:22px}
li{font-size:15px;color:var(--fg-2);margin:4px 0}
.callout{background:var(--bg-3);border-left:4px solid var(--adobe-red);
  padding:16px 20px;margin:20px 0;font-size:15px;border-radius:0 8px 8px 0}
table{border-collapse:collapse;width:100%;margin:18px 0;font-size:14px}
th{background:var(--adobe-black);color:#fff;text-align:left;padding:9px 12px;font-weight:700}
td{padding:9px 12px;border-bottom:1px solid var(--gray-300)}
tbody tr:nth-child(even){background:var(--gray-100)}
.doc-footer{margin-top:80px;padding-top:14px;border-top:1px solid var(--gray-300);
  display:flex;justify-content:space-between;font-size:11px;color:#191919}
"""


def build(spec: dict[str, Any], out_path: Path) -> None:
    title = spec.get("title", "Adobe document")
    subtitle = spec.get("subtitle", "")
    confidential = bool(spec.get("confidential", True))
    eyebrow = spec.get("eyebrow", spec.get("header_text", ""))

    sections_html = "\n".join(_render_section(s) for s in spec.get("sections", []))

    cover = ""
    if spec.get("include_cover_block", True) and title:
        cover = (f'<section class="cover"><h1>{_esc(title)}</h1>'
                 + (f'<p class="subtitle">{_esc(subtitle)}</p>' if subtitle else "")
                 + "</section>")

    trademark = ""
    if spec.get("include_trademark_page"):
        trademark = f'<p style="font-size:11px;color:var(--fg-3);margin-top:48px">{_esc(B.trademark_paragraph())}</p>'

    footer = (f'<footer class="doc-footer"><span>{_esc(B.footer_text(confidential))}</span>'
              f'<span>Adobe</span></footer>')

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)}</title>
<style>
{_font_face_css()}
{_tokens_css()}
{PAGE_CSS}
</style>
</head>
<body>
<div class="page">
  <header class="doc-header">
    {_inline_logo(white=False)}
    {f'<span class="eyebrow">{_esc(eyebrow)}</span>' if eyebrow else ''}
  </header>
  {cover}
  {sections_html}
  {trademark}
  {footer}
</div>
</body>
</html>
"""
    out_path.write_text(doc, encoding="utf-8")
    kb = out_path.stat().st_size / 1024
    print(f"✓ Wrote {out_path}  (self-contained, {kb:.0f} KB)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python build_html.py SPEC.json OUTPUT.html")
        return 2
    spec = json.loads(Path(argv[1]).read_text())
    build(spec, Path(argv[2]))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main(sys.argv))
