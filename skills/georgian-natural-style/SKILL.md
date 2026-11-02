---
name: georgian-natural-style
description: Make Georgian (ka) text sound written by a Georgian, not translated - calques from English and Russian, AI filler, passive voice, noun chains, word order. Load when a draft sounds robotic or translated.
---

# Natural Georgian, not translated Georgian

Weak models write English sentences with Georgian words. Rewrite for **meaning**, never for word order.

## Five rewrite moves

1. **Actor + verb at the end.** `Amazon-მა ახალი მოდელი გამოუშვა.` Not `გამოუშვა Amazon-მა ახალი მოდელი.`
2. **Active voice with a named actor.** ❌ `გადაწყვეტილება იქნა მიღებული` → ✅ `მთავრობამ გადაწყვიტა`.
   Passive only when the actor is unknown: `სერვერი გატეხეს` (❌ `სერვერი გატყდა`: გატყდა is for glass and bones).
3. **A verb instead of a noun phrase.** ❌ `განხორციელდა აპლიკაციის განახლება` → ✅ `აპლიკაცია განახლდა`.
   ❌ `არსებობს საჭიროება` → ✅ `საჭიროა`.
4. **One idea per sentence**, about 8-20 words. Split at `და რომელიც`, `რაც იმას ნიშნავს, რომ`.
5. **Delete what adds no fact**: empty openers, decorative connectors, hype.

## Calques (most common)

| ❌ calque | ✅ Georgian |
|---|---|
| ადგილი მიიღო (took place) | მოხდა / გაიმართა / შედგა |
| გააკეთა გადაწყვეტილება (made a decision) | მიიღო გადაწყვეტილება / გადაწყვიტა |
| თამაშობს მნიშვნელოვან როლს | მნიშვნელოვანია / დიდ როლს ასრულებს |
| იქნა გაკეთებული / იქნა მიღებული | გაკეთდა / მიიღეს |
| არის საჭიროება / არსებობს საჭიროება | საჭიროა |
| ამ მომენტში (at this moment) | ამჟამად / ახლა |
| დიდი რაოდენობით (a lot of) | ბევრი |
| შედეგად იმისა, რომ | იმის გამო, რომ |
| თამაშის შემცვლელი (game changer) | გარდამტეხი / რადიკალურად ცვლის |
| საშუალებას აძლევს X-ს (allows X) | X-ს საშუალებას აძლევს / X-ს შეუძლია |
| დაფუძნებულია X-ზე (based on) | X-ს ეყრდნობა |

Full list with Russian calques and context: `references/calques.md`.

## AI filler (delete or replace with the fact)

`მნიშვნელოვანია აღინიშნოს, რომ` · `აღსანიშნავია, რომ` · `ამ კონტექსტში` · `თანამედროვე სამყაროში` ·
`როგორც ცნობილია` · `ციფრულ ეპოქაში` · `ახალ ერას იწყებს` · `ეს ნათლად აჩვენებს` · `საბოლოო ჯამში` (when it
sums up nothing). More in `references/ai-filler.md`.

## Connectors are claims

`ამიტომ`, `შედეგად`, `თუმცა`, `ამასთან`, `მიუხედავად ამისა` state a logical relation. Use one only when the source
says that relation exists. Do not glue sentences with them for rhythm.

## Examples

- `references/collocations.md`: 80 natural vs wrong verb + noun pairs (გადაწყვეტილების მიღება, განცხადების გაკეთება).
- `examples/rewrites.md`: 80+ translated-sounding sentences and their natural rewrites. Read them before editing.
