"""Seed the Kaeasy mistakes memory from SiTech Shorts review edits (data/edits.jsonl on the hub).

Each Shorts edit line looks like "wrong → right (K5, K9)", where K-codes are rules from the Shorts ka_style.md.
Only language rules are imported. Factual ones (K10 qualifiers, K14 quotes, K15 numbers, K20 say-map) are about
the article, not about Georgian, so they are skipped, and so are deletions and long rewrites.

    KAEASY_DATA_DIR=/root/kaeasy-lab/data python3 -m kaeasy.scripts.import_edits /root/sitech-shorts-lab/data/edits.jsonl
    python3 scripts/import_edits.py edits.jsonl --dry-run      # print what would be imported

Writes through memory.learn(), so the same masking and limits apply. Run it once per edits file: it does not
deduplicate against rows that are already in the memory.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Shorts ka_style.md rule → Kaeasy memory category. Missing codes are skipped: facts (K10, K14, K15), the say map
# (K20) and layout or sentence length (K8, K9, K13), which say nothing about Georgian itself.
K_CATEGORY = {
    "K1": "style", "K2": "style", "K3": "calque", "K4": "verb", "K5": "case", "K6": "agreement",
    "K7": "postposition", "K11": "punctuation", "K12": "punctuation", "K16": "names", "K17": "names",
    "K18": "lexical", "K19": "lexical", "K21": "numbers", "K22": "numbers",
}
# The most specific category wins when an edit names several rules.
PRIORITY = ["case", "agreement", "postposition", "verb", "calque", "names", "numbers", "lexical", "punctuation",
            "style"]
EDIT = re.compile(r"^(?P<wrong>.+?)\s+→\s+(?P<right>.+?)\s*\((?P<codes>K\d+[^)]*)\)\s*$")
GEORGIAN = re.compile(r"[ა-ჰ]")
MAX_LEN = 120
# Edits of scene parts ("take lines: ...", "headline: ...", "[...]") or deletions ("(removed)"), not of a phrase.
NOT_A_PHRASE = re.compile(r"^(?:\(|\[|[A-Za-z][A-Za-z ]{1,20}:)")


def parse(change: str) -> dict | None:
    m = EDIT.match(change.strip())
    if not m:
        return None
    wrong, right = m["wrong"].strip(" „“\""), m["right"].strip(" „“\"")
    cats = {K_CATEGORY[c] for c in re.findall(r"K\d+", m["codes"]) if c in K_CATEGORY}
    if not cats or not GEORGIAN.search(wrong) or not GEORGIAN.search(right) or wrong == right:
        return None
    if NOT_A_PHRASE.match(wrong) or NOT_A_PHRASE.match(right) or " / " in wrong \
            or max(len(wrong), len(right)) > MAX_LEN:
        return None  # scene notes, deletions and long rewrites teach nothing reusable
    category = next(c for c in PRIORITY if c in cats)
    return {"wrong": wrong, "right": right, "category": category, "reason": m["codes"].strip()}


def load(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("lang") not in (None, "ka"):
            continue
        out.extend(p for p in map(parse, row.get("changes") or []) if p)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("edits", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--agent", default="shorts-review")
    a = ap.parse_args(argv)
    pairs = load(a.edits)
    if a.dry_run:
        for p in pairs:
            print(f"[{p['category']}] {p['wrong']} → {p['right']} ({p['reason']})")
    else:
        if __package__:
            from .. import memory
        else:  # run as a file from the repo root
            sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
            from kaeasy import memory
        for p in pairs:
            memory.learn(p["wrong"], p["right"], f"Shorts review {p['reason']}", p["category"], a.agent)
    print(f"{len(pairs)} pairs {'found' if a.dry_run else 'imported'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
