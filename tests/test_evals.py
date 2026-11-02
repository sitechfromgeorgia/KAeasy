import json
from pathlib import Path

import pytest
from kaeasy import lint

from evals import score

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"
TASKS_FILE = EVALS_DIR / "tasks.json"
README_FILE = EVALS_DIR / "README.md"


def test_evals_files_exist():
    assert EVALS_DIR.exists()
    assert TASKS_FILE.exists()
    assert README_FILE.exists()
    assert (EVALS_DIR / "score.py").exists()


def test_evals_task_count_and_distribution():
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    assert len(tasks) == 120

    categories = {}
    ids = set()
    for t in tasks:
        assert t["id"] not in ids, f"Duplicate task id: {t['id']}"
        ids.add(t["id"])

        cat = t["category"]
        categories[cat] = categories.get(cat, 0) + 1

        assert t["mode"] in lint.MODES
        assert len(t["prompt"].strip()) > 10
        assert isinstance(t["typical_mistakes"], list)
        assert len(t["typical_mistakes"]) >= 3
        assert len(t["reference"].strip()) > 5

    assert categories == {
        "news_rewrite": 30,
        "headline": 30,
        "shorts_hook": 30,
        "ui_error": 30
    }


def _eval_references():
    tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    out = []
    for t in tasks:
        out.append((t["id"], t["category"], t["mode"], t["reference"]))
    return out


@pytest.mark.parametrize("tid,category,mode,reference", _eval_references())
def test_every_reference_answer_lints_clean_in_strict_mode(tid, category, mode, reference):
    title = reference if category == "headline" else None
    findings = lint.check_text(reference, mode=mode, title=title, strict=True)
    assert findings == [], f"Task {tid} ({category}) reference failed lint in strict mode: {[f.as_dict() for f in findings]}"


def test_score_tool_roundtrip():
    tasks = score.load_tasks()
    assert len(tasks) == 120

    # Score reference answer for news_001
    task = tasks["news_001"]
    res = score.score_single(task, task["reference"], strict=True)
    assert res["clean"] is True
    assert res["findings_count"] == 0

    # Score broken candidate
    broken_res = score.score_single(task, "მაიკროსოფტმა გამოაცხადა.", strict=True)
    assert broken_res["clean"] is False
    assert broken_res["findings_count"] > 0
