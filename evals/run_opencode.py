"""Before/after eval: does Kaeasy make a free model write better Georgian? ($0, opencode free models.)

Runs N tasks from tasks.json twice through `opencode run`: once with only the task, once with the
kaeasy:georgian-writing SKILL and the task's sibling SKILL in front of it. Scores both with score.py (ka_lint
strict + the task's mistake checklist for a human) and writes evals/RESULTS.md.

The free opencode quota is shared with SiTech Shorts production. This script stops at the first "Free usage limit
reached" and refuses to start while Shorts' quota circuit (/tmp/sitech-shorts-circuit.json) marks the model as used
up. Requests = 2 x N; tell Louie the number before a run.

    python3 evals/run_opencode.py --n 5            # 5 per category = 20 tasks = 40 requests
    python3 evals/run_opencode.py --n 5 --score-only
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))
import score

OUT = ROOT / "evals" / "runs"
CIRCUIT = os.environ.get("SHORTS_CIRCUIT", os.path.join(tempfile.gettempdir(), "sitech-shorts-circuit.json"))
QUOTA_TEXT = ("Free usage limit reached", "QUOTA:")
SIBLING = {"news_rewrite": "georgian-news", "headline": "georgian-news", "shorts_hook": "georgian-social",
           "ui_error": "georgian-ui"}
ONLY = "Answer with the Georgian text only: no explanations, no quotes around it, no English."


class QuotaUsedUp(RuntimeError):
    pass


def skill(name: str) -> str:
    text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    return text.split("---", 2)[2].strip() if text.startswith("---") else text


def prompt(task: dict, with_kaeasy: bool) -> str:
    body = f"{task['prompt']}\n\n{ONLY}"
    if not with_kaeasy:
        return body
    return (f"Follow these Georgian writing rules.\n\n{skill('georgian-writing')}\n\n{skill(SIBLING[task['category']])}"
            f"\n\n---\n\nTask:\n{body}")


def ask(model: str, text: str, timeout: int) -> str:
    try:
        until = json.loads(Path(CIRCUIT).read_text()).get(model, 0)
    except (OSError, ValueError):
        until = 0
    if until > time.time():
        raise QuotaUsedUp(f"{model}: Shorts circuit says quota used up until {time.ctime(until)}")
    with tempfile.TemporaryDirectory() as tmp:  # opencode is an agent: give it an empty folder
        r = subprocess.run([os.environ.get("OPENCODE_BIN", "opencode"), "run", "-m", model, text], cwd=tmp,
                           capture_output=True, text=True, timeout=timeout, check=False)
    if any(t in r.stderr + r.stdout for t in QUOTA_TEXT):
        raise QuotaUsedUp(f"{model}: free usage limit reached")
    lines = [ln for ln in r.stdout.splitlines() if ln.strip() and not ln.lstrip().startswith(">")]
    return "\n".join(lines).replace("\x1b[0m", "").strip()


def run(tasks: list[dict], model: str, timeout: int) -> None:
    OUT.mkdir(exist_ok=True)
    for label, with_kaeasy in (("base", False), ("kaeasy", True)):
        path = OUT / f"{label}.json"
        done = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        for t in tasks:
            if t["id"] in done:
                continue
            print(f"{label} {t['id']} ...", file=sys.stderr, flush=True)
            done[t["id"]] = ask(model, prompt(t, with_kaeasy), timeout)
            path.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")  # resumable


def report(tasks: list[dict], model: str) -> str:
    index = {t["id"]: t for t in tasks}
    res = {}
    for label in ("base", "kaeasy"):
        preds = json.loads((OUT / f"{label}.json").read_text(encoding="utf-8"))
        res[label] = score.score_batch({k: v for k, v in preds.items() if k in index and v}, index)
    lines = [f"# Kaeasy eval: {model}", "", f"{time.strftime('%Y-%m-%d')} · {len(tasks)} tasks · ka_lint strict",
             "", "| category | base clean | kaeasy clean |", "|---|---|---|"]
    empty = {"clean": 0, "total": 0}
    for c in sorted({t["category"] for t in tasks}):
        b, k = (res[x]["by_category"].get(c, empty) for x in ("base", "kaeasy"))
        lines.append(f"| {c} | {b['clean']}/{b['total']} | {k['clean']}/{k['total']} |")
    b, k = res["base"], res["kaeasy"]
    lines += [f"| **all** | **{b['clean']}/{b['total']}** | **{k['clean']}/{k['total']}** |", "",
              "Lint finds mechanical errors only. Grammar (case, verb, calques) needs a human pass over",
              "`evals/runs/*.json` against each task's `typical_mistakes`."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kaeasy before/after eval on a free opencode model")
    ap.add_argument("--n", type=int, default=5, help="tasks per category")
    ap.add_argument("--model", default="opencode/deepseek-v4.1-flash-free")
    ap.add_argument("--timeout", type=int, default=420)
    ap.add_argument("--score-only", action="store_true")
    a = ap.parse_args(argv)
    tasks, seen = [], {}
    for t in score.load_tasks().values():
        if seen.get(t["category"], 0) < a.n:
            tasks.append(t)
            seen[t["category"]] = seen.get(t["category"], 0) + 1
    if not a.score_only:
        print(f"{len(tasks)} tasks, {2 * len(tasks)} requests to {a.model} ($0)", file=sys.stderr)
        try:
            run(tasks, a.model, a.timeout)
        except QuotaUsedUp as e:
            print(f"stopped: {e} (finished answers are saved, rerun later to resume)", file=sys.stderr)
            return 2
    md = report(tasks, a.model)
    (ROOT / "evals" / "RESULTS.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
