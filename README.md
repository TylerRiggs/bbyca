# bbyca

Tools in this repository:

- [`microsite-editor/`](microsite-editor/README.md) — a self-contained,
  no-install WYSIWYG editor (`editor.html`) that lets non-technical sellers
  visually edit AI-generated HTML microsites and save a clean file that can
  round-trip back into Claude.
- [`adobe-presentation/`](adobe-presentation/SKILL.md) — a Claude skill for
  Adobe-branded collateral (details below).

# adobe-presentation skill

A Claude skill that produces authentically Adobe-branded `.pptx`, `.docx`, and
HTML collateral — brand palette, Adobe Clean type system, red thread, approved
wordmark placement, and **structured-visual slide layouts** (styled tables,
KPI stat cards, card grids, comparison panels, process timelines) so output
looks designed, not generated.

Entry point: [`adobe-presentation/SKILL.md`](adobe-presentation/SKILL.md).

## Note on licensed assets

`adobe-presentation/assets/fonts/` (Adobe Clean OTFs) and
`adobe-presentation/assets/logos/` (approved wordmark/icon files) are
**licensed, internal-only Adobe assets and are deliberately not committed**
to this public repository (see the skill's "Packaging & distribution"
section). The scripts degrade gracefully without them, but for on-brand
output restore both folders from the internally distributed skill bundle
before use.
