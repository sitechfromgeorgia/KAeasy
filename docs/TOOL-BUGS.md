# Tool Bugs and False-Positive Deficiencies

This document catalogs bugs and false positives discovered by the adversarial and speech fixture test suites (`tests/fixtures/adversarial/` and `tests/fixtures/speech_golden.jsonl`).

Per repository rules (`AGENTS.md` and project roadmap):
> **Hard rule: No false positives in STRICT.** A strict rule must never fire on correct Georgian.
> If a tool fails an adversarial or golden case, do **NOT** modify the tool in v0.2. Instead, list the failures here with `(input, expected, actual)` so that Claude can resolve them in the v0.3 release when implementing `ka_fix` and `ka_speech`.

---

## 1. Summary of Bug Categories

| Tool | Area | Trigger Pattern | Bug Severity | Root Cause |
|---|---|---|---|---|
| `ka_lint` | Markdown / Code Fences | ```` ```python ... "string" ... ``` ```` | High (False Positive) | `quotes` rule does not ignore code fences |
| `ka_lint` | JSON Payloads | ```` ```json {"key": "val"} ``` ```` | High (False Positive) | `quotes` rule flags valid JSON syntax |
| `ka_lint` | Quoted English Titles | `"The Wall Street Journal"` | Medium (False Positive) | `quotes` rule flags straight ASCII quotes around Latin titles |
| `ka_lint` | HTML Code Blocks | `<pre><code>{"key": "val"}</code></pre>` | High (False Positive) | `strip_html` removes tags but leaves code content exposed to `quotes` |
| `ka_lint` | Technical Metrics | `98.5%` in benchmark / ML report | Medium (False Positive) | `decimal` rule unconditionally flags dot before `%` in technical metrics |
| `ka_fix` | All | N/A (Tool not yet created) | Planned | Scheduled for v0.3 release |
| `ka_speech` | All | N/A (Tool not yet created) | Planned | Scheduled for v0.3 release |

---

## 2. Detailed Bug Reports (`ka_lint`)

### Bug 1: `quotes` rule flags double quotes inside Markdown code fences

- **Tool**: `ka_lint` (`mode="article"`, `strict=True`)
- **Fixture**: `tests/fixtures/adversarial/02_markdown_links_fences.txt`
- **Input**:
  ```markdown
  ```python
  def initialize_client(api_key: str) -> str:
      return "connected"
  ```
  ```
- **Expected**:
  `[]` (0 findings; code inside fences must be preserved verbatim)
- **Actual**:
  ```json
  [
    {
      "check": "quotes",
      "severity": "error",
      "message": "ინგლისური ბრჭყალები → „…“",
      "snippet": "…lize_client(api_key: str) -> str:\n    return \"connected\"\n```\nპარამეტრების გადაცემა ხდება უსაფრთხო დაშ…",
      "start": 200,
      "end": 211
    }
  ]
  ```
- **Remediation Recommendation for Claude (v0.3)**:
  Before applying regex checks in `lint.py:check_text`, mask out multiline code fences (```` ```...``` ````) and inline code spans (`` `...` ``) with whitespace or placeholder characters to preserve index alignment, similar to how `strip_html` blanks HTML tags.

---

### Bug 2: `quotes` rule flags quotes on JSON keys and string values

- **Tool**: `ka_lint` (`mode="article"`, `strict=True`)
- **Fixture**: `tests/fixtures/adversarial/04_json_payload.txt`
- **Input**:
  ```json
  ```json
  {
    "event": "payment_received",
    "status": "success",
    "amount": 1250,
    "currency": "GEL"
  }
  ```
  ```
- **Expected**:
  `[]` (0 findings; valid JSON structure must not be converted to Georgian curly quotes)
- **Actual**:
  7 findings of check `quotes`:
  ```json
  [
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"event\": \"payment_received\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"payment_received\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"status\": \"success\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"success\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"amount\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"currency\": \"GEL\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"GEL\"..."}
  ]
  ```
- **Remediation Recommendation for Claude (v0.3)**:
  Code blocks labeled with `json` or containing JSON structures must be excluded from quotation checks. In JSON, replacing ASCII `"` with Georgian `„…“` invalidates the document format.

---

### Bug 3: `quotes` rule flags ASCII quotes around purely English / Latin titles

- **Tool**: `ka_lint` (`mode="article"`, `strict=True`)
- **Fixture**: `tests/fixtures/adversarial/16_quoted_english_titles.txt`
- **Input**:
  ```text
  სტატია გამოქვეყნდა "The Wall Street Journal"-სა და "The New York Times"-ში.
  ავტორები ეყრდნობიან ჟურნალ "Nature"-ში დაბეჭდილ უახლეს კვლევას.
  მიმოხილვა ასევე ხელმისაწვდომია გამოცემა "Wired"-ის ვებგვერდზე.
  ```
- **Expected**:
  `[]` (0 findings in strict mode; foreign publications and proper titles quoted in Latin should not be flagged)
- **Actual**:
  4 findings of check `quotes`:
  ```json
  [
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "\"The Wall Street Journal\""},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "\"The New York Times\""},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "\"Nature\""},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "\"Wired\""}
  ]
  ```
- **Remediation Recommendation for Claude (v0.3)**:
  Refine the `quotes` regex in `lint.py` to only flag strings containing Georgian characters (e.g. `r'"([^"\n]*[ა-ჰ][^"\n]*)"'`), or allow pure ASCII/Latin quoted sequences when they represent foreign book/media titles followed by hyphenated Georgian case endings.

---

### Bug 4: `decimal` rule flags technical metrics and percentages with periods

- **Tool**: `ka_lint` (`mode="article"`, `strict=True`)
- **Fixture**: `tests/fixtures/adversarial/22_data_science_metrics.txt`
- **Input**:
  ```markdown
  მოდელის ტესტირების საბოლოო მეტრიკები:
  - სიზუსტე: 98.5%
  - F1-score: 0.94
  - საშუალო შეცდომა (RMSE): 0.12
  ```
- **Expected**:
  `[]` (0 findings in strict mode; technical metric listings with standard floating-point percentages must not be forced to comma decimals)
- **Actual**:
  ```json
  [
    {
      "check": "decimal",
      "severity": "error",
      "message": "ათწილადი მძიმით: „98.5%“",
      "snippet": "…ლის ტესტირების საბოლოო მეტრიკები:\n- სიზუსტე: 98.5%\n- F1-score: 0.94\n- საშუალო შეცდომა (RMSE): 0…",
      "start": 46,
      "end": 51
    }
  ]
  ```
- **Remediation Recommendation for Claude (v0.3)**:
  Restrict the `decimal` rule in strict mode to narrative prose (e.g., words like `მილიარდი`, `მილიონი`) or allow period-separated numbers in bullet lists, tables, and mathematical / code contexts.

---

### Bug 5: `quotes` rule flags English book title in quotes in developer newsletter

- **Tool**: `ka_lint` (`mode="article"`, `strict=True`)
- **Fixture**: `tests/fixtures/adversarial/24_developer_newsletter.txt`
- **Input**:
  ```markdown
  ყოველკვირეულ ბიულეტენში განვიხილავთ წიგნს "Designing Data-Intensive Applications".
  ```
- **Expected**:
  `[]` (0 findings; English title quoted in ASCII quotes)
- **Actual**:
  ```json
  [
    {
      "check": "quotes",
      "severity": "error",
      "message": "ინგლისური ბრჭყალები → „…“",
      "snippet": "ყოველკვირეულ ბიულეტენში განვიხილავთ წიგნს \"Designing Data-Intensive Applications\".\nმიმოხილვა მოამზადა @giorgi_k-მ.\nმასალები და…",
      "start": 43,
      "end": 83
    }
  ]
  ```
- **Remediation Recommendation for Claude (v0.3)**:
  Same as Bug 3: pure Latin titles enclosed in ASCII quotes should be exempted from the Georgian quotation marks requirement in strict mode.

---

### Bug 6: `quotes` rule flags code and JSON inside HTML `<pre><code>` tags

- **Tool**: `ka_lint` (`mode="article"`, `strict=True`)
- **Fixture**: `tests/fixtures/adversarial/25_full_composite_article.txt`
- **Input**:
  ```html
  <pre><code>{"api_version": "v3.8", "timeout": 30}</code></pre>
  ```
- **Expected**:
  `[]` (0 findings; code inside `<pre><code>` blocks must not have its syntax checked for Georgian quotes)
- **Actual**:
  3 findings of check `quotes`:
  ```json
  [
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"api_version\": \"v3.8\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"v3.8\"..."},
    {"check": "quotes", "message": "ინგლისური ბრჭყალები → „…“", "snippet": "...\"timeout\"..."}
  ]
  ```
- **Remediation Recommendation for Claude (v0.3)**:
  `strip_html` in `lint.py` currently strips `<[^>]+>`, which leaves the inner text of `<pre><code>` elements exposed. `strip_html` should blank the entire `<pre><code>...</code></pre>` or `<script>...</script>` block so code blocks in HTML do not trigger prose linter rules.

---

## 3. Tool Status for `ka_fix` and `ka_speech`

- **`ka_fix`**: Not yet implemented in v0.2. Tests in `tests/test_fixtures.py` are configured to skip when `ka_fix` is absent and immediately execute when the module becomes available in v0.3.
- **`ka_speech`**: Not yet implemented in v0.2. Tests in `tests/test_fixtures.py` are configured to skip when `ka_speech` is absent and immediately execute when the module becomes available in v0.3.
- **Golden Speech Dataset**: 393 verified lines are established in `tests/fixtures/speech_golden.jsonl`. All 393 spoken target outputs are verified clean with zero lint errors in `mode="speech"`.
