# Kaeasy

Georgian (ქართული) writing skills for AI agents. A [Hermes Agent](https://hermes-agent.nousresearch.com/docs)
plugin that helps cheap models (DeepSeek, GLM, gemma) write Georgian that a native editor would publish.

**Zero runtime cost.** No LLM calls, no API keys, no network. Knowledge lives in skills (rules +
`references/` + many wrong → right `examples/`); a deterministic linter checks the mechanical rules; a shared
mistakes memory feeds every correction back to all agents.

## What is inside

| Part | What it does |
|---|---|
| `skills/georgian-writing` | Entry point: workflow, the ten most-broken rules, which sibling to load |
| `skills/georgian-grammar` | Cases by verb series, numerals, adjectives, postpositions, verbs, agreement |
| `skills/georgian-natural-style` | Calques (EN/RU), AI filler, passive, rewrites |
| `skills/georgian-names-numbers` | Brands in Latin + hyphenated endings, countries, terms, numbers, dates, punctuation |
| `skills/georgian-news` | Articles and headlines (tbilisi.today, sitech.ge blog) |
| `skills/georgian-social` | Posts, ads, cards, on-screen video text |
| `skills/georgian-ui` | Buttons, statuses, errors, forms |
| `skills/georgian-speech` | `speech_text` for TTS: numbers in words, brands in Georgian letters |
| `skills/georgian-proofread` | Three-pass self-edit, review format, learning loop |
| `ka_lint` tool | Mechanical checks, modes `article / social / ui / speech`, `strict` for publish gates |
| `ka_learn` / `ka_mistakes` tools | Shared memory of corrections (JSONL), most frequent first |
| `pre_llm_call` hook | One short hint per session so agents know the skills exist |

Skills are registered as `kaeasy:<name>` (`skill_view("kaeasy:georgian-writing")`). Plugin skills are read-only
and are not listed in `<available_skills>`, which is why the hook exists. Disable the hint with `KAEASY_HINT=0`.

## Install on a Hermes host

```bash
git clone https://github.com/sitechfromgeorgia/kaeasy /root/.hermes/shared-plugins/kaeasy
ln -s /root/.hermes/shared-plugins/kaeasy /root/.hermes/profiles/<profile>/plugins/kaeasy
# enable it for the profile (hermes plugins enable kaeasy, or plugins.enabled in config.yaml), then restart
# the gateway and check:  hermes plugins list
```

Shared learning across the fleet: set `KAEASY_DATA_DIR` to one directory for every profile (for example
`/root/.hermes/shared-knowledge/kaeasy`). Without it, each profile keeps its own memory in Hermes' plugin data dir.

## Linter outside Hermes

```bash
python lint.py --text "Microsoftმა 5 სტატიები გამოაქვეყნა" --strict
python lint.py --file draft.md --mode social --summary
```

## Develop

```bash
uv run --with pytest --with pyyaml python -m pytest -q
uv run --with ruff ruff check .
```

See `AGENTS.md` for the rules of the repo (how to add a rule or an example without breaking anything).

## Credits

The linter and the first rules come from the SiTech fleet's `ge_ka_lint.py`, `GEORGIAN-STYLE.md` and the
`georgian-copy-quality` skill, plus the SiTech Shorts rulebook (K1-K22).
