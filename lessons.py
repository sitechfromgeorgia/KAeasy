"""Lessons: the gate's learned rules, kept as an append-only event log.

A lesson is one wrong Georgian word with its correction. Its history lives in `$KAEASY_DATA_DIR/lessons.jsonl`,
one JSON event per line. Lines are only ever appended: retiring or rejecting a lesson appends an event, it never
deletes one. A lesson's current state is the replay of its events (`fold()`).

The lesson id comes from the word (`"L" + sha1(normalise(wrong))[:8]`), so proposing the same word again lands on
the same lesson, and a retired word keeps its tombstone: a later proposal only records an `observe` event.

Kinds:
    nonword  the word does not exist in Georgian
    form     it exists only as a misspelling or a wrong inflection, wrong in every context
    usage    a real word used wrongly in one context; advisory forever, it never reaches the gate

States and the exact transitions `fold()` applies (an event that does not match a row is recorded and ignored):

    propose                       (new)                        -> candidate, or advisory when kind is usage
    observe, attest, judge        any                          -> unchanged
    verify result=impossible      candidate                    -> held
    promote to=shadow             candidate, held              -> shadow       (nonword/form only)
    promote to=enforced           shadow                       -> enforced     (nonword/form only)
    approve                       candidate, held, shadow      -> enforced     (nonword/form only)
    demote                        enforced, canon              -> shadow
    graduate                      enforced                     -> canon
    retire                        any state but a tombstone    -> retired
    reject                        candidate, held, shadow, advisory -> rejected
    reopen                        retired, rejected            -> candidate, or advisory when kind is usage

The library functions below refuse an event that has no row before writing it. Automatic follow-ups:
a firing judged wrong demotes an enforced (or canon) lesson to shadow at once; a second wrong judgement retires it
with reason false_positive.

`compile()` writes `learned_forms.json` for the linter: `error` holds enforced lessons, `warn` holds shadow ones.

No network and no model calls here: proposals are validated by the caller (veasy); this module stores, folds,
compiles and reports.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

from . import lint
from .memory import CATEGORIES, data_dir, normalise

try:  # POSIX only; on Windows the thread lock is all we have
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

ROOT = Path(__file__).resolve().parent

ATTEST_MIN_COUNT = 3  # occurrences in human-written articles
ATTEST_MIN_OUTLETS = 3  # distinct outlets carrying them
EVENTS = ("propose", "observe", "attest", "verify", "promote", "demote", "approve", "retire", "reject", "reopen",
          "judge", "graduate")
STATES = ("candidate", "held", "shadow", "enforced", "canon", "retired", "rejected", "advisory")
KINDS = ("nonword", "form", "usage")
ENFORCEABLE = frozenset({"nonword", "form"})
TOMBSTONES = frozenset({"retired", "rejected"})
RETIRE_REASONS = ("false_positive", "context", "superseded", "duplicate", "test")
LEARNED_CHECKS = ("learned_form", "learned_hint")
DEFAULT_TEACHERS = {"edo": "owner"}
TEACH_ACTIONS = ("propose", "list", "show", "approve", "retire", "reopen", "judge", "stats", "graduate",
                 "import-memory")

SHADOW_DAYS = 3  # a shadow lesson fires as a warning for at least this long before automatic promotion
GRADUATE_DAYS = 14  # enforced this long with no wrong judgement before it may graduate to wrong_forms.json
STALE_DAYS = 14  # a candidate or held lesson this old is reported as "never promoted"
BREAKER_LAST = 50
BREAKER_PRECISION = 0.98
BREAKER_DAYS = 7
CONTESTED = 3  # observations on a tombstone before the report calls it contested

GEO_WORD = re.compile(r"[ა-ჰ]+")
LESSON_ID = re.compile(r"^L[0-9a-f]{8}$")
_EDGE = re.compile(r"^[\W_]+|[\W_]+$")

_lock = threading.Lock()
_cache: dict = {"key": None, "events": []}


# Paths and time ------------------------------------------------------------------------------------------------

def _dir() -> Path:
    d = data_dir()
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_path() -> Path:
    return _dir() / "lessons.jsonl"


def table_path() -> Path:
    return _dir() / "learned_forms.json"


def firings_dir() -> Path:
    d = _dir() / "firings"
    d.mkdir(parents=True, exist_ok=True)
    return d


def teachers_path() -> Path:
    return _dir() / "teachers.json"


def _now() -> datetime:
    """Local time with its offset. Tests replace this to move the clock."""
    return datetime.now().astimezone()


def _ts(dt: datetime | None = None) -> str:
    return (dt or _now()).isoformat(timespec="seconds")


def parse_ts(ts: str) -> datetime:
    dt = datetime.fromisoformat(ts)
    return dt if dt.tzinfo else dt.astimezone()


# Words ---------------------------------------------------------------------------------------------------------

def lesson_id(wrong: str) -> str:
    return "L" + hashlib.sha1(normalise(wrong).encode("utf-8")).hexdigest()[:8]


def word_re(word: str) -> re.Pattern:
    """The linter's whole-word matcher for one word (Georgian word boundaries)."""
    return lint._forms_re({word: word})


def is_single_word(word: str) -> bool:
    return bool(re.fullmatch(r"[ა-ჰ]+", word or ""))


def _shape_refusal(word: str) -> str | None:
    if re.search(r"[A-Za-z]", word):
        return "latin"
    if re.search(r"\d", word):
        return "digits"
    if not is_single_word(word):
        return "not_a_georgian_word"
    if len(word) < 4:
        return "too_short"
    return None


# Allow-lists ---------------------------------------------------------------------------------------------------

@lru_cache(maxsize=1)
def allow_lists() -> dict[str, frozenset[str]]:
    """Georgian words that must never become a learned error, by source.

    examples: every word on the ✅ side of `skills/*/examples/*.md` (the explanation in parentheses is left out,
    since it often names the wrong form); lexicon: spoken forms in `data/lexicon_ka.json`; glossary: `preferred`
    and `spoken` terms; wrong_forms: the right forms and the `warn` forms of `data/wrong_forms.json`.
    """
    out: dict[str, set[str]] = {"examples": set(), "lexicon": set(), "glossary": set(), "wrong_forms": set()}
    for md in sorted((ROOT / "skills").glob("*/examples/*.md")):
        for line in md.read_text(encoding="utf-8").splitlines():
            for m in re.finditer(r"✅\s*(.+?)(?:\s*\(|❌|$)", line):
                out["examples"].update(GEO_WORD.findall(m.group(1)))
    lex = ROOT / "data" / "lexicon_ka.json"
    if lex.exists():
        for v in (json.loads(lex.read_text(encoding="utf-8")).get("words") or {}).values():
            out["lexicon"].update(GEO_WORD.findall(str(v)))
    for gp in sorted((ROOT / "data" / "glossary").glob("*.json")):
        for entry in json.loads(gp.read_text(encoding="utf-8")):
            for k in ("preferred", "spoken"):
                out["glossary"].update(GEO_WORD.findall(str(entry.get(k) or "")))
    for table in (lint.WRONG_FORMS.values(), lint.DATED_FORMS, lint.DATED_FORMS.values()):
        for w in table:
            out["wrong_forms"].update(GEO_WORD.findall(w))
    return {k: frozenset(normalise(w) for w in v) for k, v in out.items()}


def allow_hit(word: str) -> str | None:
    """The allow-list that holds this word, or None. A word in wrong_forms.json `error` is "canon"."""
    w = normalise(word)
    if w in {normalise(k) for k in lint.WRONG_FORMS}:
        return "canon"
    for name, words in allow_lists().items():
        if w in words:
            return name
    return None


# Teachers ------------------------------------------------------------------------------------------------------

def teachers() -> dict[str, str]:
    p = teachers_path()
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {str(k).strip().casefold(): str(v) for k, v in data.items()}
        except (OSError, json.JSONDecodeError):
            pass
    return dict(DEFAULT_TEACHERS)


def is_teacher(name: str | None) -> bool:
    return bool(name) and name.strip().casefold() in teachers()


def _actor(name: str | None) -> str:
    return (name or "").strip().casefold()


# The log -------------------------------------------------------------------------------------------------------

def _append(event: dict, path: Path | None = None) -> dict:
    ev = {"ts": event.get("ts") or _ts(), **event}
    ev = {k: v for k, v in ev.items() if v is not None}
    line = json.dumps(ev, ensure_ascii=False) + "\n"
    p = path or log_path()
    with _lock, p.open("a", encoding="utf-8") as fh:
        if fcntl:
            fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.write(line)
            fh.flush()
        finally:
            if fcntl:
                fcntl.flock(fh, fcntl.LOCK_UN)
    return ev


def _read_jsonl(p: Path) -> list[dict]:
    rows = []
    if not p.exists():
        return rows
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def read_events() -> list[dict]:
    """Every event in the log, in file order. Malformed lines are skipped."""
    p = log_path()
    try:
        st = p.stat()
        key = (str(p), st.st_mtime_ns, st.st_size)
    except OSError:
        return []
    if _cache["key"] != key:
        _cache["events"] = _read_jsonl(p)
        _cache["key"] = key
    return list(_cache["events"])


# The fold ------------------------------------------------------------------------------------------------------

@dataclass
class Lesson:
    id: str
    wrong: str
    kind: str
    category: str = "lexical"
    state: str = "candidate"
    state_since: str = ""
    created: str = ""
    owner: str | None = None
    rights: dict[str, int] = field(default_factory=dict)
    modes: list[str] = field(default_factory=lambda: list(lint.MODES))
    sources: list[dict] = field(default_factory=list)
    readers: list[str] = field(default_factory=list)
    days: list[str] = field(default_factory=list)
    observations: int = 0
    observed_dead: int = 0  # observations recorded while tombstoned
    attest: dict | None = None
    verification: dict | None = None
    judged_ok: int = 0
    judged_wrong: int = 0
    strikes: int = 0  # wrong judgements since creation or the last reopen
    reason: str | None = None  # why it was last retired, rejected or reopened
    history: list[dict] = field(default_factory=list)
    ignored: list[dict] = field(default_factory=list)  # events that matched no transition

    @property
    def right(self) -> str:
        if not self.rights:
            return ""
        return max(self.rights.items(), key=lambda kv: kv[1])[0]

    @property
    def tombstoned(self) -> bool:
        return self.state in TOMBSTONES

    @property
    def contested(self) -> bool:
        return self.tombstoned and self.observed_dead >= CONTESTED

    def proposers(self) -> set[str]:
        return {_actor(s.get("actor")) for s in self.sources if s.get("actor")}

    def as_dict(self, history: bool = True) -> dict:
        d = asdict(self)
        d["right"] = self.right
        d["contested"] = self.contested
        if not history:
            d.pop("history")
            d.pop("ignored")
        return d


def _family(ev: dict) -> str:
    reader = ev.get("reader")
    if reader:
        reader = str(reader)
        return reader if reader.startswith("human:") else reader.split(":", 1)[0]
    actor = _actor(ev.get("actor"))
    return f"human:{actor}" if is_teacher(actor) else actor


def _source(ev: dict) -> dict:
    keys = ("ts", "ev", "actor", "reader", "right", "kind", "why", "quote", "ref", "url", "corpus_key", "imported")
    return {k: ev[k] for k in keys if ev.get(k) is not None}


def _observe(lesson: Lesson, ev: dict) -> None:
    if ev.get("right"):
        lesson.rights[ev["right"]] = lesson.rights.get(ev["right"], 0) + 1
    lesson.sources.append(_source(ev))
    fam = _family(ev)
    if fam and fam not in lesson.readers:
        lesson.readers.append(fam)
    day = str(ev.get("ts", ""))[:10]
    if day and day not in lesson.days:
        lesson.days.append(day)
    lesson.observations += 1


def _set(lesson: Lesson, state: str, ev: dict) -> None:
    lesson.state = state
    lesson.state_since = ev.get("ts", "")


def _apply(lessons: dict[str, Lesson], ev: dict) -> None:
    kind_of = ev.get("ev")
    lid = ev.get("id")
    if kind_of not in EVENTS or not lid:
        return
    lesson = lessons.get(lid)
    if lesson is None:
        if kind_of != "propose" or not ev.get("wrong"):
            return
        kind = ev.get("kind") if ev.get("kind") in KINDS else "usage"
        lesson = Lesson(id=lid, wrong=ev["wrong"], kind=kind,
                        category=ev.get("category") if ev.get("category") in CATEGORIES else "lexical",
                        created=ev.get("ts", ""))
        _set(lesson, "advisory" if kind == "usage" else "candidate", ev)
        _observe(lesson, ev)
        lesson.history.append(ev)
        lessons[lid] = lesson
        return

    lesson.history.append(ev)
    st, enforceable = lesson.state, lesson.kind in ENFORCEABLE
    ok = True
    if kind_of in ("propose", "observe"):
        _observe(lesson, ev)
        if lesson.tombstoned:
            lesson.observed_dead += 1
    elif kind_of == "attest":
        lesson.attest = {k: ev.get(k) for k in ("wrong_n", "right_n", "outlets", "index_tokens", "at")}
    elif kind_of == "verify":
        lesson.verification = {k: ev.get(k) for k in ("result", "rules", "ts")}
        if ev.get("result") == "impossible" and st == "candidate":
            _set(lesson, "held", ev)
    elif kind_of == "promote":
        to = ev.get("to")
        if enforceable and to == "shadow" and st in ("candidate", "held"):
            _set(lesson, "shadow", ev)
        elif enforceable and to == "enforced" and st == "shadow":
            _set(lesson, "enforced", ev)
        else:
            ok = False
    elif kind_of == "approve":
        if enforceable and st in ("candidate", "held", "shadow"):
            _set(lesson, "enforced", ev)
            lesson.owner = _actor(ev.get("actor"))
        else:
            ok = False
    elif kind_of == "demote":
        if st in ("enforced", "canon"):
            _set(lesson, "shadow", ev)
        else:
            ok = False
    elif kind_of == "graduate":
        if st == "enforced":
            _set(lesson, "canon", ev)
        else:
            ok = False
    elif kind_of == "retire":
        if st not in TOMBSTONES:
            _set(lesson, "retired", ev)
            lesson.reason = ev.get("reason")
        else:
            ok = False
    elif kind_of == "reject":
        if st in ("candidate", "held", "shadow", "advisory"):
            _set(lesson, "rejected", ev)
            lesson.reason = ev.get("reason")
        else:
            ok = False
    elif kind_of == "reopen":
        if st in TOMBSTONES:
            _set(lesson, "candidate" if enforceable else "advisory", ev)
            lesson.reason = ev.get("reason")
            lesson.strikes = 0
            lesson.observed_dead = 0
        else:
            ok = False
    elif kind_of == "judge":
        if ev.get("verdict") == "ok":
            lesson.judged_ok += 1
        elif ev.get("verdict") == "wrong":
            lesson.judged_wrong += 1
            lesson.strikes += 1
    if not ok:
        lesson.ignored.append(ev)


def fold(events: list[dict] | None = None) -> dict[str, Lesson]:
    """Replay events (the whole log by default) into lessons keyed by id."""
    lessons: dict[str, Lesson] = {}
    for ev in read_events() if events is None else events:
        _apply(lessons, ev)
    return lessons


def get(id_or_wrong: str) -> Lesson | None:
    key = (id_or_wrong or "").strip()
    lid = key if LESSON_ID.match(key) else lesson_id(key)
    return fold().get(lid)


def tombstoned() -> set[str]:
    """Normalised wrong words of retired and rejected lessons (memory.tombstoned_words() is the plain scan of the
    same log that memory.top() uses)."""
    return {normalise(lesson.wrong) for lesson in fold().values() if lesson.tombstoned}


# Intake --------------------------------------------------------------------------------------------------------

def _refused(reason: str, detail: str = "") -> dict:
    out = {"refused": reason}
    if detail:
        out["detail"] = detail
    return out


def propose(wrong: str, right: str, kind: str, why: str = "", quote: str = "", by: str = "",
            reader: str | None = None, ref: str | None = None, url: str | None = None,
            corpus_key: str | None = None, category: str = "lexical", imported: dict | None = None) -> dict:
    """Record a proposed lesson, or refuse it.

    Returns {"id", "state", "created", "kind"} (plus "note") or {"refused": reason, "detail": ...}. A word
    that is already a lesson gets an `observe` event (a vote for its right form and one more source); a
    tombstoned word stays tombstoned.
    """
    actor = _actor(by)
    if not actor:
        return _refused("no_actor", "say who proposes it (--by)")
    if kind not in KINDS:
        return _refused("bad_kind", f"kind must be one of {', '.join(KINDS)}")
    w = unicodedata.normalize("NFC", _EDGE.sub("", " ".join((wrong or "").split())))
    r = unicodedata.normalize("NFC", " ".join((right or "").split()))
    if not w or not r:
        return _refused("empty", "wrong and right must both be given")
    if normalise(w) == normalise(r):
        return _refused("same", "wrong and right are the same word")
    teacher = is_teacher(actor)
    if " " in w:
        if not (teacher and kind == "usage"):
            return _refused("multi_word", "one word only; a teacher may record a phrase with --kind usage")
        bad = next((x for x in (_shape_refusal(t) for t in w.split()) if x and x != "too_short"), None)
        if bad:
            return _refused(bad, "a phrase must be Georgian words")
    else:
        bad = _shape_refusal(w)
        if bad:
            return _refused(bad, "one Georgian word of at least 4 letters, no Latin letters, no digits")
    q = unicodedata.normalize("NFC", quote or "")
    if not word_re(w).search(q):
        return _refused("no_quote", "the quote must contain the wrong word as a whole word")

    lid = lesson_id(w)
    lesson = fold().get(lid)
    note = None
    nw, nr = normalise(w), normalise(r)
    if nw in nr or nr in nw:
        if kind != "usage":
            note = "kind forced to usage: one form contains the other, so the right choice depends on context"
        kind = "usage"
    if category not in CATEGORIES:
        category = "lexical"
    base = {"id": lid, "actor": actor, "reader": reader or (f"human:{actor}" if teacher else None),
            "wrong": w, "right": r, "kind": kind, "category": category, "why": (why or "")[:300] or None,
            "quote": q[:500], "ref": ref, "url": url, "corpus_key": corpus_key, "imported": imported}

    if lesson is not None and lesson.tombstoned:
        _append({**base, "ev": "observe"})
        return {"id": lid, "state": lesson.state, "created": False, "kind": lesson.kind,
                "note": "reopen needs a teacher"}
    hit = allow_hit(w)
    if hit == "canon":
        return _refused("already_canon", "already in data/wrong_forms.json")
    if hit:
        return _refused(f"allow_list:{hit}", f"„{w}“ is on the {hit} allow-list, so it is correct Georgian")
    if lesson is not None:
        _append({**base, "ev": "observe"})
        return {"id": lid, "state": lesson.state, "created": False, "kind": lesson.kind,
                "note": "seen again; recorded as an observation"}
    _append({**base, "ev": "propose"})
    out = {"id": lid, "state": "advisory" if kind == "usage" else "candidate", "created": True, "kind": kind}
    if note:
        out["note"] = note
    return out


# Teacher actions -----------------------------------------------------------------------------------------------

def _need_teacher(by: str) -> dict | None:
    if not _actor(by):
        return _refused("no_actor", "--by NAME is required")
    if not is_teacher(by):
        return _refused("not_a_teacher", f"„{by}“ is not in {teachers_path()}")
    return None


def _lesson_or_refusal(id_or_wrong: str) -> Lesson | dict:
    lesson = get(id_or_wrong)
    return lesson if lesson is not None else _refused("unknown_lesson", str(id_or_wrong))


def approve(id_or_wrong: str, by: str, attested_ok: str | None = None) -> dict:
    """Teacher approval: candidate, held or shadow becomes enforced. Replaces the two-reader rule and the circuit
    breaker. A wrong form that the attestation index has seen in human text needs `attested_ok` (a reason)."""
    if (bad := _need_teacher(by)):
        return bad
    lesson = _lesson_or_refusal(id_or_wrong)
    if isinstance(lesson, dict):
        return lesson
    if lesson.kind not in ENFORCEABLE:
        return _refused("usage_is_advisory", "a usage lesson never reaches the gate")
    if not is_single_word(lesson.wrong):
        return _refused("multi_word", "only a single word can be enforced")
    if (hit := allow_hit(lesson.wrong)):
        return _refused(f"allow_list:{hit}", "on an allow-list")
    if lesson.state in ("enforced", "canon") or lesson.tombstoned:
        return _refused(f"already_{lesson.state}", "use reopen for a tombstone" if lesson.tombstoned else "")
    if lesson.state not in ("candidate", "held", "shadow"):
        return _refused("bad_state", lesson.state)
    if lesson.attest and (lesson.attest.get("wrong_n") or 0) > 0 and not attested_ok:
        return _refused("attested", "human text uses this form; pass --attested-ok REASON to enforce it anyway")
    _append({"id": lesson.id, "ev": "approve", "actor": _actor(by), "from": lesson.state,
             "attested_ok": attested_ok, "attest": lesson.attest})
    compile()
    return {"id": lesson.id, "state": "enforced", "from": lesson.state}


def retire(id_or_wrong: str, by: str, reason: str, note: str = "") -> dict:
    if (bad := _need_teacher(by)):
        return bad
    if reason not in RETIRE_REASONS:
        return _refused("bad_reason", f"reason must be one of {', '.join(RETIRE_REASONS)}")
    lesson = _lesson_or_refusal(id_or_wrong)
    if isinstance(lesson, dict):
        return lesson
    if lesson.tombstoned:
        return _refused(f"already_{lesson.state}")
    _append({"id": lesson.id, "ev": "retire", "actor": _actor(by), "from": lesson.state, "reason": reason,
             "note": note or None})
    compile()
    return {"id": lesson.id, "state": "retired", "from": lesson.state}


def reject(id_or_wrong: str, by: str, reason: str, note: str = "") -> dict:
    """Tombstone a lesson that never reached the gate (refuted by attestation, a test word). For the daily job
    and imports; a teacher retires instead."""
    lesson = _lesson_or_refusal(id_or_wrong)
    if isinstance(lesson, dict):
        return lesson
    if not _actor(by) or not reason:
        return _refused("no_actor" if not _actor(by) else "no_reason")
    if lesson.state not in ("candidate", "held", "shadow", "advisory"):
        return _refused("bad_state", lesson.state)
    _append({"id": lesson.id, "ev": "reject", "actor": _actor(by), "from": lesson.state, "reason": reason,
             "note": note or None})
    compile()
    return {"id": lesson.id, "state": "rejected", "from": lesson.state}


def reopen(id_or_wrong: str, by: str, reason: str) -> dict:
    if (bad := _need_teacher(by)):
        return bad
    if not (reason or "").strip():
        return _refused("no_reason", "say why the tombstone is wrong")
    lesson = _lesson_or_refusal(id_or_wrong)
    if isinstance(lesson, dict):
        return lesson
    if not lesson.tombstoned:
        return _refused("not_tombstoned", lesson.state)
    _append({"id": lesson.id, "ev": "reopen", "actor": _actor(by), "from": lesson.state, "reason": reason})
    return {"id": lesson.id, "state": "candidate" if lesson.kind in ENFORCEABLE else "advisory",
            "from": lesson.state}


def graduate(id_or_wrong: str, by: str) -> dict:
    """Enforced for GRADUATE_DAYS with no wrong judgement: mark it canon and print the line and test a human adds
    to data/wrong_forms.json by PR. Until that PR is merged the compiled table keeps enforcing it."""
    if (bad := _need_teacher(by)):
        return bad
    lesson = _lesson_or_refusal(id_or_wrong)
    if isinstance(lesson, dict):
        return lesson
    if lesson.state != "enforced":
        return _refused("not_enforced", lesson.state)
    since = parse_ts(lesson.state_since) if lesson.state_since else _now()
    if _now() - since < timedelta(days=GRADUATE_DAYS):
        return _refused("too_early", f"enforced since {lesson.state_since}; needs {GRADUATE_DAYS} days")
    if lesson.judged_wrong:
        return _refused("judged_wrong", f"{lesson.judged_wrong} firing(s) judged wrong")
    _append({"id": lesson.id, "ev": "graduate", "actor": _actor(by)})
    compile()
    quote = next((s["quote"] for s in lesson.sources if s.get("quote")), lesson.wrong)
    return {"id": lesson.id, "state": "canon",
            "wrong_forms_line": json.dumps({lesson.wrong: lesson.right}, ensure_ascii=False)[1:-1] + ",",
            "test_case": "(" + json.dumps(quote, ensure_ascii=False) + ', "wrong_form"),'}


# Firings and judgements ----------------------------------------------------------------------------------------

def _firing_files() -> list[Path]:
    return sorted(firings_dir().glob("*.jsonl"))


def firings(lesson: str | None = None) -> list[dict]:
    rows = [r for p in _firing_files() for r in _read_jsonl(p)]
    return [r for r in rows if lesson is None or r.get("id") == lesson]


def _text_sha(snippet: str) -> str:
    return hashlib.sha1(unicodedata.normalize("NFC", snippet or "").encode("utf-8")).hexdigest()[:12]


def record_firings(findings: list, agent: str, ref: str | None, mode: str) -> int:
    """Log learned findings (Finding objects or their dicts) to firings/YYYY-MM.jsonl.

    Deduplicated on (lesson id, ref, text_sha), where text_sha hashes the finding's snippet, so a writer retry
    that keeps the same sentence counts once. Returns the number of new rows."""
    rows = [f.as_dict() if hasattr(f, "as_dict") else dict(f) for f in findings or []]
    rows = [r for r in rows if r.get("check") in LEARNED_CHECKS]
    if not rows:
        return 0
    lessons = fold()
    ids = {normalise(lesson.wrong): lid for lid, lesson in lessons.items()}
    seen = {(r.get("id"), r.get("ref"), r.get("text_sha")) for r in firings()}
    now = _now()
    path = firings_dir() / f"{now:%Y-%m}.jsonl"
    n = 0
    for r in rows:
        snippet = str(r.get("snippet") or "")
        lid = r.get("lesson") or ids.get(normalise(str(r.get("word") or "")))
        if not lid:
            continue
        sha = _text_sha(snippet)
        key = (lid, ref, sha)
        if key in seen:
            continue
        seen.add(key)
        lesson = lessons.get(lid)
        state = lesson.state if lesson else ("enforced" if r["check"] == "learned_form" else "shadow")
        fid = "F" + hashlib.sha1(f"{lid}|{ref}|{sha}".encode()).hexdigest()[:10]
        _append({"ts": _ts(now), "fid": fid, "id": lid, "state": state, "check": r["check"], "agent": agent or None,
                 "ref": ref, "mode": mode, "snippet": snippet[:300], "text_sha": sha,
                 "allowed": r["check"] == "learned_hint" and state in ("enforced", "canon")}, path)
        n += 1
    return n


def judgements() -> dict[str, dict]:
    """The judge event for each firing id."""
    return {ev["fid"]: ev for ev in read_events() if ev.get("ev") == "judge" and ev.get("fid")}


def judge(fid: str, verdict: str, by: str, note: str = "") -> dict:
    """A teacher's verdict on one firing. `wrong` demotes an enforced lesson at once and a second `wrong` retires
    it. Nobody may judge a firing of a lesson they proposed as `ok`."""
    if (bad := _need_teacher(by)):
        return bad
    if verdict not in ("ok", "wrong"):
        return _refused("bad_verdict", "ok or wrong")
    firing = next((f for f in firings() if f.get("fid") == fid), None)
    if firing is None:
        return _refused("unknown_firing", fid)
    if fid in judgements():
        return _refused("already_judged", judgements()[fid].get("verdict", ""))
    lesson = fold().get(firing["id"])
    if lesson is None:
        return _refused("unknown_lesson", firing["id"])
    actor = _actor(by)
    if verdict == "ok" and actor in lesson.proposers():
        return _refused("own_proposal", "a teacher may not judge their own proposal as ok")
    _append({"id": lesson.id, "ev": "judge", "actor": actor, "fid": fid, "verdict": verdict,
             "firing_state": firing.get("state"), "ref": firing.get("ref"), "note": note or None})
    out = {"id": lesson.id, "fid": fid, "verdict": verdict, "state": lesson.state}
    if verdict == "wrong":
        lesson = fold()[lesson.id]
        if lesson.strikes >= 2 and lesson.state in ("shadow", "enforced", "canon"):
            _append({"id": lesson.id, "ev": "retire", "actor": "auto", "from": lesson.state,
                     "reason": "false_positive", "note": f"second wrong judgement ({fid})"})
            out["state"] = "retired"
        elif lesson.state in ("enforced", "canon"):
            _append({"id": lesson.id, "ev": "demote", "actor": "auto", "from": lesson.state, "to": "shadow",
                     "reason": f"judged wrong ({fid})"})
            out["state"] = "shadow"
        if out["state"] != lesson.state:
            compile()
    return out


# The circuit breaker and automatic promotion -------------------------------------------------------------------

def breaker(now: datetime | None = None) -> dict:
    """Open when the last BREAKER_LAST judged firings of enforced lessons have precision below BREAKER_PRECISION,
    or when any firing was judged wrong in the last BREAKER_DAYS days. While open, nothing is promoted
    automatically; a teacher's approve still works."""
    now = now or _now()
    judged = [ev for ev in read_events() if ev.get("ev") == "judge" and ev.get("verdict") in ("ok", "wrong")]
    enforced = [ev for ev in judged if ev.get("firing_state") in ("enforced", "canon")][-BREAKER_LAST:]
    ok = sum(ev["verdict"] == "ok" for ev in enforced)
    precision = ok / len(enforced) if enforced else None
    recent = [ev for ev in judged if ev["verdict"] == "wrong"
              and now - parse_ts(ev["ts"]) <= timedelta(days=BREAKER_DAYS)]
    reasons = []
    if precision is not None and precision < BREAKER_PRECISION:
        reasons.append(f"precision {precision:.3f} < {BREAKER_PRECISION} over the last {len(enforced)} judged")
    if recent:
        reasons.append(f"{len(recent)} firing(s) judged wrong in the last {BREAKER_DAYS} days")
    return {"open": bool(reasons), "reasons": reasons, "precision": precision, "judged": len(enforced),
            "wrong_recent": len(recent)}


def promote_due(now: datetime | None = None, dry: bool = False) -> dict:
    """Automatic shadow -> enforced, the part of the daily tick that needs no attestation index.

    A shadow lesson of kind nonword/form is promoted when it has been in shadow for SHADOW_DAYS, has no wrong
    judgement since creation or reopen, and every firing outside its own evidence (refs it was proposed from)
    has been judged ok. Nothing moves while the circuit breaker is open."""
    now = now or _now()
    br = breaker(now)
    out = {"breaker": br, "promoted": [], "waiting": {}}
    if br["open"]:
        return out
    verdicts = {fid: ev.get("verdict") for fid, ev in judgements().items()}
    fired = firings()
    for lesson in fold().values():
        if lesson.state != "shadow" or lesson.kind not in ENFORCEABLE:
            continue
        if now - parse_ts(lesson.state_since) < timedelta(days=SHADOW_DAYS):
            out["waiting"][lesson.id] = f"in shadow less than {SHADOW_DAYS} days"
            continue
        if lesson.strikes:
            out["waiting"][lesson.id] = "judged wrong before; needs a teacher"
            continue
        own = {s.get("ref") for s in lesson.sources if s.get("ref")}
        open_ = [f["fid"] for f in fired if f.get("id") == lesson.id and f.get("ref") not in own
                 and verdicts.get(f["fid"]) != "ok"]
        if open_:
            out["waiting"][lesson.id] = f"{len(open_)} firing(s) not judged ok"
            continue
        if not dry:
            _append({"id": lesson.id, "ev": "promote", "actor": "tick", "from": "shadow", "to": "enforced"})
        out["promoted"].append(lesson.id)
    if out["promoted"] and not dry:
        compile()
    return out


def load_attest(path: str | os.PathLike | None) -> dict[str, tuple[int, int]] | None:
    """Read the word index built by veasy's ops/attest_index.py: word -> (articles, outlets).

    None means "there is no usable index", which is different from an empty one: with no index a lesson
    cannot be verified and must wait for a teacher, never be promoted on a model's word alone.
    """
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    out: dict[str, tuple[int, int]] = {}
    try:
        with p.open(encoding="utf-8") as fh:
            for line in fh:
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 3:
                    continue
                try:
                    out[parts[0]] = (int(parts[1]), int(parts[2]))
                except ValueError:
                    continue
    except OSError:
        return None
    return out or None


def verify_candidates(index: dict[str, tuple[int, int]] | None, dry: bool = False) -> dict:
    """Move candidates by what the newsroom actually writes.

    The rule the design turns on: a form human outlets use is not a defect, whatever a model says, and a
    form nobody writes is the shape of a coinage. Thresholds come from the design: three occurrences in
    three outlets means attested; zero occurrences with a right form that is attested means a coinage.

    With no index, every candidate goes to `held` and says why. That is the honest state: unverified.
    """
    out = {"attested": [], "coinage": [], "held": [], "unverified": []}
    if index is None:
        out["unverified"] = [l.id for l in fold().values() if l.state == "candidate"]
        return out

    for lesson in sorted(fold().values(), key=lambda l: l.created):
        if lesson.state != "candidate":
            continue
        wrong_n, wrong_outlets = index.get(lesson.wrong.lower(), (0, 0))
        right_n, right_outlets = index.get(lesson.right.lower(), (0, 0))
        record = {"id": lesson.id, "wrong": lesson.wrong, "right": lesson.right,
                  "wrong_n": wrong_n, "wrong_outlets": wrong_outlets,
                  "right_n": right_n, "right_outlets": right_outlets}

        if wrong_n >= ATTEST_MIN_COUNT and wrong_outlets >= ATTEST_MIN_OUTLETS:
            # the newsroom writes this form: the lesson is wrong, not the text
            record["state"] = "rejected"
            out["attested"].append(record)
            if not dry:
                _append({"ev": "reject", "id": lesson.id, "by": "auto",
                        "reason": f"attested in human text: {wrong_n} articles, {wrong_outlets} outlets",
                        "attest": {"wrong_n": wrong_n, "right_n": right_n, "outlets": wrong_outlets,
                                   "index_tokens": sum(v[0] for v in index.values())}})
            continue

        if wrong_n == 0 and right_n >= ATTEST_MIN_COUNT and right_outlets >= ATTEST_MIN_OUTLETS:
            record["state"] = "shadow" if lesson.kind in ("nonword", "form") else lesson.state
            out["coinage"].append(record)
            if not dry and lesson.kind in ("nonword", "form"):
                _append({"ev": "attest", "id": lesson.id, "by": "auto",
                        "wrong_n": 0, "right_n": right_n, "outlets": right_outlets,
                        "index_tokens": sum(v[0] for v in index.values())})
                _append({"ev": "promote", "id": lesson.id, "by": "auto", "to": "shadow",
                        "why": f"not in {len(index)} indexed words; the correction is in {right_n} articles"})
            continue

        record["state"] = "held"
        record["why"] = ("the wrong form is rare but not absent" if wrong_n else
                         "the correction is not attested either")
        out["held"].append(record)
    return out


def tick(attest_path: str | None = None, dry: bool = False) -> dict:
    """The daily job's deterministic step: verify candidates, promote what is due, compile.

    Verification is deterministic and needs no model: it reads the word index veasy builds from D1 and
    applies the three thresholds. Promotion (shadow -> enforced) keeps its own conditions and the circuit
    breaker. With no index, nothing is promoted from `candidate` and the report says `unverified`.
    """
    index = load_attest(attest_path)
    out = {"verification": verify_candidates(index, dry=dry)}
    out.update(promote_due(dry=dry))
    if not dry:
        out["table"] = str(compile())
    return out


# The compiled table --------------------------------------------------------------------------------------------

def build_table() -> tuple[dict, dict[str, str]]:
    """The learned table and the words left out of it, with why. Only nonword/form single words are compiled;
    a word on an allow-list is dropped even if its lesson says enforced. A canon lesson stays in `error` until
    its line is in data/wrong_forms.json."""
    error: dict[str, str] = {}
    warn: dict[str, str] = {}
    ids: dict[str, str] = {}
    dropped: dict[str, str] = {}
    for lesson in fold().values():
        if lesson.state not in ("shadow", "enforced", "canon"):
            continue
        w = lesson.wrong
        if lesson.kind not in ENFORCEABLE:
            dropped[w] = "usage"
            continue
        if not is_single_word(w):
            dropped[w] = "multi_word"
            continue
        hit = allow_hit(w)
        if hit == "canon" and lesson.state == "canon":
            continue  # merged into wrong_forms.json: the canon rule fires, not this one
        if hit:
            dropped[w] = f"allow_list:{hit}"
            continue
        (warn if lesson.state == "shadow" else error)[w] = lesson.right
        ids[w] = lesson.id
    return {"error": error, "warn": warn, "ids": ids, "built": _ts()}, dropped


def compile() -> Path:
    """Write learned_forms.json atomically (tmp + rename) in the shape of wrong_forms.json."""
    table, _ = build_table()
    path = table_path()
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(table, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


# Reports -------------------------------------------------------------------------------------------------------

def stats(last: int = BREAKER_LAST, since: str | None = None, corpus_dir: str | None = None) -> dict:
    """Gate precision against human judgement, the funnel, stale candidates and the weekly number.

    Misses (an enforced lesson that should have fired on published text and did not) need a replay over the
    published corpus, which lives in veasy; that arrives in stage 3, so `corpus_dir` raises NotImplementedError."""
    if corpus_dir:
        raise NotImplementedError("misses need a replay over veasy's published corpus (stage 3)")
    now = _now()
    lessons = fold()
    cutoff = parse_ts(since) if since else None
    judged = [ev for ev in read_events() if ev.get("ev") == "judge" and ev.get("verdict") in ("ok", "wrong")]
    if cutoff:
        judged = [ev for ev in judged if parse_ts(ev["ts"]) >= cutoff]
    window = [ev for ev in judged if ev.get("firing_state") in ("enforced", "canon")][-max(1, last):]
    ok = sum(ev["verdict"] == "ok" for ev in window)
    by_state: dict[str, int] = {}
    by_kind: dict[str, int] = {}
    by_actor: dict[str, int] = {}
    for lesson in lessons.values():
        by_state[lesson.state] = by_state.get(lesson.state, 0) + 1
        by_kind[lesson.kind] = by_kind.get(lesson.kind, 0) + 1
        first = lesson.sources[0].get("actor", "") if lesson.sources else ""
        by_actor[first] = by_actor.get(first, 0) + 1
    stale = [lesson.id for lesson in lessons.values() if lesson.state in ("candidate", "held")
             and now - parse_ts(lesson.state_since) > timedelta(days=STALE_DAYS)]
    verdicts = judgements()
    fired = firings()
    unjudged = [f for f in fired if f.get("fid") not in verdicts]
    # Correct text the gate refused this week: firings of an enforced lesson that a teacher judged wrong.
    week = [ev for ev in judged if ev["verdict"] == "wrong" and ev.get("firing_state") in ("enforced", "canon")
            and now - parse_ts(ev["ts"]) <= timedelta(days=7)]
    enforced_n = by_state.get("enforced", 0) + by_state.get("canon", 0)
    caught = sum(1 for f in fired if f.get("state") in ("enforced", "canon") and not f.get("allowed")
                 and verdicts.get(f["fid"], {}).get("verdict") == "ok")
    return {
        "precision": {"ok": ok, "wrong": len(window) - ok, "n": len(window),
                      "value": ok / len(window) if window else None, "last": last},
        "unjudged_firings": len(unjudged),
        "firings": len(fired),
        "funnel": {"by_state": by_state, "by_kind": by_kind, "by_first_actor": by_actor},
        "never_promoted": stale,
        "contested": [lesson.id for lesson in lessons.values() if lesson.contested],
        "breaker": breaker(now),
        "weekly_wrong_refusals": len(week),
        "weekly_line": f"{enforced_n} lessons enforced, {caught} defects caught (judged ok)",
        "misses": "not built: needs the published corpus replay (stage 3)",
    }
