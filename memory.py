"""Shared mistakes memory: corrections that agents (or Edo) made, fed back to every writer.

A JSONL file, one correction per line. Agents add a line with ka_learn when a human or a review fixes their
Georgian; ka_mistakes returns the most frequent ones so a writer reads them before drafting.

Location: $KAEASY_DATA_DIR/mistakes.jsonl. Point every profile at the same directory to share learning across the
fleet (for example /root/.hermes/shared-knowledge/kaeasy). Without the variable it uses the fleet's shared
directory when the plugin is installed as <hermes>/shared-plugins/kaeasy and <hermes>/shared-knowledge/kaeasy
exists (the gateway does not pass a profile's .env to plugin code), then the Hermes per-plugin data dir, then
./data next to this file (tests, local use).
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import unicodedata
from pathlib import Path

CATEGORIES = ("case", "verb", "agreement", "postposition", "word_order", "calque", "lexical",
              "names", "numbers", "punctuation", "style", "speech", "other")

_lock = threading.Lock()
_SECRETISH = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d\s-]{8,}\d|(?:sk|gho|ghp|xox)[-_][A-Za-z0-9_-]{8,}")


def data_dir() -> Path:
    env = os.environ.get("KAEASY_DATA_DIR")
    if env:
        return Path(env)
    here = Path(__file__).resolve().parent  # symlinks resolved: <hermes>/shared-plugins/kaeasy
    shared = here.parent.parent / "shared-knowledge" / "kaeasy"
    if here.parent.name == "shared-plugins" and shared.is_dir():
        return shared
    try:
        from plugins.plugin_storage import plugin_data_dir  # Hermes host API

        return Path(plugin_data_dir("kaeasy"))
    except Exception:
        return Path(__file__).resolve().parent / "data"


def _path() -> Path:
    d = data_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d / "mistakes.jsonl"


def _clean(s: str, limit: int) -> str:
    s = unicodedata.normalize("NFC", (s or "").strip())
    s = _SECRETISH.sub("[masked]", s)
    return s[:limit]


def learn(wrong: str, right: str, reason: str = "", category: str = "other", agent: str = "") -> dict:
    wrong, right = _clean(wrong, 300), _clean(right, 300)
    if not wrong or not right or wrong == right:
        raise ValueError("wrong and right must be non-empty and different")
    if category not in CATEGORIES:
        category = "other"
    row = {"ts": int(time.time()), "wrong": wrong, "right": right, "reason": _clean(reason, 200),
           "category": category, "agent": _clean(agent, 40)}
    with _lock, _path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _rows() -> list[dict]:
    p = _path()
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def top(limit: int = 20, category: str | None = None) -> list[dict]:
    """Most frequent (wrong → right) pairs, newest first among equals."""
    groups: dict[tuple[str, str], dict] = {}
    for r in _rows():
        if category and r.get("category") != category:
            continue
        key = (r["wrong"].casefold(), r["right"].casefold())
        g = groups.setdefault(key, {**r, "count": 0})
        g["count"] += 1
        if r["ts"] >= g["ts"]:
            g.update({k: r[k] for k in ("ts", "reason", "category") if k in r})
    ranked = sorted(groups.values(), key=lambda g: (-g["count"], -g["ts"]))
    return ranked[: max(1, min(limit, 100))]


def as_markdown(rows: list[dict]) -> str:
    if not rows:
        return "ჯერ შეცდომები არ დაგროვილა."
    lines = []
    for r in rows:
        why = f": {r['reason']}" if r.get("reason") else ""
        lines.append(f"- ❌ {r['wrong']} → ✅ {r['right']} ({r['category']}, ×{r['count']}){why}")
    return "\n".join(lines)
