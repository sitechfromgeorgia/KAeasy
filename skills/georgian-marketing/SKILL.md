---
name: georgian-marketing
description: Georgian (ka) marketing copy — taglines, CTAs, landing pages, ads, and Shorts hooks. Ban English hype calques, enforce natural equivalents, punchy imperatives, and strict length limits.
---

# Georgian marketing copy

Marketing copy in Georgian must be direct, crisp, and grounded in real benefits. Avoid translating English Silicon Valley clichés; Georgian audiences find them inflated and unnatural.

## Core rules

| Element | Rule | ✅ | ❌ |
|---|---|---|---|
| Tagline | 3-6 words, clear benefit | `მარტივი ფინანსური მართვა გუნდისთვის` | `ჩვენ ვცვლით მსოფლიოს ინოვაციით` |
| Hero H1 | Under 8 words, user outcome | `გაზარდე გაყიდვები ერთ ეკრანზე` | `ჩვენი თამაშის შემცვლელი პლატფორმა` |
| CTA | 1-3 words, active verb | `დაიწყე უფასოდ`, `ნახე დემო` | `დააჭირეთ აქ თქვენი საცდელი ვადისთვის` |
| Register | `შენ` (B2C) or `თქვენ` (B2B), strictly one | `სცადე უფასოდ ... დარეგისტრირდი` | `სცადეთ უფასოდ ... დარეგისტრირდი` |
| Video hook | 6-12 words, problem or contrast | `რატომ კარგავს ბიზნესი კლიენტებს პირველივე წუთში?` | `შოკისმომგვრელი საიდუმლო, რომელსაც გიმალავენ!` |
| Proof | Real numbers, singular noun | `10 000 მომხმარებელი`, `20% ზრდა` | `ათასობით მომხმარებლები`, `20 % ზრდა` |

## Ban English hype calques

Replace translated marketing jargon with concrete, native Georgian expressions:

- ❌ `თამაშის შემცვლელი` (game changer) → ✅ `გარდამტეხი სიახლე`, `ახალი სტანდარტი`, `რადიკალურად ცვლის ბაზარს`
- ❌ `შემდეგ დონეზე აყვანა` (take to the next level) → ✅ `შედეგების გაუმჯობესება`, `ხარისხის გაზრდა`
- ❌ `ყველაფერი ერთში` (all-in-one) → ✅ `ერთიანი პლატფორმა`, `სრული გადაწყვეტა`
- ❌ `პოტენციალის განბლოკვა` (unlock potential) → ✅ `შესაძლებლობების სრულად გამოყენება`
- ❌ `შეუფერხებელი გამოცდილება` (seamless experience) → ✅ `მარტივი და სწრაფი პროცესი`
- ❌ `ხელოვნების დონეზე` (state-of-the-art) → ✅ `უახლესი ტექნოლოგია`, `მოწინავე სისტემა`
- ❌ `სუპერდამუხტვა` (supercharge) → ✅ `მნიშვნელოვნად დააჩქარე`, `გააძლიერე`

## Imperatives and address

Choose one address and apply it across the entire page, ad, or funnel:
1. **Direct informal (`შენ`):** Default for mobile apps, consumer SaaS, digital tools, and creator audiences.
   - Verbs: `დაიწყე`, `ნახე`, `შეარჩიე`, `დარეგისტრირდი`, `ჩამოტვირთე`.
2. **Polite formal (`თქვენ`):** For enterprise B2B, legal, medical, and banking solutions.
   - Verbs: `დაიწყეთ`, `ნახეთ`, `შეარჩიეთ`, `დაგვიკავშირდით`, `გაიარეთ კონსულტაცია`.

Never mix singular and plural imperatives in the same campaign or UI screen.

## Shorts and video hooks (no clickbait)

The first 2-3 seconds must engage without misleading the viewer:
- State a relatable friction point: `შენი საიტი მყიდველს ართულებს თუ ეხმარება?`
- Present a concrete metric: `როგორ დაზოგა ამ გუნდმა კვირაში 15 საათი?`
- Avoid deceptive hype words (`შოკი!`, `წარმოუდგენელი!`, `არ დაიჯერებთ!`).

## Copy inside a design (poster, card, ad)

A line on a graphic has no paragraph around it to rescue it, so one unclear phrase reads as a mistake. Run three
checks on the final strings before rendering:
1. **No literal English idioms.** `ბარათი თავს იხდის` (pays for itself) made Edo ask what it means. State the
   mechanism instead: `გვერდმა ხარჯი 2,8 თვეში დააბრუნა`. Test: if someone who has not seen the brief asks
   `რას ნიშნავს?`, it is a calque.
2. **A supporting line has a finite verb.** A headline may be a fragment; a bullet may not.
   ❌ `შაბლონი. ათეულობით ფაილი ტექსტამდე` ✅ `ტექსტამდე ათეულობით ფაილი იტვირთება`.
3. **The verb fits the noun.** ❌ `ხარისხს ზომით აჩვენებს` ✅ `ხარისხს ზომით იძლევა`. Read the noun and verb pair
   alone before trusting the sentence.

When a graphic is built from a copy table, fix the table, never the rendered output. Otherwise the fix covers
one card and the next build reverts it.

## Related skills

- Social posts and video cards: `kaeasy:georgian-social`
- Natural style and anti-calque: `kaeasy:georgian-natural-style`
- UI strings and buttons: `kaeasy:georgian-ui`

## References and examples

- `references/hype-calques.md`: complete dictionary of English buzzwords vs Georgian replacements.
- `references/cta-and-copy-rules.md`: CTAs, headline formulas, length limits, video hooks.
- `examples/marketing-fixes.md`: 50+ marketing copy fixes.

Run `ka_lint` with `mode: article` or `mode: social`.
