---
name: georgian-news
description: Writing and editing Georgian (ka) news articles and headlines for tbilisi.today and the sitech.ge blog - structure, attribution, headlines, quotes, neutral tone. Load before drafting or editing a news piece.
---

# Georgian news copy

Load `kaeasy:georgian-grammar` and `kaeasy:georgian-names-numbers` too; this skill adds the news layer.

## Structure

1. **First sentence = the news**: who did what, where, when. `Microsoft-მა ორშაბათს ახალი AI მოდელი წარადგინა.`
2. Second paragraph: the most important detail or number.
3. Then context, reaction, what happens next.
4. Attribution for every claim that is not a plain fact: `კომპანიის განცხადებით`, `მკვლევრების თქმით`,
   `ანგარიშის მიხედვით`. Name the source once; following sentences from the same source need no repeat.
5. Sentences 8-20 words, past tense for events (`განაცხადა`, `გამოუშვა`), present for ongoing facts.

## Headlines

- The strongest verified fact, in natural Georgian, actor + verb: `Apple-მა iPhone-ის ფასი გაზარდა`.
- No final period, no clickbait question, no unsupported superlative, no vague `ეს` / `ის`.
- A colon only before a quote: `სტუდია: „ჩვენ ვჩერდებით“`.
- A headline inherited from a source outlet is a quote: do not rewrite it silently.

## Quotes

- Copy the quote's meaning faithfully in `„…“`; never turn a paraphrase into a quote or a quote into a new claim.
- Do not "fix" grammar inside a quoted Georgian source.

## Tone

Neutral and direct. Not promotional, not bureaucratic, not conversational. No hype (`რევოლუციური`,
`შოკისმომგვრელი`) unless a number proves it. Prefer numbers to adjectives: ❌ `ბევრი მომხმარებელი` →
✅ `12 მილიონი მომხმარებელი`.

## Gate

`ka_lint` with `mode: article`, `strict: true`, and the headline in `title`. The tbilisi.today publisher
(`publish_piece.py`) has its own fail-closed gate; a blocked piece must be rewritten, never bypassed.

## Examples

`examples/headlines.md` (20 headline fixes), `examples/article-before-after.md` (one full article edited).
