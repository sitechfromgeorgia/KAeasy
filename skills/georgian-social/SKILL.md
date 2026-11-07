---
name: georgian-social
description: Georgian (ka) copy for social posts, ads, design cards and on-screen video text (SiTech Shorts, Postiz, Instagram, Facebook, TikTok) - register, hooks, short lines, calque traps. Load before writing any social or design copy.
---

# Georgian social and design copy

A line on a card or a short has no paragraph around it to rescue it. One unclear phrase reads as a mistake.

## Register

- Speak to the reader as `შენ`, consistently: `გამოიწერე`, `რას ფიქრობ?`, `ნახე`. Never mix with `თქვენ`.
  (Brand pages that chose `თქვენ` keep it everywhere; check the brand's existing posts.)
- Educated conversational Georgian: direct, warm, clear. Not a translated English marketing voice.
- Closing question in the present: ✅ `შენ რას ფიქრობ?`, `როგორ ფიქრობ?` ❌ `შენ რას იფიქრებ?`.

## Lines

1. **No literal English idioms.** ❌ `ბარათი თავს იხდის` (pays for itself) → ✅ `ხარჯი 2,8 თვეში დაბრუნდა`.
   Test: would someone who has not seen the brief ask `რას ნიშნავს?` Then it is a calque.
2. **A supporting line needs a finite verb.** A headline may be a fragment; a bullet may not:
   ❌ `შაბლონი. ათეულობით ფაილი ტექსტამდე` → ✅ `ათეულობით ფაილი ტექსტად გარდაიქმნება`.
3. **The verb must fit the noun.** Read the (noun, verb) pair alone: ❌ `ხარისხს ზომით აჩვენებს` →
   ✅ `ხარისხს ზომა არ განსაზღვრავს` (say what you mean).
4. Every on-screen line set reads as one grammatical phrase top to bottom. No stray inflected fragment on its
   own line.
5. Video narration: 6-14 words per sentence, one idea each. No `!`, `?!`, `…`, slashes, emoji or dashes in
   narration; a list with a colon: `სამი ფუნქცია: ძიება, თარგმნა და შეჯამება`.

## Facts still matter

Quotes word for word in `„…“` or not at all; numbers exactly as the source; qualifiers stay (`კომპანიის
თქმით`, `შესაძლოა`). Hype words only with a fact behind them.

## When copy comes from a table

If a design is generated from a copy table (e.g. `sitech-social-cards`), fix the table, never the rendered
output, or the next build reverts it.

## Gate

`ka_lint` with `mode: social`, `strict: true`. For Shorts the pipeline's own `ka_check.py` (rules K1-K22 in
`shorts/ka_style.md`) also runs; KAeasy and that rulebook must agree. If they differ, report it.

## Examples

`examples/social-fixes.md`.
