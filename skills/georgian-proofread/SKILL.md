---
name: georgian-proofread
description: Self-edit or review Georgian (ka) text before it is published - fact freeze, natural rewrite, adversarial copy desk, ka_lint gate, and recording corrections with ka_learn. Load after drafting, or when asked to check or fix someone's Georgian.
---

# Georgian proofreading protocol

Every model's text is a draft, including a fluent one. Smaller models need this more, not less. The same model
does the editing (no extra service, no extra cost): run three separate passes, never one combined prompt.

## Pass 1: fact freeze

List everything that may not change: names, numbers, dates, quotes, attributions, links, qualifiers
(`შესაძლოა`, `ვარაუდობს`, `-მდე`). Keep the list.

## Pass 2: natural Georgian rewrite

Rewrite for meaning, not word order, using `kaeasy:georgian-grammar` and `kaeasy:georgian-natural-style`.
Check each sentence:

1. Verb series → subject case (`-მა` in aorist transitive, dative with feeling verbs).
2. Object case (nominative in aorist).
3. Numeral → singular noun and verb.
4. Adjective forms, postposition cases.
5. Brands Latin + hyphen; countries Georgian; terms Georgian.
6. Calques, filler, passive, noun chains removed.
7. Sentence length 8-20 words (6-14 for narration).

For a fallback-model draft, end the editing prompt with this line verbatim:

```text
ჯერ ჩუმად შეადარე ტექსტი ფაქტების სიას. შემდეგ გადაწერე ბუნებრივი ქართული წინადადებებით, არა
ინგლისური წყობის კალკით. არ დაამატო არც ფაქტი, არც მიზეზშედეგობრივი კავშირი. ბრენდები დატოვე
Latin script-ით, ქართული ბრუნვის ნიშანი მიაბი დეფისით. პასუხში დააბრუნე მხოლოდ საბოლოო ტექსტი.
```

## Pass 3: adversarial copy desk

- Compare the rewrite with the fact freeze. Reject if a fact moved, a qualifier disappeared or a causal link
  was invented.
- Read every sentence as a Georgian reader: if it needs two readings, rewrite it.
- `ka_lint` (right `mode`, `strict: true`, headline in `title`). Fix and re-run until clean. A clean lint does
  not prove good Georgian; it proves the mechanical rules hold.

## Reviewing someone else's text

Report each problem with the rule name and the fix: `ergative: „კომპანია გამოაცხადა“ → „კომპანიამ
გამოაცხადა“`. Do not rewrite quoted sources or a source outlet's headline.

## Learning

When Edo, an editor or a review corrects Georgian you wrote, call `ka_learn` once per correction:
`wrong` and `right` as the shortest phrase that shows the mistake, `category`, a one-line `reason` in
Georgian. Do not store whole articles, names of private people or anything secret. Before writing, `ka_mistakes`
shows what the fleet learned.
