#!/usr/bin/env python3
"""
Embed Adobe Clean into a finished .pptx / .docx so the file renders correctly
on machines that don't have the proprietary font installed.

Why this exists
---------------
The builder scripts write the real Adobe font *names* into every run, but a
name alone only renders if the recipient has the font. Embedding ships the
actual glyphs inside the file. The Adobe Clean OTFs carry fsType=8 (editable
embedding permitted), so this is licensed-compatible for internal Adobe use.

Two formats, two mechanisms
---------------------------
- PPTX: PowerPoint embeds fonts as raw OpenType in `ppt/fonts/*.fntdata`,
  referenced from `presentation.xml` via a `<p:embeddedFontLst>`. CFF/OpenType
  (OTTO) embeds fine, so we embed the .otf bytes verbatim.
- DOCX: Word will NOT embed CFF/OpenType; it only embeds TrueType, and the
  bytes must be lightly "obfuscated" (first 32 bytes XORed with a GUID key).
  So we convert each OTF -> TTF (fontTools + cu2qu) in memory, obfuscate, and
  write `word/fonts/*.odttf` referenced from `fontTable.xml`.

Public API
----------
    embed_fonts(path)            # dispatches on extension, returns list[str] embedded
    embed_pptx_fonts(path)
    embed_docx_fonts(path)

Run standalone:
    python scripts/embed_fonts.py output.pptx
"""
from __future__ import annotations

import io
import os
import re
import shutil
import sys
import uuid
import zipfile
from pathlib import Path

import brand as B

FONTS_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"

# Which family names to embed, and the style->file mapping for each.
# Keys are the typeface names that the builder scripts write into runs.
EMBED_PLAN = {
    B.FONT_BODY: {                       # "Adobe Clean"
        "regular":    "AdobeClean-Regular.otf",
        "bold":       "AdobeClean-Bold.otf",
        "italic":     "AdobeClean-It.otf",
        "boldItalic": "AdobeClean-BoldIt.otf",
    },
    B.FONT_DISPLAY: {                    # "Adobe Clean Black" (headline weight)
        "regular":    "AdobeClean-Black.otf",
        "italic":     "AdobeClean-BlackIt.otf",
    },
}


# ===========================================================================
# PPTX
# ===========================================================================

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

# Order of children allowed *after* embeddedFontLst in CT_Presentation. We
# insert embeddedFontLst immediately before the first of these we find.
_AFTER_EMBED = ("custShowLst", "photoAlbum", "custDataLst", "kinsoku",
                "defaultTextStyle", "modifyVerifier", "extLst")


def embed_pptx_fonts(path: Path) -> list[str]:
    path = Path(path)
    src = zipfile.ZipFile(path, "r")
    names = src.namelist()
    items = {n: src.read(n) for n in names}
    src.close()

    pres = items["ppt/presentation.xml"].decode("utf-8")
    rels = items["ppt/_rels/presentation.xml.rels"].decode("utf-8")
    cts = items["[Content_Types].xml"].decode("utf-8")

    # next free rId in presentation rels
    existing_ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
    next_id = (max(existing_ids) + 1) if existing_ids else 1

    font_files: list[tuple[str, bytes]] = []   # (zip path, bytes)
    embedded_font_xml = []
    embedded: list[str] = []
    font_idx = 1

    for typeface, styles in EMBED_PLAN.items():
        slot_xml = [f'<p:font typeface="{typeface}"/>']
        any_slot = False
        for slot in ("regular", "bold", "italic", "boldItalic"):
            fname = styles.get(slot)
            if not fname:
                continue
            fpath = FONTS_DIR / fname
            if not fpath.exists():
                continue
            zip_path = f"ppt/fonts/font{font_idx}.fntdata"
            font_files.append((zip_path, fpath.read_bytes()))
            rid = f"rId{next_id}"
            rels = rels.replace(
                "</Relationships>",
                f'<Relationship Id="{rid}" '
                f'Type="{R_NS}/font" Target="fonts/font{font_idx}.fntdata"/>'
                "</Relationships>",
            )
            slot_xml.append(f'<p:{slot} r:id="{rid}"/>')
            next_id += 1
            font_idx += 1
            any_slot = True
        if any_slot:
            embedded_font_xml.append(
                "<p:embeddedFont>" + "".join(slot_xml) + "</p:embeddedFont>"
            )
            embedded.append(typeface)

    if not embedded_font_xml:
        return []

    embed_lst = (f'<p:embeddedFontLst xmlns:p="{P_NS}" xmlns:r="{R_NS}">'
                 + "".join(embedded_font_xml) + "</p:embeddedFontLst>")

    # Ensure the embed flags on the root element (idempotent — the default
    # python-pptx template already carries saveSubsetFonts).
    if "saveSubsetFonts" in pres:
        pres = re.sub(r'saveSubsetFonts="[^"]*"', 'saveSubsetFonts="0"', pres, count=1)
    else:
        pres = re.sub(r"<p:presentation\b",
                      '<p:presentation saveSubsetFonts="0"', pres, count=1)
    if "embedTrueTypeFonts" not in pres:
        pres = re.sub(r"<p:presentation\b",
                      '<p:presentation embedTrueTypeFonts="1"', pres, count=1)

    # Insert embeddedFontLst at the schema-correct position: after notesSz
    # (and after sldSz), before custShowLst/defaultTextStyle/extLst/etc.
    inserted = False
    for tag in _AFTER_EMBED:
        m = re.search(rf"<p:{tag}[ />]", pres)
        if m:
            pres = pres[:m.start()] + embed_lst + pres[m.start():]
            inserted = True
            break
    if not inserted:
        # fall back: right after notesSz close, else before </p:presentation>
        m = re.search(r"</p:notesSz>|<p:notesSz[^>]*/>", pres)
        if m:
            pres = pres[:m.end()] + embed_lst + pres[m.end():]
        else:
            pres = pres.replace("</p:presentation>", embed_lst + "</p:presentation>")

    # content-type default for .fntdata
    if "fntdata" not in cts:
        cts = cts.replace(
            "</Types>",
            '<Default Extension="fntdata" '
            'ContentType="application/x-fontdata"/></Types>',
        )

    items["ppt/presentation.xml"] = pres.encode("utf-8")
    items["ppt/_rels/presentation.xml.rels"] = rels.encode("utf-8")
    items["[Content_Types].xml"] = cts.encode("utf-8")
    for zip_path, data in font_files:
        items[zip_path] = data

    _rewrite_zip(path, items)
    return embedded


# ===========================================================================
# DOCX
# ===========================================================================

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _otf_to_ttf_bytes(otf_path: Path) -> bytes:
    """Convert a CFF/OpenType font to TrueType outlines in memory."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.ttGlyphPen import TTGlyphPen
    from cu2qu.pens import Cu2QuPen

    font = TTFont(str(otf_path))
    if "glyf" in font:  # already TrueType
        buf = io.BytesIO(); font.save(buf); return buf.getvalue()

    glyph_set = font.getGlyphSet()
    glyf_glyphs = {}
    from fontTools.ttLib.tables._g_l_y_f import table__g_l_y_f, Glyph
    from fontTools.ttLib.tables._g_l_y_f import GlyphCoordinates  # noqa

    # Build TrueType glyf table from the CFF charstrings.
    upm = font["head"].unitsPerEm
    max_err = upm / 1000.0
    glyph_order = font.getGlyphOrder()
    for gname in glyph_order:
        pen = TTGlyphPen(glyph_set)
        cu2qu = Cu2QuPen(pen, max_err, reverse_direction=True)
        glyph_set[gname].draw(cu2qu)
        glyf_glyphs[gname] = pen.glyph()

    glyf = table__g_l_y_f()
    glyf.glyphs = glyf_glyphs
    glyf.glyphOrder = glyph_order
    font["glyf"] = glyf

    # loca is generated on compile from glyf. Add minimal required tables.
    from fontTools.ttLib.tables._l_o_c_a import table__l_o_c_a
    font["loca"] = table__l_o_c_a()
    # maxp must be upgraded from CFF's v0.5 to TrueType's v1.0, which carries
    # extra fields. glyf compile recalculates maxPoints/maxContours; the rest
    # we set to safe zeros (no hinting in the converted outlines).
    maxp = font["maxp"]
    maxp.tableVersion = 0x00010000
    for fld, val in (("maxZones", 1), ("maxTwilightPoints", 0), ("maxStorage", 0),
                     ("maxFunctionDefs", 0), ("maxInstructionDefs", 0),
                     ("maxStackElements", 0), ("maxSizeOfInstructions", 0),
                     ("maxComponentElements", 0), ("maxComponentDepth", 0),
                     ("maxPoints", 0), ("maxContours", 0),
                     ("maxCompositePoints", 0), ("maxCompositeContours", 0)):
        if not hasattr(maxp, fld):
            setattr(maxp, fld, val)
    # Drop CFF
    for t in ("CFF ", "CFF2", "VORG"):
        if t in font:
            del font[t]
    font.sfntVersion = "\x00\x01\x00\x00"
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def _obfuscate(font_bytes: bytes, guid: str) -> bytes:
    """Word's font obfuscation: XOR first 32 bytes with the 16-byte GUID key
    (applied twice)."""
    hexstr = guid.replace("-", "").replace("{", "").replace("}", "")
    key = bytes.fromhex(hexstr)            # 16 bytes
    key = key[::-1]                        # Word uses the reversed byte order
    data = bytearray(font_bytes)
    for i in range(32):
        data[i] ^= key[i % 16]
    return bytes(data)


def embed_docx_fonts(path: Path) -> list[str]:
    path = Path(path)
    src = zipfile.ZipFile(path, "r")
    items = {n: src.read(n) for n in src.namelist()}
    src.close()

    cts = items["[Content_Types].xml"].decode("utf-8")
    settings = items.get("word/settings.xml", b"").decode("utf-8")
    if not settings:
        return []

    font_table_rels_path = "word/_rels/fontTable.xml.rels"
    fonttable_path = "word/fontTable.xml"

    rels = items.get(font_table_rels_path, (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{PR_NS}"></Relationships>'
    ).encode("utf-8")).decode("utf-8")

    fonttbl = items.get(fonttable_path, (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:fonts xmlns:w="{W_NS}" '
        f'xmlns:r="{R_NS}"></w:fonts>'
    ).encode("utf-8")).decode("utf-8")

    existing_ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
    next_id = (max(existing_ids) + 1) if existing_ids else 1

    embedded: list[str] = []
    font_idx = 1
    new_font_entries = []
    SLOT_TAG = {"regular": "embedRegular", "bold": "embedBold",
                "italic": "embedItalic", "boldItalic": "embedBoldItalic"}

    for typeface, styles in EMBED_PLAN.items():
        embed_xml = []
        for slot in ("regular", "bold", "italic", "boldItalic"):
            fname = styles.get(slot)
            if not fname:
                continue
            fpath = FONTS_DIR / fname
            if not fpath.exists():
                continue
            ttf = _otf_to_ttf_bytes(fpath)
            guid = "{" + str(uuid.uuid4()).upper() + "}"
            obf = _obfuscate(ttf, guid)
            odttf_path = f"word/fonts/font{font_idx}.odttf"
            items[odttf_path] = obf
            rid = f"rId{next_id}"
            rels = rels.replace(
                "</Relationships>",
                f'<Relationship Id="{rid}" Type="{R_NS}/font" '
                f'Target="fonts/font{font_idx}.odttf"/></Relationships>',
            )
            embed_xml.append(
                f'<w:{SLOT_TAG[slot]} r:id="{rid}" w:fontKey="{guid}" '
                f'w:subsetted="0"/>'
            )
            next_id += 1
            font_idx += 1
        if embed_xml:
            new_font_entries.append(
                f'<w:font w:name="{typeface}">' + "".join(embed_xml) + "</w:font>"
            )
            embedded.append(typeface)

    if not new_font_entries:
        return []

    fonttbl = fonttbl.replace("</w:fonts>", "".join(new_font_entries) + "</w:fonts>")

    # settings.xml needs the embed switch (must be early in the element order;
    # placing it right after the opening tag is schema-tolerant for this flag).
    if "embedTrueTypeFonts" not in settings:
        settings = re.sub(r"(<w:settings\b[^>]*>)",
                          r"\1<w:embedTrueTypeFonts/>", settings, count=1)

    # content types: declare fontTable part (if newly created) + odttf default
    if "fontTable.xml" not in cts:
        cts = cts.replace(
            "</Types>",
            '<Override PartName="/word/fontTable.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.fontTable+xml"/></Types>',
        )
    if "obfuscatedFont" not in cts:
        cts = cts.replace(
            "</Types>",
            '<Default Extension="odttf" ContentType="application/'
            'vnd.openxmlformats-officedocument.obfuscatedFont"/></Types>',
        )

    # ensure document.xml.rels references fontTable (Word auto-includes it when
    # the part exists, but the relationship must be present)
    doc_rels_path = "word/_rels/document.xml.rels"
    doc_rels = items[doc_rels_path].decode("utf-8")
    if "fontTable.xml" not in doc_rels:
        d_ids = [int(m) for m in re.findall(r'Id="rId(\d+)"', doc_rels)]
        d_rid = f"rId{(max(d_ids)+1) if d_ids else 1}"
        doc_rels = doc_rels.replace(
            "</Relationships>",
            f'<Relationship Id="{d_rid}" '
            f'Type="{R_NS}/fontTable" Target="fontTable.xml"/></Relationships>',
        )
        items[doc_rels_path] = doc_rels.encode("utf-8")

    items["[Content_Types].xml"] = cts.encode("utf-8")
    items["word/settings.xml"] = settings.encode("utf-8")
    items[fonttable_path] = fonttbl.encode("utf-8")
    items[font_table_rels_path] = rels.encode("utf-8")

    _rewrite_zip(path, items)
    return embedded


# ===========================================================================
# shared
# ===========================================================================

def _rewrite_zip(path: Path, items: dict[str, bytes]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items.items():
            z.writestr(name, data)
    os.replace(tmp, path)


def embed_fonts(path: Path) -> list[str]:
    path = Path(path)
    if path.suffix.lower() == ".pptx":
        return embed_pptx_fonts(path)
    if path.suffix.lower() == ".docx":
        return embed_docx_fonts(path)
    raise ValueError(f"Unsupported file for font embedding: {path}")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python embed_fonts.py FILE.pptx|FILE.docx")
        return 2
    p = Path(argv[1])
    embedded = embed_fonts(p)
    if embedded:
        print(f"✓ Embedded into {p.name}: {', '.join(embedded)}")
    else:
        print(f"! No fonts embedded into {p.name}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main(sys.argv))
