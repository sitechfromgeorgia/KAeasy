---
name: georgian-writing
description: Use before writing or editing any Georgian (ka) text a person will read - article, headline, post, video script, UI string, report or message to Edo. Entry point of the kaeasy skills; tells you which sibling skill to load.
---

# Georgian writing (entry point)

Edo reads what agents publish and catches single mistakes. Your model's Georgian is weaker than its English:
it translates English word order, drops the ergative, and borrows English idioms. These skills make up for that
with rules and many wrong → right examples. Follow them literally; when a rule and your instinct disagree, the
rule wins.

## Workflow (every public Georgian text)

1. `ka_mistakes` (limit 20): read the fleet's recent mistakes. Do not repeat them.
   `examples/fleet-mistakes.md` has 30+ real ones from our own Shorts reviews.
2. Load the sibling skill for the job (table below). Read its `examples/` before drafting.
3. Draft. Think in Georgian sentence structure: actor + object + verb at the end.
4. Self-edit with `kaeasy:georgian-proofread` (fact freeze, rewrite, copy desk). Same model, no extra cost.
5. `ka_lint` with the right `mode`, `strict: true` as the gate (`fields` for JSON scripts, e.g.
   `{"say": "speech", "*": "social"}`). `ka_fix` repairs the mechanical findings; fix the rest yourself and run
   `ka_lint` again. Voice text: `ka_speech` (see `kaeasy:georgian-speech`).
6. When a human or a review corrects you, call `ka_learn` once per fix (short phrase, not the whole text).

## Which skill

| Job | Load |
|---|---|
| Any text: case endings, verbs, agreement, postpositions | `kaeasy:georgian-grammar` |
| Sounds translated, calques, AI filler, passive voice | `kaeasy:georgian-natural-style` |
| Brands, acronyms, countries, numbers, dates, quotes, dashes | `kaeasy:georgian-names-numbers` |
| News article or headline (tbilisi.today, sitech.ge blog) | `kaeasy:georgian-news` |
| Social post, ad, card, on-screen video text | `kaeasy:georgian-social` |
| Buttons, labels, errors, statuses | `kaeasy:georgian-ui` |
| Text that will be read aloud by TTS (`speech_text`) | `kaeasy:georgian-speech` |
| Reviewing or fixing someone's Georgian | `kaeasy:georgian-proofread` |

## The ten rules broken most often

1. Aorist transitive verb → subject with **-მა / -მ**: ✅ `კომპანიამ გამოაცხადა` ❌ `კომპანია გამოაცხადა`.
2. Aorist transitive verb → direct object in the **nominative**: ✅ `ახალი მოდელი გამოუშვა` ❌ `ახალ მოდელს გამოუშვა`.
3. After a number, the noun is **singular**, and so is the verb: ✅ `სამმა კომპანიამ განაცხადა` ❌ `სამმა კომპანიებმა განაცხადეს`.
4. Brands stay in **Latin**, case ending after a **hyphen**: ✅ `Microsoft-მა`, `OpenAI-ს`, `GPU-ები` ❌ `მაიკროსოფტმა`, `Microsoftმა`.
5. Countries and cities in **Georgian**: ✅ `გერმანიაში` ❌ `Germany-ში`.
6. No calques: ✅ `მიიღო გადაწყვეტილება`, `შეხვედრა გაიმართა` ❌ `გააკეთა გადაწყვეტილება`, `შეხვედრამ ადგილი მიიღო`.
7. Active voice with a named actor: ✅ `მკვლევრებმა აღმოაჩინეს` ❌ `აღმოჩენილ იქნა მკვლევრების მიერ`.
8. No empty openers: ❌ `მნიშვნელოვანია აღინიშნოს, რომ`, `აღსანიშნავია, რომ`, `თანამედროვე სამყაროში`.
9. Typography: `„…“` quotes, decimal comma `3,5%`, no space before `%`, **no — or –** (Edo's rule; use a comma, colon or hyphen).
10. Keep the source's certainty: `შესაძლოა`, `ვარაუდობს`, `აცხადებს` never become a fact.

## Language of these skills

Instructions are in English (your model follows English instructions better); every example is real Georgian.
Write your output in Georgian unless asked otherwise. Never translate Georgian examples back into English in
your head; copy their structure.
