"""Offline scoring tool for Georgian evals.

Zero API calls, zero network, zero LLM calls.
Evaluates model outputs against Kaeasy's deterministic linter (ka_lint) and task-specific mistake checklists.

Usage:
  # Score a single output manually:
  uv run python evals/score.py --task news_001 --text "ტექსტი..."

  # Score a batch of model predictions from a JSON file:
  uv run python evals/score.py --file predictions.json

  # Inspect a task prompt, reference answer, and mistake checklist:
  uv run python evals/score.py --inspect news_001

  # Output machine-readable JSON:
  uv run python evals/score.py --file predictions.json --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Resolve repo root and import lint
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import lint

TASKS_FILE = REPO_ROOT / "evals" / "tasks.json"


def load_tasks() -> dict[str, dict]:
    if not TASKS_FILE.exists():
        raise FileNotFoundError(f"Tasks file not found: {TASKS_FILE}")
    with open(TASKS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return {task["id"]: task for task in data}


def score_single(task: dict, candidate_text: str, strict: bool = True) -> dict:
    mode = task.get("mode", "article")
    is_headline = task.get("category") == "headline"
    title = candidate_text if is_headline else None

    findings = lint.check_text(candidate_text, mode=mode, title=title, strict=strict)
    findings_dicts = [f.as_dict() for f in findings]

    return {
        "id": task["id"],
        "category": task["category"],
        "mode": mode,
        "clean": len(findings) == 0,
        "findings_count": len(findings),
        "findings": findings_dicts,
        "typical_mistakes": task["typical_mistakes"],
        "reference": task["reference"],
    }


def score_batch(predictions: dict[str, str], tasks: dict[str, dict], strict: bool = True) -> dict:
    results = {}
    categories = {}
    total = 0
    clean_count = 0

    for task_id, text in predictions.items():
        if task_id not in tasks:
            continue
        task = tasks[task_id]
        res = score_single(task, text, strict=strict)
        results[task_id] = res

        cat = task["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "clean": 0}
        categories[cat]["total"] += 1
        total += 1

        if res["clean"]:
            clean_count += 1
            categories[cat]["clean"] += 1

    return {
        "total": total,
        "clean": clean_count,
        "pass_rate": (clean_count / total * 100.0) if total else 0.0,
        "strict": strict,
        "by_category": categories,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic offline evaluator for Kaeasy Georgian evals.")
    parser.add_argument("--task", help="Task ID to evaluate (e.g. news_001, headline_005).")
    parser.add_argument("--text", help="Model candidate text to score.")
    parser.add_argument("--file", help="Path to JSON file containing predictions: {\"task_id\": \"output\", ...}.")
    parser.add_argument("--inspect", help="Display prompt, reference, and checklist for a task ID.")
    parser.add_argument("--strict", action="store_true", default=True, help="Use strict linter mode (default: True).")
    parser.add_argument("--all-rules", dest="strict", action="store_false", help="Run non-strict linter rules too.")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Output raw JSON.")

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    args = parser.parse_args(argv)
    tasks = load_tasks()

    if args.inspect:
        tid = args.inspect
        if tid not in tasks:
            print(f"Unknown task ID: {tid}", file=sys.stderr)
            return 1
        t = tasks[tid]
        print(f"=== Task: {t['id']} [{t['category']} / mode: {t['mode']}] ===")
        print(f"\n[PROMPT / BRIEF]:\n{t['prompt']}")
        print(f"\n[REFERENCE ANSWER]:\n{t['reference']}")
        print("\n[TYPICAL WEAK-MODEL MISTAKES CHECKLIST]:")
        for i, m in enumerate(t["typical_mistakes"], 1):
            print(f"  {i}. {m}")
        return 0

    if args.task and args.text:
        tid = args.task
        if tid not in tasks:
            print(f"Unknown task ID: {tid}", file=sys.stderr)
            return 1
        task = tasks[tid]
        res = score_single(task, args.text, strict=args.strict)

        if args.as_json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
            return 0 if res["clean"] else 1

        print(f"Task: {tid} ({task['category']})")
        print(f"Candidate: {args.text}")
        if res["clean"]:
            print("Status: \033[92mPASS (0 linter errors)\033[0m")
        else:
            print(f"Status: \033[91mFAIL ({res['findings_count']} findings)\033[0m")
            for f in res["findings"]:
                print(f"  - [{f['check']}] {f['message']}")

        print("\nReview against checklist:")
        for m in task["typical_mistakes"]:
            print(f"  [ ] {m}")
        return 0 if res["clean"] else 1

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Predictions file not found: {path}", file=sys.stderr)
            return 1
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        # Normalize format: either {"id": "text"} or [{"id": "...", "output": "..."}]
        if isinstance(raw, list):
            predictions = {item["id"]: item.get("output", item.get("text", "")) for item in raw}
        elif isinstance(raw, dict):
            predictions = raw
        else:
            print("Invalid JSON structure. Expected dict or list of objects.", file=sys.stderr)
            return 1

        report = score_batch(predictions, tasks, strict=args.strict)

        if args.as_json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0

        print(f"Evaluated {report['total']} tasks (Strict mode: {report['strict']})")
        print(f"Clean (0 errors): {report['clean']} / {report['total']} ({report['pass_rate']:.1f}% pass rate)\n")
        print("Breakdown by category:")
        for cat, data in report["by_category"].items():
            rate = (data["clean"] / data["total"] * 100.0) if data["total"] else 0.0
            print(f"  - {cat:15}: {data['clean']:2d}/{data['total']:2d} clean ({rate:.1f}%)")

        failed_tasks = [tid for tid, r in report["results"].items() if not r["clean"]]
        if failed_tasks:
            print(f"\nFailed tasks ({len(failed_tasks)}): {', '.join(failed_tasks[:20])}" + ("..." if len(failed_tasks) > 20 else ""))

        return 0 if report["clean"] == report["total"] else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
