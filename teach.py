"""Teach the gate: one entry point per action over lessons.py.

    python -m kaeasy.teach propose WRONG RIGHT --kind nonword|form|usage --quote "…" --by NAME [--why …]
    python -m kaeasy.teach list [--state S] [--kind K] [--since YYYY-MM-DD]
    python -m kaeasy.teach show ID|WRONG
    python -m kaeasy.teach approve ID --by NAME [--attested-ok REASON]
    python -m kaeasy.teach retire ID --by NAME --reason false_positive|context|superseded|duplicate|test
    python -m kaeasy.teach reopen ID --by NAME --reason "…"
    python -m kaeasy.teach judge FID ok|wrong --by NAME [--note …]
    python -m kaeasy.teach stats [--last 50] [--since YYYY-MM-DD]
    python -m kaeasy.teach graduate ID --by NAME
    python -m kaeasy.teach import-memory --by NAME [--apply] [--quote WORD=TEXT ...] [--kind WORD=KIND ...]

Every action prints human-readable text; --json prints machine output. Anything that changes state needs
--by NAME, and NAME must be in $KAEASY_DATA_DIR/teachers.json ({"edo": "owner"} when the file is missing).
The ka_teach tool calls handle(action, **kwargs), which returns the same result as JSON and never raises.
"""
from __future__ import annotations

import argparse
import inspect
import json
import sys

from . import lessons, memory

# Memory rows a language job or a person wrote; the 442 editor diffs (agent tt-shorts) are edits, not lessons.
LEARNED_AGENTS = {"corpus-review", "human", "teacher"}
ACTION_NAMES = lessons.TEACH_ACTIONS
MUTATING = {"propose", "approve", "retire", "reopen", "judge", "graduate", "import-memory"}


def _gate(by: str | None) -> dict | None:
    if not (by or "").strip():
        return {"refused": "no_actor", "detail": "--by NAME is required for anything that changes state"}
    if not lessons.is_teacher(by):
        return {"refused": "not_a_teacher", "detail": f"„{by}“ is not in {lessons.teachers_path()}"}
    return None


def _summary(lesson: lessons.Lesson) -> dict:
    return {"id": lesson.id, "wrong": lesson.wrong, "right": lesson.right, "kind": lesson.kind,
            "state": lesson.state, "since": lesson.state_since, "readers": lesson.readers,
            "days": len(lesson.days), "observations": lesson.observations, "judged_ok": lesson.judged_ok,
            "judged_wrong": lesson.judged_wrong, "contested": lesson.contested}


# Actions -------------------------------------------------------------------------------------------------------

def do_propose(wrong: str = "", right: str = "", kind: str = "", why: str = "", quote: str = "", by: str = "",
               reader: str | None = None, ref: str | None = None, url: str | None = None,
               category: str = "lexical") -> dict:
    if (bad := _gate(by)):
        return bad
    return lessons.propose(wrong, right, kind, why=why, quote=quote, by=by, reader=reader, ref=ref, url=url,
                           category=category)


def do_list(state: str | None = None, kind: str | None = None, since: str | None = None) -> dict:
    rows = []
    for lesson in lessons.fold().values():
        if state and lesson.state != state:
            continue
        if kind and lesson.kind != kind:
            continue
        if since and lesson.created[:10] < since:
            continue
        rows.append(_summary(lesson))
    return {"lessons": rows, "count": len(rows)}


def do_show(id: str = "") -> dict:
    lesson = lessons.get(id)
    if lesson is None:
        return {"refused": "unknown_lesson", "detail": id}
    verdicts = lessons.judgements()
    fired = lessons.firings(lesson.id)
    recent = [{"fid": f["fid"], "ts": f.get("ts"), "ref": f.get("ref"), "state": f.get("state"),
               "snippet": f.get("snippet"), "verdict": (verdicts.get(f["fid"]) or {}).get("verdict")}
              for f in fired[-10:]]
    return {"lesson": lesson.as_dict(), "fired": len(fired), "firings": recent}


def do_approve(id: str = "", by: str = "", attested_ok: str | None = None) -> dict:
    return _gate(by) or lessons.approve(id, by, attested_ok=attested_ok)


def do_retire(id: str = "", by: str = "", reason: str = "", note: str = "") -> dict:
    return _gate(by) or lessons.retire(id, by, reason, note=note)


def do_reopen(id: str = "", by: str = "", reason: str = "") -> dict:
    return _gate(by) or lessons.reopen(id, by, reason)


def do_judge(fid: str = "", verdict: str = "", by: str = "", note: str = "") -> dict:
    return _gate(by) or lessons.judge(fid, verdict, by, note=note)


def do_stats(last: int = lessons.BREAKER_LAST, since: str | None = None) -> dict:
    return lessons.stats(last=int(last or lessons.BREAKER_LAST), since=since)


def do_graduate(id: str = "", by: str = "") -> dict:
    return _gate(by) or lessons.graduate(id, by)


def do_import_memory(by: str = "", apply: bool = False, quotes: dict | None = None,
                     kinds: dict | None = None) -> dict:
    """Bring the single-word rows a language job or a person wrote into the lessons log as proposals.

    Memory rows carry neither a quote nor a kind, and intake needs both, so a teacher supplies them per word
    (--quote WORD=TEXT, --kind WORD=KIND). Rows without them are listed, not imported. Dry run unless apply."""
    if apply and (bad := _gate(by)):
        return bad
    quotes, kinds = quotes or {}, kinds or {}
    seen: set[str] = set()
    plan = []
    for row in memory._rows():
        agent, wrong = str(row.get("agent") or ""), str(row.get("wrong") or "")
        if agent not in LEARNED_AGENTS or not lessons.is_single_word(lessons.normalise(wrong)):
            continue
        key = lessons.normalise(wrong)
        if key in seen:
            continue
        seen.add(key)
        item = {"wrong": wrong, "right": row.get("right"), "agent": agent, "id": lessons.lesson_id(wrong)}
        quote, kind = quotes.get(wrong) or row.get("quote"), kinds.get(wrong) or row.get("kind")
        existing = lessons.get(wrong)
        if existing is not None:
            item["result"] = {"exists": existing.state}
        elif not quote or not kind:
            item["result"] = {"needs": [k for k, v in (("quote", quote), ("kind", kind)) if not v]}
        elif apply:
            item["result"] = lessons.propose(wrong, row.get("right", ""), kind, why=row.get("reason", ""),
                                             quote=quote, by=agent, category=row.get("category") or "lexical",
                                             imported={"from": "mistakes.jsonl", "ts": row.get("ts"),
                                                       "by": lessons._actor(by)})
        else:
            item["result"] = {"would_propose": kind}
        plan.append(item)
    return {"applied": bool(apply), "rows": plan, "count": len(plan)}


ACTIONS = {"propose": do_propose, "list": do_list, "show": do_show, "approve": do_approve, "retire": do_retire,
           "reopen": do_reopen, "judge": do_judge, "stats": do_stats, "graduate": do_graduate,
           "import-memory": do_import_memory}


def run(action: str, **kwargs) -> dict:
    """Call one action with the arguments it knows; unknown arguments are ignored."""
    action = (action or "").replace("_", "-")
    fn = ACTIONS.get(action)
    if fn is None:
        return {"error": f"unknown action „{action}“; one of {', '.join(ACTION_NAMES)}"}
    params = inspect.signature(fn).parameters
    return fn(**{k: v for k, v in kwargs.items() if k in params and v is not None})


# Human output --------------------------------------------------------------------------------------------------

def _line(s: dict) -> str:
    return (f"{s['id']}  {s['state']:<9} {s['kind']:<7} {s['wrong']} → {s['right']}  "
            f"readers={','.join(s['readers']) or '-'} days={s['days']} ok={s['judged_ok']} wrong={s['judged_wrong']}"
            + ("  CONTESTED" if s.get("contested") else ""))


def render(action: str, out: dict) -> str:
    if "error" in out:
        return f"error: {out['error']}"
    if "refused" in out:
        return f"refused: {out['refused']}" + (f" ({out['detail']})" if out.get("detail") else "")
    action = action.replace("_", "-")
    if action == "propose":
        head = f"{out['id']} {out['state']} [{out['kind']}] " + ("created" if out.get("created") else "existing")
        return head + (f"\nnote: {out['note']}" if out.get("note") else "")
    if action == "list":
        return "\n".join([_line(s) for s in out["lessons"]] + [f"{out['count']} lesson(s)"])
    if action == "show":
        lesson = out["lesson"]
        lines = [_line(_summary(lessons.get(lesson["id"]))),
                 (f"category={lesson['category']} created={lesson['created']} since={lesson['state_since']}"
                  f" owner={lesson['owner'] or '-'} rights={lesson['rights']}"),
                 f"attest={lesson['attest'] or 'none (no index yet)'}", "sources:"]
        lines += [f"  {s.get('ts', '')} {s.get('ev')} by {s.get('actor')}"
                  f"{' (' + s['reader'] + ')' if s.get('reader') else ''} ref={s.get('ref') or '-'}: "
                  f"„{s.get('quote', '')}“" for s in lesson["sources"]]
        lines.append(f"firings: {out['fired']}")
        lines += [f"  {f['fid']} {f.get('ts', '')} ref={f.get('ref') or '-'} [{f.get('verdict') or 'unjudged'}] "
                  f"{f.get('snippet', '')}" for f in out["firings"]]
        lines.append("history:")
        lines += [f"  {e.get('ts', '')} {e.get('ev')} by {e.get('actor', '-')}"
                  + "".join(f" {k}={e[k]}" for k in ("to", "reason", "verdict", "fid") if e.get(k))
                  for e in lesson["history"]]
        if lesson["ignored"]:
            lines.append(f"ignored events (no transition): {len(lesson['ignored'])}")
        return "\n".join(lines)
    if action == "stats":
        p, b = out["precision"], out["breaker"]
        val = f"{p['value']:.3f}" if p["value"] is not None else "n/a"
        return "\n".join([
            f"correct text refused this week: {out['weekly_wrong_refusals']}  ({out['weekly_line']})",
            f"gate precision over the last {p['n']} judged firings: {val} (ok {p['ok']}, wrong {p['wrong']})",
            f"unjudged firings: {out['unjudged_firings']} of {out['firings']}",
            "breaker: " + ("OPEN, " + "; ".join(b["reasons"]) if b["open"] else "closed"),
            f"lessons by state: {out['funnel']['by_state']}",
            f"lessons by kind: {out['funnel']['by_kind']}",
            f"never promoted (> {lessons.STALE_DAYS} days): {', '.join(out['never_promoted']) or 'none'}",
            f"contested tombstones: {', '.join(out['contested']) or 'none'}",
            f"misses: {out['misses']}"])
    if action == "graduate":
        return (f"{out['id']} is canon. Add to data/wrong_forms.json \"error\" by PR:\n  {out['wrong_forms_line']}\n"
                f"and to tests/test_lint.py test_detects:\n  {out['test_case']}")
    if action == "import-memory":
        lines = [f"{r['id']} {r['wrong']} → {r['right']} ({r['agent']}): {json.dumps(r['result'], ensure_ascii=False)}"
                 for r in out["rows"]]
        return "\n".join(lines + [f"{out['count']} row(s); " + ("applied" if out["applied"] else "dry run")])
    if action == "judge":
        return f"{out['fid']} judged {out['verdict']}; {out['id']} is now {out['state']}"
    return f"{out.get('id', '')} {out.get('from', '')} -> {out.get('state', '')}".strip()


def handle(action: str = "", **kwargs) -> str:
    """The ka_teach tool: run one action and return JSON with the result and its text. Never raises."""
    try:
        out = run(action, **kwargs)
        ok = "error" not in out and "refused" not in out
        return json.dumps({"action": action, "ok": ok, **out, "text": render(action, out)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"action": action, "ok": False, "error": f"ka_teach failed: {e}"}, ensure_ascii=False)


# CLI -----------------------------------------------------------------------------------------------------------

def _pairs(items: list[str] | None, flag: str) -> dict:
    out = {}
    for item in items or []:
        if "=" not in item:
            raise SystemExit(f"{flag} takes WORD=VALUE, got {item!r}")
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="machine output")
    ap = argparse.ArgumentParser(prog="python -m kaeasy.teach", description="Teach the kaeasy gate.")
    sub = ap.add_subparsers(dest="action", required=True)

    p = sub.add_parser("propose", parents=[common], help="propose a lesson")
    p.add_argument("wrong")
    p.add_argument("right")
    p.add_argument("--kind", required=True, choices=lessons.KINDS)
    p.add_argument("--quote", required=True, help="the sentence the wrong word was seen in")
    p.add_argument("--why", default="")
    p.add_argument("--by", required=True)
    p.add_argument("--reader")
    p.add_argument("--ref")
    p.add_argument("--url")
    p.add_argument("--category", default="lexical", choices=memory.CATEGORIES)

    p = sub.add_parser("list", parents=[common], help="list lessons")
    p.add_argument("--state", choices=lessons.STATES)
    p.add_argument("--kind", choices=lessons.KINDS)
    p.add_argument("--since", help="created on or after YYYY-MM-DD")

    p = sub.add_parser("show", parents=[common], help="one lesson with its quotes, firings and history")
    p.add_argument("id", help="lesson id or the wrong word")

    p = sub.add_parser("approve", parents=[common], help="teacher: enforce a lesson")
    p.add_argument("id")
    p.add_argument("--by", required=True)
    p.add_argument("--attested-ok", dest="attested_ok")

    p = sub.add_parser("retire", parents=[common], help="teacher: tombstone a lesson")
    p.add_argument("id")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", required=True, choices=lessons.RETIRE_REASONS)
    p.add_argument("--note", default="")

    p = sub.add_parser("reopen", parents=[common], help="teacher: bring a tombstone back as a candidate")
    p.add_argument("id")
    p.add_argument("--by", required=True)
    p.add_argument("--reason", required=True)

    p = sub.add_parser("judge", parents=[common], help="teacher: judge one firing")
    p.add_argument("fid")
    p.add_argument("verdict", choices=("ok", "wrong"))
    p.add_argument("--by", required=True)
    p.add_argument("--note", default="")

    p = sub.add_parser("stats", parents=[common], help="precision, funnel, breaker, weekly number")
    p.add_argument("--last", type=int, default=lessons.BREAKER_LAST)
    p.add_argument("--since")

    p = sub.add_parser("graduate", parents=[common], help="teacher: print the wrong_forms.json line for a PR")
    p.add_argument("id")
    p.add_argument("--by", required=True)

    p = sub.add_parser("import-memory", parents=[common], help="propose memory rows from language jobs")
    p.add_argument("--by", default="")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--quote", action="append", metavar="WORD=TEXT")
    p.add_argument("--kind", action="append", metavar="WORD=KIND")
    return ap


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    a = vars(parser().parse_args(argv))
    action, as_json = a.pop("action"), a.pop("json")
    if action == "import-memory":
        a["quotes"], a["kinds"] = _pairs(a.pop("quote"), "--quote"), _pairs(a.pop("kind"), "--kind")
    try:
        out = run(action, **a)
    except Exception as e:
        out = {"error": str(e)}
    print(json.dumps(out, ensure_ascii=False, indent=1) if as_json else render(action, out))
    return 1 if ("error" in out or "refused" in out) else 0


if __name__ == "__main__":
    sys.exit(main())
