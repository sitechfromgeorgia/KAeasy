import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _module():
    spec = importlib.util.spec_from_file_location("run_opencode", ROOT / "evals" / "run_opencode.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_prompt_and_report(tmp_path, monkeypatch):
    mod = _module()
    tasks = [t for t in mod.score.load_tasks().values() if t["id"] == "news_001"]
    assert "ka_lint" in mod.prompt(tasks[0], True) and "ka_lint" not in mod.prompt(tasks[0], False)
    monkeypatch.setattr(mod, "OUT", tmp_path)
    (tmp_path / "base.json").write_text(json.dumps({"news_001": "მაიკროსოფტმა გამოაცხადა"}), encoding="utf-8")
    (tmp_path / "kaeasy.json").write_text(json.dumps({"news_001": "Microsoft-მა გამოაცხადა."}), encoding="utf-8")
    md = mod.report(tasks, "m")
    assert "| news_rewrite | 0/1 | 1/1 |" in md


def test_respects_shorts_quota_circuit(tmp_path, monkeypatch):
    mod = _module()
    circuit = tmp_path / "c.json"
    circuit.write_text(json.dumps({"m": time.time() + 3600}))
    monkeypatch.setattr(mod, "CIRCUIT", str(circuit))
    try:
        mod.ask("m", "x", 1)
    except mod.QuotaUsedUp:
        return
    raise AssertionError("ran a model the circuit marks as used up")
