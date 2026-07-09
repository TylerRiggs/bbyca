# Adobe Brand — Do's and Don'ts

Quick-reference list of everything that breaks brand compliance. Use as a final pass before delivering a deck or document.

---

## Marks (wordmark, icon, lockups)

| ❌ Don't | ✅ Do |
|---|---|
| Recreate the wordmark by typing "Adobe" in Adobe Clean | Use the approved file from Brand Center |
| Use the icon to replace the letter "A" in any word | Keep words and the icon visually separate |
| Lock up the icon next to the wordmark | The wordmark already contains the icon |
| Use the Adobe Experience Cloud logo as the Adobe icon | They are different marks |
| Apply effects: drop shadow, bevel, glow, 3D | Flat reproduction only |
| Use gradients or image-fills inside the wordmark | Solid color only |
| Recolor the wordmark to any non-approved color | Red, white, or (for B&W contexts) black only |
| Combine the corporate logo with the wordmark | Never lock them up together |
| Crop, distort, or alter spacing of the wordmark | Use approved files at correct aspect |
| Place the wordmark on busy, low-contrast imagery | Saturated/dark image → white wordmark. Light/warm image → red, ensuring contrast |
| Use the wordmark below minimum size | Screen 16px height min; print 0.75" / 19mm wide |
| Use the legacy "Adobe Systems" / red "A" logo | Retired — use the current wordmark |
| Add ™ or ® to "Adobe" or product names | Adobe does not bug its marks in materials |

---

## Color

| ❌ Don't | ✅ Do |
|---|---|
| Use any red other than `#EB1000` | Always Adobe red `#EB1000` |
| Use Adobe red for body text | Body is black, dark gray, or white only |
| Use Adobe red for chart bars/lines | Gray-scale chart + one accent from extended palette |
| Use `#999999` or `#666666` for footers | `#191919` — extracted from Adobe's master |
| Apply transparency or tones to brand colors | Solid full saturation only |
| Use color gradients | Flat fills only |
| Stack 3+ extended palette colors per slide | One accent color per chart/diagram |
| Use pink for "women" or blue for "men" | Avoid color stereotypes — let context decide |
| Match a competitor's signature color | Pick a different extended-palette color |

---

## Typography

| ❌ Don't | ✅ Do |
|---|---|
| Use Arial, Calibri, Helvetica, or any non-Adobe-Clean font in code | Specify `Adobe Clean` or `Adobe Clean Display Black` — user remaps if missing |
| Write headlines in ALL CAPS | Sentence case, period or question mark |
| Write headlines in Title Case (Every Word Capitalized) | Sentence case |
| Bold + italicize + underline body text for emphasis | Use weight (bold) sparingly; no underlines |
| Color body text in Adobe red | Black / white / dark gray for body only |
| Use ≥4 bullet levels | 3 levels max in slides, 2 max in docs |
| Set body text below 10pt in documents or 11pt in slides | 10pt doc / 11pt slide minimums |
| Mix Adobe Clean Regular with non-Adobe Clean weights | Stay within the official weight set |
| Use SemiLight outside of Experience Cloud pull-quotes | SemiLight is reserved |
| Track headlines at 0 | Track to -20 (or -31 in Adobe XD/Express) |
| Use leading > 110% for headlines | 90% for headlines, 110% for subheads |

---

## Layout

| ❌ Don't | ✅ Do |
|---|---|
| Omit the red left thread | Always present, except on full-red title slides |
| Resize, recolor, or move the red thread | `x=0, y=0, w=0.14", h=7.5"`, fill `#EB1000`, fixed |
| Place body content overlapping the thread (left of 0.14") | Content starts at x ≥ 0.67" |
| Center-align body text | Left-align body. Center only on title/cover slides |
| Crowd a slide with > 7 bullets | Restructure into multi-column or split into two slides |
| Use full-bleed images that cover the thread | Image right-edge can bleed; left edge respects the thread |
| Add decorative borders, dividers, or rules | The red thread IS the brand's structural element |
| Use 4:3 aspect ratio | 16:9 widescreen (13.33" × 7.5") |
| Center the title vertically on content slides | Title at top placeholder `y=0.29"` |
| Skip the footer/copyright on internal decks | Always include unless the user asks otherwise |

---

## Imagery

| ❌ Don't | ✅ Do |
|---|---|
| Pull stock photos without rights | Use Adobe Stock with proper license, or supplied imagery |
| Add the Adobe lens to arbitrary images | Lens only on images supplied with it — contact brand@adobe.com for new applications |
| Use heavy/cluttered device mockups | Simplified white/dark gray devices only |
| Use red or saturated colors for device frames | White devices on light; dark gray devices on dark |
| Apply filters, vignettes, color shifts to brand imagery | Use imagery as supplied |
| Mix the simplified container style with realistic UI in one piece | Pick one — simplified for marketing, realistic UI for instructional |
| Layer the wordmark/icon onto an image without contrast check | Always pass WCAG AAA: 4.5:1 for large text, 7:1 for body |

---

## Voice / writing

| ❌ Don't | ✅ Do |
|---|---|
| Write in corporate speak / buzzwords | "People talking to people" — conversational |
| Be vague or ambiguous | Be confident and specific |
| Personify AI ("the magic of AI", "AI creates for you") | Frame AI as a tool that empowers humans |
| Frame AI as a replacement for creativity | AI enhances creativity; the user is the creator |
| Use "the power of" / "transformational" / "synergy" | Direct, concrete phrasing |
| Be cute, ironic, or sarcastic | Confident, warm, optimistic |
| Be elitist, gatekeep, or alienate non-experts | Inclusive, approachable |
| Be political, controversial, or take a stance on social issues outside Adobe's stated positions | Stay neutral |
| Write "Adobe Inc.", "Adobe Systems", "Adobe Incorporated" in copy | Just "Adobe" everywhere except legal contracts |
| Localize Adobe product names, cloud names, taglines for marketing identity | Product names stay English globally |
| Use ™ or ® bugs | No bugs |

---

## Mechanical / compliance

| ❌ Don't | ✅ Do |
|---|---|
| Omit the copyright line | `© [year] Adobe. All Rights Reserved. Adobe Confidential.` in footer |
| Drop "Adobe Confidential" without checking | Internal docs always include it; external content may omit (confirm with user) |
| Skip the trademark attribution paragraph in legal/end matter | Include it for any Adobe mark referenced |
| Save as `.ppt` (legacy format) | Always `.pptx` |
| Save as `.doc` (legacy format) | Always `.docx` |
| Embed proprietary Adobe Clean font in distributed files | Specify font name; do not bundle Adobe Clean — it's not redistributable |
| Use uneven file names | `adobe-[account-or-topic]-[type].pptx` (kebab-case) |

---

## Red flags to catch in QA

Before delivering, scan for:

1. **Wrong red.** Search `EB1000` — make sure every fill that should be Adobe red is exactly that hex.
2. **Wrong gray.** No `999999`, `666666`, `808080`, or `CCCCCC` in body text. Footers must be `#191919`.
3. **Missing red thread.** Every slide except full-red title slides must have it.
4. **Missing footer.** Every slide except optionally the cover must have the legal line.
5. **Wrong font.** Search font names — must be `Adobe Clean` or `Adobe Clean Display Black`. No Calibri/Arial.
6. **Title case / ALL CAPS.** Headlines should read like sentences.
7. **Placeholder text left in.** No "Click to edit", no "Lorem ipsum", no `{{placeholder}}`.
8. **Trademark bugs.** No ™ or ® on Adobe marks.
9. **"Adobe Inc."** anywhere in body copy.
10. **Bullets > 3 levels.** Restructure.

`scripts/validate.py` automates steps 1–7 and 10.
