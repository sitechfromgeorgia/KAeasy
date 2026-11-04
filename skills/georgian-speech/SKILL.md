---
name: georgian-speech
description: Turning written Georgian (ka) into speech_text for TTS (Gemini TTS, Azure, edge-tts) - numbers in words with the correct case, Latin brands in Georgian letters, letter-by-letter acronyms, dates, percent. Load when preparing narration text that a voice will read.
---

# Georgian speech text (for TTS)

Two texts exist: `display_text` (screen, follows `kaeasy:georgian-names-numbers`) and `speech_text` (voice,
this skill). Speech text has **no Latin letters and no digits**. `ka_lint` with `mode: speech` enforces that.

**Use the `ka_speech` tool first.** It converts the written text deterministically (numbers with case, times,
percent, money, versions, brands from the approved lexicon, acronyms) and returns `speech`, the Latin names it
could not voice (`unspoken`) and any `ka_lint` findings left. Give it a `say` map for new names
(`{"ARTEX": "არტექსი"}`). Do the conversion by hand only for what it leaves, using the rules below.

## Numbers in words (vigesimal: counts in twenties)

| Digits | Words |
|---|---|
| 11-19 | თერთმეტი, თორმეტი, ცამეტი, თოთხმეტი, თხუთმეტი, თექვსმეტი, ჩვიდმეტი, თვრამეტი, ცხრამეტი |
| 20, 40, 60, 80 | ოცი, ორმოცი, სამოცი, ოთხმოცი |
| 30, 50, 70, 90 | ოცდაათი, ორმოცდაათი, სამოცდაათი, ოთხმოცდაათი |
| 36 | ოცდათექვსმეტი |
| 47 | ორმოცდაშვიდი |
| 100, 125 | ასი, ას ოცდახუთი |
| 200, 500 | ორასი, ხუთასი |
| 1000, 1500 | ათასი, ათას ხუთასი |
| 2026 | ორი ათას ოცდაექვსი |
| 2 250 | ორი ათას ორას ორმოცდაათი (one number, never "two" + "two hundred fifty") |
| 3,5 | სამი მთელი ხუთი მეათედი / სამნახევარი (.5 decimals use …ნახევარი: 1,5 ერთნახევარი, 2,5 ორნახევარი) |

- Inside a compound, non-final components lose their -ი: `ას ოცდახუთი`, `ათას ხუთასი`, `ორი ათას ...`.
- **Case endings on numbers before nouns**: A numeral before a noun declines like an adjective. In the
  dative and adverbial it takes the bare stem without -ს (❌ `ხუთს სერვერს` → ✅ `ხუთ სერვერს`,
  `40%-მდე` → `ორმოც პროცენტამდე`); in the ergative it takes -მა (`ხუთმა სერვერმა`, `ოცდათექვსმეტმა პროცენტმა`);
  in the genitive and instrumental it keeps -ი (`ოცდათექვსმეტი პროცენტის`, `ოცდათექვსმეტი პროცენტით`).
- A number with a suffix: `4-ჯერ` → `ოთხჯერ`, `8-დან` → `რვიდან`, `2012 წელს` → `ორი ათას თორმეტ წელს`,
  `40%-მდე` → `ორმოც პროცენტამდე`.
- Ordinals: `მე-3` → `მესამე`, `მე-20 საუკუნე` → `მეოცე საუკუნე`. Above 100: `180-ე მუხლი` → `ას მეოთხმოცე მუხლი` (not cardinal `ას ოთხმოცი`).
- Dates: Day of the month is cardinal: `22 ნოემბერს` → `ოცდაორ ნოემბერს` (❌ `ოცდამეორე`). Only day 1 is ordinal: `1 ნოემბერს` → `პირველ ნოემბერს`. Full dates: `2026 წლის 22 ნოემბერს` → `ორი ათას ოცდაექვსი წლის ოცდაორ ნოემბერს`.
- Legal primes: `353¹-ე მუხლი` → `სამას ორმოცდამეცამეტე პრიმა მუხლი`.
- Identifiers (`CVE-2026-97631`, `KB5034441`) are never read: say `ხარვეზი` / `განახლება`.

## Latin names in Georgian letters

Spoken as a Georgian presenter says them, case ending glued (no hyphen in speech):
`Microsoft-მა` → `მაიკროსოფტმა`, `NVIDIA-ს` → `ენვიდიას`, `OpenAI-მ` → `ოუფენეიაიმ`, `ChatGPT` →
`ჩატჯიპიტი`, `GitHub-ზე` → `გითჰაბზე`, `YouTube` → `იუთუბი`. A project lexicon wins over your guess
(Shorts: `lexicon_ka.json`, `say` map).

Letter acronyms use **English** letter names, never Russian (❌ ტე, პე, ბე, დე, კა):
A ეი, B ბი, C სი, D დი, E ი, F ეფ, G ჯი, H ეიჩ, I აი, J ჯეი, K ქეი, L ელ, M ემ, N ენ, O ოუ, P პი, Q ქიუ, R არ,
S ეს, T ტი, U იუ, V ვი, W დაბლიუ, X ექს, Y უაი, Z ზედ.
`GPU` → `ჯი პი იუ`, `AI` → `ეი აი`, `macOS` → `მაკ ოუ ეს`. A name said as a word keeps its word: `NASA` → `ნასა`.

## Symbols

`%` → `პროცენტი` (with the case: `პროცენტით`), `$300` → `სამასი დოლარი`, `°C` → `გრადუსი`, `km` → `კილომეტრი`,
`&` → `და`, `/` → rewrite the sentence.

## Examples & References

- `references/dates-numbers-speech.md`: comprehensive spoken dates, ordinals above 100, money, percent, and time.
- `examples/speech-fixes.md`: 60+ written to spoken speech text pairs (numbers, dates, percent, brands, acronyms).

## Prosody

Short sentences (6-14 words), comma where a breath belongs, no `…` or `!`. The TTS reads punctuation literally
as rhythm. Delivery instructions go in the TTS style field, never into the text.

Deeper material: My Projects `knowledge/video-brainstorm/georgian-tts/` (normalization, prosody, brands).
