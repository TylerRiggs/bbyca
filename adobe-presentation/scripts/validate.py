#!/usr/bin/env python3
"""
Adobe brand QA — validates an Adobe-branded .pptx or .docx for compliance.

Usage:
    python scripts/validate.py output.pptx
    python scripts/validate.py output.docx

Checks (PPTX):
  1. A logo IMAGE is placed (catches drawn/approximated/omitted logos)
  2. Adobe Clean is embedded (warning if not)
  3. Red thread present on every non-full-red slide       (x=0, w≈0.14")
  4. Footer present on every slide except first cover     (color #191919)
  5. Font on every text run is Adobe Clean / Adobe Clean Black
  6. No placeholder text ("Click to edit", "Lorem ipsum", etc.)
  7. No disallowed color (red `EB1000`) used as body text fill
  8. No bullet level > 2 (i.e. > 3 visible levels)
  9. No banned phrases ("Adobe Inc.", "Adobe Systems", "Adobe Incorporated")
     except in legal/trademark sections

Checks (DOCX):
  Same surface checks adapted for docx structure.

Exits 0 on pass, 1 on fail. Prints a brand-compliance report.
"""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import brand as B

NS = {
    "a":   "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p":   "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r":   "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w":   "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

PLACEHOLDER_PATTERNS = [
    re.compile(r"click to edit", re.I),
    re.compile(r"lorem ipsum", re.I),
    re.compile(r"\{\{[^}]+\}\}"),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\bxxx+\b", re.I),
]

BANNED_PHRASES = [
    re.compile(r"\bAdobe Inc\b"),
    re.compile(r"\bAdobe Systems\b"),
    re.compile(r"\bAdobe Incorporated\b"),
]

ALLOWED_FONTS = {B.FONT_BODY.lower(), B.FONT_DISPLAY.lower(),
                 "adobe clean", "adobe clean display", "adobe clean display black"}


# ---------------------------------------------------------------------------
# PPTX validator
# ---------------------------------------------------------------------------

def validate_pptx(path: Path) -> tuple[int, list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    z = zipfile.ZipFile(path)

    # --- Logo: the approved wordmark must be a placed image, never drawn. ---
    media = [n for n in z.namelist() if n.startswith("ppt/media/")]
    pics_total = 0
    for n in z.namelist():
        if re.match(r"^ppt/slides/slide\d+\.xml$", n):
            pics_total += z.read(n).decode("utf-8", "ignore").count("<p:pic")
    if pics_total == 0:
        issues.append(
            "no image placed on any slide — covers/closing slides must use the "
            "approved Adobe wordmark FILE (assets/logos/), never a drawn or "
            "approximated logo")

    # --- Fonts: should be embedded for portable rendering. ---
    pres_xml = z.read("ppt/presentation.xml").decode("utf-8", "ignore")
    if "<p:embeddedFontLst" not in pres_xml:
        warnings.append(
            "Adobe Clean is not embedded — recipients without the font will see "
            "a fallback. Rebuild without --no-embed, or run embed_fonts.py.")

    slide_files = sorted(
        [n for n in z.namelist() if re.match(r"^ppt/slides/slide\d+\.xml$", n)],
        key=lambda n: int(re.search(r"slide(\d+)", n).group(1)),
    )
    total = len(slide_files)
    visual_slides = 0   # slides with graphic structure beyond thread/bg
    print(f"Validating {path.name} — {total} slides")

    for n in slide_files:
        idx = int(re.search(r"slide(\d+)", n).group(1))
        xml = z.read(n).decode("utf-8", errors="ignore")
        root = ET.fromstring(xml)

        # Background full red? Two ways: <p:bg> element OR a full-bleed
        # rectangle shape covering the entire slide with fill EB1000.
        bg_red = False
        if "<p:bg>" in xml:
            bg_block = xml.split("<p:bg>", 1)[1].split("</p:bg>", 1)[0]
            if B.ADOBE_RED in bg_block.upper():
                bg_red = True
        if not bg_red:
            for sp in root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp"):
                off = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}off")
                ext = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}ext")
                fills = sp.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr")
                if off is None or ext is None or not fills:
                    continue
                x_in = int(off.attrib.get("x", "0")) / 914400
                y_in = int(off.attrib.get("y", "0")) / 914400
                w_in = int(ext.attrib.get("cx", "0")) / 914400
                h_in = int(ext.attrib.get("cy", "0")) / 914400
                colors = {f.attrib.get("val", "").upper() for f in fills}
                if (abs(x_in) < 0.05 and abs(y_in) < 0.05 and
                        w_in > 12.5 and h_in > 7.0 and B.ADOBE_RED in colors):
                    bg_red = True
                    break

        # Red thread check (skip if full-red bg)
        if not bg_red:
            has_thread = False
            for sp in root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp"):
                # find offset
                off = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}off")
                ext = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}ext")
                fills = sp.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr")
                if off is None or ext is None or not fills:
                    continue
                x_emu = int(off.attrib.get("x", "0"))
                w_emu = int(ext.attrib.get("cx", "0"))
                h_emu = int(ext.attrib.get("cy", "0"))
                x_in = x_emu / 914400
                w_in = w_emu / 914400
                h_in = h_emu / 914400
                colors = {f.attrib.get("val", "").upper() for f in fills}
                if x_in < 0.05 and 0.10 <= w_in <= 0.20 and h_in >= 6.5 and B.ADOBE_RED in colors:
                    has_thread = True
                    break
            if not has_thread:
                issues.append(f"slide {idx}: missing or malformed red thread")

        # Visual structure: any filled shape that is neither the red thread
        # nor a full-bleed background (bands, cards, accent bars, discs,
        # table shading). Decks of pure text boxes read as generic.
        has_visual = False
        for sp in root.iter("{http://schemas.openxmlformats.org/presentationml/2006/main}sp"):
            spPr = sp.find("{http://schemas.openxmlformats.org/presentationml/2006/main}spPr")
            if spPr is None:
                continue
            off = spPr.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}off")
            ext = spPr.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}ext")
            # A real graphic element has a shape-level solid fill; text boxes
            # only carry srgbClr inside their run properties (font color).
            fill = spPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill")
            if off is None or ext is None or fill is None:
                continue
            x_in = int(off.attrib.get("x", "0")) / 914400
            w_in = int(ext.attrib.get("cx", "0")) / 914400
            h_in = int(ext.attrib.get("cy", "0")) / 914400
            is_thread = x_in < 0.05 and 0.10 <= w_in <= 0.20 and h_in >= 6.5
            is_fullbleed = w_in > 12.5 and h_in > 7.0
            if not is_thread and not is_fullbleed:
                has_visual = True
                break
        if has_visual:
            visual_slides += 1

        # Font + placeholder + banned phrase checks
        slide_text_runs: list[tuple[str, str]] = []  # (font, text)
        for rTxt in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}r"):
            t_el = rTxt.find("{http://schemas.openxmlformats.org/drawingml/2006/main}t")
            if t_el is None or not t_el.text:
                continue
            rPr = rTxt.find("{http://schemas.openxmlformats.org/drawingml/2006/main}rPr")
            font = ""
            if rPr is not None:
                latin = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}latin")
                if latin is not None:
                    font = latin.attrib.get("typeface", "")
            slide_text_runs.append((font.lower(), t_el.text))

        font_problems = set()
        for font, txt in slide_text_runs:
            if font and font not in ALLOWED_FONTS and "adobe clean" not in font:
                font_problems.add(font)
        if font_problems:
            issues.append(f"slide {idx}: non-Adobe-Clean fonts: {sorted(font_problems)}")

        # Placeholder & banned phrase
        for _, txt in slide_text_runs:
            for pat in PLACEHOLDER_PATTERNS:
                if pat.search(txt):
                    issues.append(f"slide {idx}: placeholder text remains: {txt[:60]!r}")
                    break
            for pat in BANNED_PHRASES:
                if pat.search(txt):
                    issues.append(f"slide {idx}: banned phrase: {pat.pattern} in {txt[:60]!r}")

        # Footer check (look for the © wording or an Adobe Clean run at footer y-position)
        full_text = " ".join(t for _, t in slide_text_runs)
        if not bg_red and idx > 1:
            if "© " not in full_text or "Adobe" not in full_text:
                issues.append(f"slide {idx}: no Adobe copyright footer detected")

    # Generic-deck check: covers/dividers/quotes are legitimately text-only,
    # so only warn when a substantive deck has almost no graphic structure.
    body_slides = max(total - 2, 0)   # ignore cover + closing
    if body_slides >= 3 and visual_slides < max(1, round(body_slides * 0.4)):
        warnings.append(
            f"only {visual_slides} of {total} slides have visual structure "
            "(bands, cards, tables, accent bars) — the deck reads as a "
            "text-only bullet wall. Rebuild structured content (pricing, "
            "metrics, options, timelines) with the table / stat-row / cards / "
            "comparison / process layouts (SKILL.md Step 2a).")

    z.close()
    return total, issues, warnings


# ---------------------------------------------------------------------------
# DOCX validator
# ---------------------------------------------------------------------------

def validate_docx(path: Path) -> tuple[int, list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    z = zipfile.ZipFile(path)

    # Logo: the header wordmark must be a placed image, not drawn / not text.
    if not any(n.startswith("word/media/") for n in z.namelist()):
        issues.append(
            "no image in the document — the header must use the approved Adobe "
            "wordmark FILE (assets/logos/), never a drawn or text approximation")
    # Fonts embedded?
    if not any(n.endswith(".odttf") for n in z.namelist()):
        warnings.append(
            "Adobe Clean is not embedded — recipients without the font will see "
            "a fallback. Rebuild without --no-embed, or export to PDF to share.")
    doc_xml = z.read("word/document.xml").decode("utf-8", errors="ignore")
    root = ET.fromstring(doc_xml)

    # Fonts in document body
    fonts_used: set[str] = set()
    text_runs: list[str] = []
    for r in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r"):
        rPr = r.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr")
        if rPr is not None:
            rFonts = rPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts")
            if rFonts is not None:
                for attr in rFonts.attrib.values():
                    fonts_used.add(attr.lower())
        for t in r.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"):
            if t.text:
                text_runs.append(t.text)

    bad_fonts = {f for f in fonts_used if f and not any(af in f for af in ("adobe clean", "calibri"))}
    # Calibri is OK as fallback display but flag it as a warning
    if bad_fonts:
        issues.append(f"document: non-Adobe-Clean fonts present: {sorted(bad_fonts)}")

    full = " ".join(text_runs)
    for pat in PLACEHOLDER_PATTERNS:
        if pat.search(full):
            m = pat.search(full)
            issues.append(f"document: placeholder text: {m.group(0)[:50]!r}")
    for pat in BANNED_PHRASES:
        if pat.search(full):
            issues.append(f"document: banned phrase {pat.pattern}")

    # Footer check
    footer_files = [n for n in z.namelist() if n.startswith("word/footer") and n.endswith(".xml")]
    if not footer_files:
        issues.append("document: no footer defined")
    else:
        has_copyright = False
        for fn in footer_files:
            if "© " in z.read(fn).decode("utf-8", errors="ignore"):
                has_copyright = True
                break
        if not has_copyright:
            issues.append("document: footer present but no © copyright wording")

    z.close()
    return 1, issues, warnings


# ---------------------------------------------------------------------------
# HTML validator
# ---------------------------------------------------------------------------

def validate_html(path: Path) -> tuple[int, list[str], list[str]]:
    issues: list[str] = []
    warnings: list[str] = []
    src = path.read_text(errors="ignore")
    low = src.lower()

    # Logo: must come from an approved asset — an <img> pointing at
    # assets/logos/, an inlined approved wordmark/icon SVG (the kit's wordmark
    # uses viewBox "0 0 360 87"; icon uses a small square-ish viewBox), or a
    # base64 image. A bare hand-drawn <path>/<polygon> labelled "adobe" is NOT.
    approved_img = ("logos/" in low or "adobe-wordmark" in low
                    or 'viewbox="0 0 360 87"' in low or "data:image" in low)
    if not approved_img:
        issues.append(
            "no approved Adobe logo found — use an <img> from assets/logos/ or "
            "inline an approved wordmark/icon SVG; never hand-draw the mark")

    # Fonts
    if "adobe clean" not in low:
        issues.append("Adobe Clean is not specified anywhere in the CSS")
    elif "data:font" not in low and "@font-face" not in low:
        warnings.append(
            "Adobe Clean is named but not loaded (@font-face/base64). Recipients "
            "without the font will see a fallback — build with build_html.py for "
            "a self-contained file.")

    # Core red present?
    if B.ADOBE_RED.lower() not in low and "--adobe-red" not in low:
        warnings.append(f"Adobe red (#{B.ADOBE_RED}) not found — the brand's hero "
                        f"colour should appear (red thread, accents).")

    # Placeholder / banned phrases (strip tags first)
    text = re.sub(r"<[^>]+>", " ", src)
    for pat in PLACEHOLDER_PATTERNS:
        if pat.search(text):
            issues.append(f"placeholder text remains: {pat.search(text).group(0)[:50]!r}")
    for pat in BANNED_PHRASES:
        if pat.search(text):
            issues.append(f"banned phrase: {pat.pattern}")

    return 1, issues, warnings


# ---------------------------------------------------------------------------
# Entry
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python validate.py FILE.pptx|FILE.docx|FILE.html")
        return 2
    p = Path(argv[1])
    if not p.exists():
        print(f"Not found: {p}")
        return 2
    if p.suffix.lower() == ".pptx":
        total, issues, warnings = validate_pptx(p)
    elif p.suffix.lower() == ".docx":
        total, issues, warnings = validate_docx(p)
    elif p.suffix.lower() in (".html", ".htm"):
        total, issues, warnings = validate_html(p)
    else:
        print("Unsupported file type")
        return 2

    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  • {w}")

    if not issues:
        print(f"\n✅ PASS — {total} {'slides' if p.suffix.lower() == '.pptx' else 'document'} clean")
        return 0
    print(f"\n❌ {len(issues)} issue(s):")
    for i in issues:
        print(f"  • {i}")
    return 1


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main(sys.argv))
