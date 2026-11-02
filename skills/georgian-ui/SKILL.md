---
name: georgian-ui
description: Georgian (ka) UI strings - buttons, labels, status messages, errors, empty states, forms. Load when writing or reviewing interface text for any app or website.
---

# Georgian UI copy

| Element | Rule | ✅ | ❌ |
|---|---|---|---|
| Button | short verbal noun or verb | `შენახვა`, `გამოწერა`, `წაშლა`, `გაგზავნა` | `დააჭირეთ აქ შესანახად` |
| Status in progress | present-tense verb + `…` | `იტვირთება…`, `ინახება…`, `იგზავნება…` | `იტვირთვა…`, `შენახვა მიმდინარეობს` |
| Done status | short verb | `შენახულია`, `გაიგზავნა` | `წარმატებით განხორციელდა შენახვა` |
| Error | what happened + what to do | `სერვერს ვერ დავუკავშირდით. გადატვირთე გვერდი.` | `შეცდომა #500`, `წარუმატებელი ოპერაცია` |
| Empty state | explanation + action | `სიახლეები ჯერ არ არის. სცადე მოგვიანებით.` | `მონაცემები არ მოიძებნა` |
| Form label | noun | `ელფოსტა`, `პაროლი`, `სახელი` | `შეიყვანეთ თქვენი ელფოსტა აქ` |
| Placeholder | example, not instruction | `name@example.com` | `შეიყვანეთ ელფოსტა` (duplicate of label) |
| Confirmation | question with the real verb | `წავშალო პროექტი?` | `დარწმუნებული ხართ?` (alone) |

- Address: `თქვენ` (formal products) or `შენ` (young products), **one per product**. Verb forms follow:
  `შეიყვანეთ` / `შეიყვანე`.
- A status inside a drawn element (progress bar, toast) uses the verb, not the verbal noun: a verbal noun reads
  as a heading, not as state (Edo, 2026-11-02).
- No final period on buttons and labels; a period on full-sentence messages.
- Brands keep Latin with hyphenated endings: `Google-ით შესვლა`.
- Verify status words with a native speaker before a release.

`ka_lint` with `mode: ui`.
