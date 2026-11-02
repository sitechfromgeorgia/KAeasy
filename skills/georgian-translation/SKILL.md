---
name: georgian-translation
description: Translation protocol for English→Georgian and Russian→Georgian — sentence restructuring, what stays Latin vs transliterated, idioms, units, currencies, quotes, and work titles.
---

# Georgian translation protocol (EN→KA and RU→KA)

Do not translate word-for-word from English or Russian. Machine translators and non-native drafts mirror foreign SVO word order, produce bureaucratic passive chains, and borrow dead metaphors. Restructure each sentence into native, natural Georgian.

## Protocol summary

| Dimension | Rule | ✅ | ❌ |
|---|---|---|---|
| Tech brands & APIs | Keep Latin; hyphenated case ending | `Google-მა`, `Python-ში`, `REST API-ს` | `გუგლმა`, `Pythonში`, `Python ის` |
| Geography | Translate into Georgian | `გერმანიაში`, `საფრანგეთში`, `ტოკიოში` | `Germany-ში`, `Tokyo-ში` |
| Word order | SOV-leaning; verb toward the end | `კომპანიამ გუშინ ახალი მოდელი წარადგინა.` | `კომპანიამ წარადგინა ახალი მოდელი გუშინ.` |
| Voice | Active with named actor | `მეცნიერებმა წყალი აღმოაჩინეს.` | `წყალი აღმოჩენილ იქნა მეცნიერების მიერ.` |
| Idioms | Map to meaning, not literal image | `გადაწყვეტილება ახლა მათზეა.` | `ბურთი მათ მოედანზეა.` |
| False friends | Beware faux cognates | `სინამდვილეში` (actually), `ათწლეული` (decade) | `აქტუალურად` (actually), `დეკადა` (decade) |
| Currencies & units | Spell out currency; decimal comma | `5 მილიონი დოლარი`, `2,5%` | `$5 მილიონი`, `2.5 %` |
| Titles & quotes | Georgian quotes `„…“` | `წიგნი „დიდი გეთსბი“` | `წიგნი "The Great Gatsby"` |

## Step-by-step translation process

1. **Grasp the core proposition:** Identify the real actor, the action, and the recipient/object.
2. **Assign cases correctly:**
   - In the past tense (aorist), transitive verbs take an ergative subject (`-მა / -მ`) and a nominative object: `მკვლევარმა აღმოაჩინა მეთოდი`.
   - Never copy English passive voice (`was done by...` → `...-მა გააკეთა`).
3. **Handle proper names:**
   - Tech companies, programming languages, libraries, models stay in Latin (`Apple-ი`, `Docker-ი`, `iOS-ი`).
   - Countries and cities must be in Georgian (`გერმანია`, `ლონდონი`, `პარიზი`).
   - People are transliterated phonetically (`უილიამ შექსპირი`, `ილონ მასკი`).
4. **Translate idioms for meaning:**
   - `game changer` → `გარდამტეხი სიახლე`
   - `tip of the iceberg` → `პრობლემის მხოლოდ მცირე ნაწილი`
   - `take to the next level` → `შედეგების გაუმჯობესება`
   - RU `иметь в виду` → `გულისხმობა`
   - RU `на самом деле` → `სინამდვილეში`
5. **Format numbers and units:**
   - Singular noun after any number: `10 კომპანია`, `3 თვე`.
   - Currency: `100 000 ლარი`, `1,5 მილიონი დოლარი`.
   - Punctuation: `„…“` quotes; no space before `%` (`15%`).

## Related skills

- Case endings, ergative, and verbs: `kaeasy:georgian-grammar`
- Natural flow, collocations, anti-calque: `kaeasy:georgian-natural-style`
- Proper nouns, brand declension, and typography: `kaeasy:georgian-names-numbers`

## References and examples

- `references/translation-protocol.md`: deep protocol for syntax restructuring, voice, and units.
- `references/false-friends.md`: catalog of English and Russian false friends in Georgian.
- `examples/translation-rewrites.md`: 60+ full source → bad literal → natural Georgian rewrites.

Run `ka_lint` with `mode: article` on final output.
