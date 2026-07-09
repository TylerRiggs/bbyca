# Deck brief template

Drop this file in any project, fill in the sections you want, then say to Claude:

> Use the adobe-presentation skill to build a deck from `/path/to/this-brief.md`.

Claude will translate the brief into the JSON spec, run `build_deck.py`, and validate the output. You can leave sections out — Claude infers reasonable defaults (e.g., agenda from your section list, thank-you from your contact info).

---

## Meta

- **File name to produce:** `adobe-<account>-<type>.pptx` (e.g., `adobe-acme-discovery-deck.pptx`)
- **Audience:** (e.g., CMO + CFO at Acme Corp; technical buyers; internal sales kickoff)
- **Tone:** Confident / Aspirational / Encouraging  *(pick one; default: Confident)*
- **Confidential:** Yes / No  *(default: Yes — sets the footer to "Adobe Confidential")*
- **Length target:** ~N slides  *(skill works well for 8–25 slides; longer decks should be split)*

---

## Cover

- **Headline:** *(sentence case, ≤ 3 lines at 77pt — short and declarative)*
- **Subtitle / context:** *(one line — who, what, when)*
- **Cover style:** red / white / dark  *(default: red)*

---

## Agenda

List the section names. Claude will assign times if you provide them, otherwise omit the time column.

1. Section name — duration
2. Section name — duration
3. ...

---

## Sections

For each section, give Claude a header plus the substance. Anything below works — narrative paragraphs, bullets, comparison pairs. Claude picks the layout (`section divider`, `content`, `two-col`, `three-col`, `quote`, `four-col`, etc.) based on what fits.

### Section 1: [name]

What you want said here. Bullets, prose, key stats, customer quotes — whatever you have. Examples:

- Top-level point one.
- Top-level point two.
  - Supporting detail.
- Top-level point three.

If you have a "before vs. after" or "their world vs. ours" idea, write it as a pair:

**Before:** What's broken today.
**After:** What it looks like with Adobe.

If you have a customer quote, drop it in as a blockquote — Claude will use the quote layout:

> "Adobe gave us a 7x lift in conversion in the first quarter."
> — VP, Digital, Acme Co.

### Section 2: [name]

...

---

## Proof / numbers

Any specific stats, customer outcomes, comparisons. Claude will pick a multi-column or table layout.

| Industry | Outcome | Customer |
|---|---|---|
| Retail | 3.2x conversion lift | Top-10 US retailer |
| Financial | 47% CPA reduction | ... |

---

## Next steps / ask

What you want the audience to do. Phase plan, timeline, the specific decision you're asking for.

---

## Closing

- **Closing slide title:** (default: "Thank you.")
- **Contact info:** First Last  |  first.last@adobe.com  |  Title
