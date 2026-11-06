# Georgian Agent Writing Evals (`evals/`)

This directory contains **121 short Georgian writing tasks** reflecting the exact tasks Hermes agents execute daily.
Each task includes the prompt, the linter evaluation mode, a checklist of mistakes weak models typically make on it, and a verified gold-standard reference answer.

> [!IMPORTANT]
> **No API calls in this repo.** This benchmark runs entirely offline and deterministically. Evaluation uses our zero-cost deterministic linter (`ka_lint` / `lint.py`), the curated mistake checklists, and the offline scoring utility (`evals/score.py`).

---

## Benchmark Composition

The 121 tasks are divided across 4 core production categories:

| Category | Task IDs | Linter Mode | Description | Key Focus |
|---|---|---|---|---|
| **News Rewrite** | `news_001` – `news_031` | `article` | Short English news paragraphs (tech, science, finance, local events) to rewrite into natural Georgian | Ergative case (`-მა`), numbers + singular, hyphenated Latin brands, no calques, no AI filler, negation concord |
| **Headline** | `headline_001` – `headline_030` | `article` | Event and product summaries to condense into punchy Georgian news headlines | **No trailing period**, active voice, actor in ergative, no vague clickbait |
| **Shorts Hook** | `shorts_001` – `shorts_030` | `social` | 3-second opening video hooks (6–14 words) for vertical shorts/reels | Consistent `შენ` register, no formulaic YouTube openers, active finite verbs |
| **UI Error** | `ui_001` – `ui_030` | `ui` | System errors, form validations, empty states, and dialog prompts | "What happened + what to do" (მიზეზი + გამოსავალი), helpful tone, period at end |

All tasks are stored in [`evals/tasks.json`](file:///d:/MyStaff/Kaeasy/evals/tasks.json).

---

## Task Schema

Each entry in `evals/tasks.json` has the following structure:

```json
{
  "id": "news_001",
  "category": "news_rewrite",
  "mode": "article",
  "prompt": "Rewrite this news paragraph into Georgian: Microsoft has announced Copilot Pro for enterprise customers in Germany and France. The company stated that the service costs $30 per user per month and includes access to the latest OpenAI models.",
  "typical_mistakes": [
    "Transliterating brands into Georgian letters (მაიკროსოფტმა, ოპენაის) instead of keeping Latin (Microsoft-მა, OpenAI-ს).",
    "Leaving European country names in English (Germany-ში, France-ში) instead of translating (გერმანიასა და საფრანგეთში).",
    "Dropping the ergative suffix -მა on the subject with an aorist verb (Microsoft გამოაცხადა instead of Microsoft-მა გამოაცხადა).",
    "Using dative for the direct object in aorist (Copilot Pro-ს გამოაცხადა instead of Copilot Pro გამოაცხადა)."
  ],
  "reference": "Microsoft-მა გერმანიასა და საფრანგეთში კორპორაციული მომხმარებლებისთვის Copilot Pro გამოაცხადა. კომპანიის განცხადებით, სერვისი თითოეულ მომხმარებელზე თვეში 30 დოლარი ღირს და OpenAI-ს უახლეს მოდელებზე წვდომას მოიცავს."
}
```

---

## How to Run a Model Manually

You can benchmark any model (e.g. Claude 3.5 Sonnet, Claude 3.5 Haiku, GPT-4o, GPT-4o-mini, Gemini 1.5 Pro/Flash, Llama 3) manually or via your own external test harness.

### Step 1: Inspect the Task Prompt

View the prompt, reference answer, and mistake checklist using the offline CLI:

```bash
uv run python evals/score.py --inspect news_001
```

Or read `evals/tasks.json` directly.

### Step 2: Test Baseline vs Kaeasy Skill

To measure the improvement provided by Kaeasy:

1. **Baseline run (No skill):**
   Provide only the `prompt` to the model with standard instructions:
   > "You are an assistant. Answer the user prompt directly in high-quality Georgian."

2. **Kaeasy-assisted run (With skill):**
   Include the relevant skill instructions from `skills/` (e.g. `skills/georgian-writing/SKILL.md` and the sibling skill `georgian-news`, `georgian-social`, or `georgian-ui`) in the model's system prompt or context.

### Step 3: Collect Output

Save the model's Georgian response. For batch evaluations, save responses to a JSON file (see [Batch Scoring](#batch-scoring)).

---

## How to Score Model Outputs

Evaluation consists of two complementary layers:
1. **Automated Linter Gate (`ka_lint`)**: Zero false-positive mechanical error detection.
2. **Task Mistake Checklist**: Semantic, grammatical, and stylistic rubric review.

### 1. Automated Linter Gate (`ka_lint`)

Run `lint.py` directly on the model's Georgian text:

```bash
# Article mode (news paragraphs & headlines)
uv run python lint.py --text "<MODEL_OUTPUT>" --mode article --strict

# Social mode (Shorts hooks)
uv run python lint.py --text "<MODEL_OUTPUT>" --mode social --strict

# UI mode (UI errors & strings)
uv run python lint.py --text "<MODEL_OUTPUT>" --mode ui --strict
```

#### Gate Criteria:
- **Strict Mode Pass (`clean: true`)**: The text must trigger **0 findings** in strict mode. Strict mode checks:
  - `translit`: Foreign brands must be kept in Latin (`Microsoft`, `Apple`, `Google`), never transliterated into Georgian letters (`მაიკროსოფტმა` ❌).
  - `ending_hyphen`: Georgian case endings on Latin brands require a hyphen without spaces (`Google-მა` ✅, `Googleმა` ❌, `Google -მა` ❌).
  - `quotes`: Must use Georgian quotes `„…“` instead of straight English quotes `"..."`.
  - `title_period`: Headlines must not end with a period (`.`).
  - `number_plural`: After a numeral or quantity word, the noun must be singular (`5 კომპანია` ✅, `5 კომპანიები` ❌).
  - `percent` & `decimal`: No space before percent (`20%` ✅, `20 %` ❌); Georgian uses decimal comma (`2,5` ✅, `2.5` ❌).
  - `dash`: Em-dash `—` and en-dash `–` are forbidden in fleet style (use comma, colon, or hyphen).
  - `cyrillic`: No accidental Cyrillic letters.

### 2. Task Mistake Checklist Review

Weak models frequently pass shallow regexes but fail on Georgian morphosyntax. Check the model output against the `typical_mistakes` listed in the task:

1. **Ergative Case Alignment:**
   - Did the model drop `-მა / -მ` on the subject of a past transitive verb? (e.g. `კომპანია გამოაცხადა` ❌ vs `კომპანიამ გამოაცხადა` ✅)
   - Is the direct object in the nominative rather than dative? (e.g. `ახალ მოდელს წარადგინა` ❌ vs `ახალი მოდელი წარადგინა` ✅)
2. **Subject-Verb Number Agreement:**
   - Plural nouns after numerals must take a singular verb (e.g. `სამმა კომპანიამ განაცხადა` ✅ vs `სამმა კომპანიებმა განაცხადეს` ❌).
   - Plural human agents take plural verbs (e.g. `მკვლევრებმა აღმოაჩინეს` ✅).
3. **Calques & AI Filler:**
   - Did it translate English idioms literally? (e.g. `ადგილი მიიღო` ❌ vs `გაიმართა` ✅; `გააკეთა გადაწყვეტილება` ❌ vs `გადაწყვიტა` ✅).
   - Did it add empty AI filler? (e.g. `მნიშვნელოვანია აღინიშნოს, რომ` ❌, `თანამედროვე სამყაროში` ❌).
4. **Tone & Register:**
   - In Shorts hooks: Is the viewer addressed consistently as `შენ`? Did it avoid formulaic greetings (`გამარჯობათ მეგობრებო`)?
   - In UI errors: Does it follow "what happened + what to do" (მიზეზი + გამოსავალი)? Is it actionable rather than cryptic?

---

## Using `evals/score.py`

Kaeasy includes a dedicated offline scoring script [`evals/score.py`](file:///d:/MyStaff/Kaeasy/evals/score.py).

### Scoring a Single Output Interactively

```bash
uv run python evals/score.py --task news_001 --text "Microsoft-მა გერმანიასა და საფრანგეთში კორპორაციული მომხმარებლებისთვის Copilot Pro გამოაცხადა."
```

Output:
```text
Task: news_001 (news_rewrite)
Candidate: Microsoft-მა გერმანიასა და საფრანგეთში კორპორაციული მომხმარებლებისთვის Copilot Pro გამოაცხადა.
Status: PASS (0 linter errors)

Review against checklist:
  [ ] Transliterating brands into Georgian letters (მაიკროსოფტმა, ოპენაის) instead of keeping Latin (Microsoft-მა, OpenAI-ს).
  [ ] Leaving European country names in English (Germany-ში, France-ში) instead of translating (გერმანიასა და საფრანგეთში).
  [ ] Dropping the ergative suffix -მა on the subject with an aorist verb (Microsoft გამოაცხადა instead of Microsoft-მა გამოაცხადა).
  [ ] Using dative for the direct object in aorist (Copilot Pro-ს გამოაცხადა instead of Copilot Pro გამოაცხადა).
```

### Batch Scoring

Create a JSON file with model outputs, either as an object mapping task IDs to text:
```json
{
  "news_001": "Microsoft-მა გერმანიაში ახალი Copilot Pro გამოაცხადა.",
  "headline_001": "Apple-მა iPhone 16 Pro-ს ფასი 100 დოლარით გაზარდა"
}
```
Or as an array of objects:
```json
[
  {"id": "news_001", "output": "Microsoft-მა გერმანიაში ახალი Copilot Pro გამოაცხადა."},
  {"id": "headline_001", "output": "Apple-მა iPhone 16 Pro-ს ფასი 100 დოლარით გაზარდა"}
]
```

Run batch evaluation:
```bash
uv run python evals/score.py --file predictions.json
```

Output summary:
```text
Evaluated 120 tasks (Strict mode: True)
Clean (0 errors): 112 / 120 (93.3% pass rate)

Breakdown by category:
  - news_rewrite   : 28/30 clean (93.3%)
  - headline       : 30/30 clean (100.0%)
  - shorts_hook    : 27/30 clean (90.0%)
  - ui_error       : 27/30 clean (90.0%)
```

Add `--json` for machine-readable output:
```bash
uv run python evals/score.py --file predictions.json --json
```

---

## Verifying Reference Answers

All 120 reference answers in `evals/tasks.json` are verified against `ka_lint` in strict and standard mode.
You can run automated verification anytime with pytest:

```bash
uv run --with pytest --with pyyaml python -m pytest tests/test_evals.py -q
```
