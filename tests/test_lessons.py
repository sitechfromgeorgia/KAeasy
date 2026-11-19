"""The lessons log: intake refusals, the state machine, the circuit breaker, the compiled table and the linter."""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from kaeasy import lessons, lint, memory

ROOT = Path(__file__).resolve().parent.parent
TZ = timezone(timedelta(hours=4))
T0 = datetime(2026, 11, 1, 12, 0, tzinfo=TZ)

# Made-up words: no allow-list can hold them.
WORD, RIGHT = "მოქცევარი", "მამაკაცი"
QUOTE = "80 წლის მოქცევარი გარდაიცვალა."
FAKE = "ბლაბლუკა"


class Clock:
    def __init__(self, now):
        self.now = now

    def __call__(self):
        return self.now

    def advance(self, **kw):
        self.now += timedelta(**kw)


@pytest.fixture
def clock(monkeypatch):
    c = Clock(T0)
    monkeypatch.setattr(lessons, "_now", c)
    return c


@pytest.fixture
def louie():
    """A second teacher, so a judgement is not the proposer's own."""
    lessons.teachers_path().write_text(json.dumps({"edo": "owner", "louie": "reviewer"}), encoding="utf-8")
    return "louie"


def propose(wrong=WORD, right=RIGHT, kind="nonword", quote=QUOTE, by="edo", **kw):
    return lessons.propose(wrong, right, kind, quote=quote, by=by, **kw)


def raw(*evs):
    for ev in evs:
        lessons._append(ev)


def checks(text, **kw):
    return [f.check for f in lint.check_text(text, **kw)]


# Intake refusals -----------------------------------------------------------------------------------------------

def test_refuses_no_actor():
    assert propose(by="")["refused"] == "no_actor"


def test_refuses_bad_kind():
    assert propose(kind="typo")["refused"] == "bad_kind"


def test_refuses_empty():
    assert propose(wrong="")["refused"] == "empty"
    assert propose(right="  ")["refused"] == "empty"


def test_refuses_same():
    assert propose(right=WORD)["refused"] == "same"
    assert propose(right=f"„{WORD}“")["refused"] == "same"


def test_refuses_multi_word():
    """A loose phrase is not a rule; a fixed collocation is.

    "შუა დერეფანი" is a real trade term, and a rule that fires on it is a false positive on every
    article. "მკვლელობა დაიწყო" is a legal formula that is never right. The difference is shape, not
    who asks: the review lane found the second class and could record none of it before 2026-11-19.
    """
    assert propose(wrong="შუა დერეფანი", quote="შუა დერეფანი იყო", right="შუა კარი")["refused"] == "multi_word"
    assert propose(wrong="ეს არის", quote="ეს არის ასე", right="ესაა")["refused"] == "multi_word"
    assert propose(wrong="ერთი ორი სამი ოთხი ხუთი", quote="ერთი ორი სამი ოთხი ხუთი იყო",
                   right="ხუთი")["refused"] == "multi_word"


def test_a_fixed_phrase_is_proposable_and_enforceable():
    # A phrase that is NOT already a canon rule, so this exercises the lesson path rather than the
    # wrong_forms.json short-circuit. "მკვლელობა დაიწყო" is canon since 2026-11-19 and returns
    # already_canon by design.
    out = propose(wrong="საქმე დაიწყო", right="საქმე აღიძრა", kind="nonword",
                  quote="პროკურატურამ საქმე დაიწყო გამოძიება", by="corpus-review", reader="agy")
    assert out["state"] == "candidate", out
    assert lessons._is_fixed_phrase("საქმე დაიწყო")
    assert lessons._is_fixed_phrase("მკვლელობა დაიწყო")


def test_teacher_may_record_a_usage_phrase():
    out = propose(wrong="მერია მან", right="მან", kind="usage", quote="ამის შემდეგ მერია მან თქვა")
    assert out["state"] == "advisory" and out["kind"] == "usage"


def test_refuses_latin():
    assert propose(wrong="tbilisi.today-ზე", quote="tbilisi.today-ზე იხილავთ")["refused"] == "latin"


def test_refuses_digits():
    assert propose(wrong="1-ელიი", quote="1-ელიი ადგილი")["refused"] == "digits"


def test_refuses_under_four_letters():
    assert propose(wrong="მას", right="პატიმარზე", quote="მას უთხრეს")["refused"] == "too_short"


def test_wrong_inside_right_forces_usage():
    out = propose(wrong=FAKE, right=FAKE + "ში", quote=f"ის {FAKE} წავიდა")
    assert out["kind"] == "usage" and out["state"] == "advisory" and "forced to usage" in out["note"]


def test_right_inside_wrong_forces_usage():
    out = propose(wrong=FAKE + "ში", right=FAKE, quote=f"ის {FAKE}ში წავიდა")
    assert out["kind"] == "usage" and out["state"] == "advisory"


def test_refuses_without_a_quote_holding_the_whole_word():
    assert propose(quote="")["refused"] == "no_quote"
    assert propose(quote="სხვა წინადადება")["refused"] == "no_quote"
    assert propose(quote=f"{WORD}ებმა თქვეს")["refused"] == "no_quote"  # only inside a longer word


def _only_in(name):
    lists = lessons.allow_lists()
    others = set().union(*(v for k, v in lists.items() if k != name))
    return min(w for w in lists[name] if len(w) >= 5 and w not in others and lessons.is_single_word(w))


@pytest.mark.parametrize("name", ["examples", "lexicon", "glossary", "wrong_forms"])
def test_refuses_allow_listed(name):
    w = _only_in(name)
    assert propose(wrong=w, right="ბლაბლა", quote=f"აქ {w} წერია")["refused"] == f"allow_list:{name}"


def test_refuses_what_wrong_forms_json_already_holds():
    canon = next(w for w in lint.WRONG_FORMS if lessons.is_single_word(w) and len(w) >= 4)
    assert propose(wrong=canon, quote=f"აქ {canon} წერია")["refused"] == "already_canon"


def test_tombstoned_reproposal_records_observe_and_does_not_reopen():
    lid = propose()["id"]
    assert lessons.retire(lid, "edo", "false_positive")["state"] == "retired"
    out = propose(by="corpus-review", reader="agy")
    assert out == {"id": lid, "state": "retired", "created": False, "kind": "nonword",
                   "note": "reopen needs a teacher"}
    lesson = lessons.get(WORD)
    assert lesson.state == "retired" and [e["ev"] for e in lesson.history] == ["propose", "retire", "observe"]
    assert lesson.observed_dead == 1 and not lesson.contested
    propose(by="corpus-review")
    propose(by="corpus-review")
    assert lessons.get(lid).contested and lessons.get(lid).state == "retired"


# Ids and the fold ----------------------------------------------------------------------------------------------

def test_id_comes_from_the_word():
    assert lessons.lesson_id(WORD) == lessons.lesson_id(f" „{WORD}“ ") == propose()["id"]
    assert re.fullmatch(r"L[0-9a-f]{8}", lessons.lesson_id(WORD))


def test_reproposal_lands_on_the_same_lesson():
    first = propose(by="corpus-review", reader="agy:gemini")
    again = propose(by="proofread", reader="deepseek", right="კაცი")
    assert again["id"] == first["id"] and again["created"] is False
    lesson = lessons.get(first["id"])
    assert lesson.readers == ["agy", "deepseek"] and lesson.observations == 2
    assert lesson.rights == {RIGHT: 1, "კაცი": 1}
    assert len(lessons.fold()) == 1
    assert sum(1 for line in lessons.log_path().read_text(encoding="utf-8").splitlines() if line) == 2


def test_log_is_append_only():
    lid = propose()["id"]
    before = lessons.log_path().read_text(encoding="utf-8")
    lessons.approve(lid, "edo")
    lessons.retire(lid, "edo", "test")
    assert lessons.log_path().read_text(encoding="utf-8").startswith(before)


def test_transitions(clock):
    lid = propose()["id"]
    assert lessons.get(lid).state == "candidate"
    raw({"id": lid, "ev": "verify", "result": "impossible"})
    assert lessons.get(lid).state == "held"
    raw({"id": lid, "ev": "promote", "to": "shadow"})
    assert lessons.get(lid).state == "shadow"
    raw({"id": lid, "ev": "promote", "to": "enforced"})
    assert lessons.get(lid).state == "enforced"
    raw({"id": lid, "ev": "demote", "to": "shadow"})
    assert lessons.get(lid).state == "shadow"
    raw({"id": lid, "ev": "graduate"})  # only from enforced: ignored
    lesson = lessons.get(lid)
    assert lesson.state == "shadow" and lesson.ignored[-1]["ev"] == "graduate"
    raw({"id": lid, "ev": "reject", "reason": "attested"})
    assert lessons.get(lid).state == "rejected"
    assert lessons.reopen(lid, "edo", "the index was wrong")["state"] == "candidate"


def test_approve_and_its_refusals():
    lid = propose()["id"]
    # An unknown seat cannot approve; corpus-review is a language-review seat since 2026-11-19.
    assert lessons.approve(lid, "stranger")["refused"] == "not_a_teacher"
    assert lessons.approve(lid, "edo") == {"id": lid, "state": "enforced", "from": "candidate"}
    assert lessons.get(lid).owner == "edo"
    assert lessons.approve(lid, "edo")["refused"] == "already_enforced"
    usage = propose(wrong=FAKE, right=FAKE + "ში", quote=f"ის {FAKE} წავიდა")["id"]
    assert lessons.approve(usage, "edo")["refused"] == "usage_is_advisory"


def test_approve_needs_a_reason_when_human_text_uses_the_form():
    lid = propose()["id"]
    raw({"id": lid, "ev": "attest", "wrong_n": 12, "right_n": 900, "outlets": 4})
    assert lessons.approve(lid, "edo")["refused"] == "attested"
    assert lessons.approve(lid, "edo", attested_ok="common misspelling")["state"] == "enforced"


# Judgements ----------------------------------------------------------------------------------------------------

def _fire(ref, text=QUOTE):
    found = lint.check_text(text)
    assert lessons.record_firings(found, "test", ref, "article") == 1
    return next(f for f in lessons.firings() if f["ref"] == ref)


def test_one_wrong_judgement_demotes_and_two_retire(louie):
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    assert "learned_form" in checks(QUOTE, strict=True)
    first = _fire("r1")
    assert first["state"] == "enforced"
    assert lessons.judge(first["fid"], "wrong", louie)["state"] == "shadow"
    assert lessons.get(lid).state == "shadow"
    assert "learned_form" not in checks(QUOTE, strict=True) and "learned_hint" in checks(QUOTE)
    second = _fire("r2")
    assert second["state"] == "shadow"
    assert lessons.judge(second["fid"], "wrong", louie)["state"] == "retired"
    lesson = lessons.get(lid)
    assert lesson.state == "retired" and lesson.reason == "false_positive"
    assert [e["actor"] for e in lesson.history if e["ev"] in ("demote", "retire")] == ["auto", "auto"]
    assert not [c for c in checks(QUOTE) if c.startswith("learned")]


def test_judge_refusals_and_actor(louie):
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    fid = _fire("r1")["fid"]
    assert lessons.judge("Fnope", "ok", louie)["refused"] == "unknown_firing"
    assert lessons.judge(fid, "maybe", louie)["refused"] == "bad_verdict"
    assert lessons.judge(fid, "ok", "corpus-review")["refused"] == "not_a_teacher"
    assert lessons.judge(fid, "ok", "edo")["refused"] == "own_proposal"
    assert lessons.judge(fid, "ok", louie)["verdict"] == "ok"
    assert lessons.judge(fid, "wrong", louie)["refused"] == "already_judged"
    ev = lessons.judgements()[fid]
    assert ev["actor"] == "louie" and ev["firing_state"] == "enforced"


def test_a_proposer_may_judge_their_own_lesson_wrong():
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    fid = _fire("r1")["fid"]
    assert lessons.judge(fid, "wrong", "edo")["state"] == "shadow"


# Circuit breaker -----------------------------------------------------------------------------------------------

def _shadow_lesson(clock):
    lid = propose()["id"]
    raw({"id": lid, "ev": "promote", "to": "shadow"})
    clock.advance(days=lessons.SHADOW_DAYS + 1)
    return lid


def _judged(n_ok, n_wrong, when):
    ts = when.isoformat(timespec="seconds")
    for i in range(n_wrong):
        raw({"ts": ts, "id": "L00000000", "ev": "judge", "fid": f"Fw{i}", "verdict": "wrong",
             "firing_state": "enforced", "actor": "louie"})
    for i in range(n_ok):
        raw({"ts": ts, "id": "L00000000", "ev": "judge", "fid": f"Fo{i}", "verdict": "ok",
             "firing_state": "enforced", "actor": "louie"})


def test_breaker_closed_promotes_shadow_to_enforced(clock):
    lid = _shadow_lesson(clock)
    out = lessons.promote_due()
    assert not out["breaker"]["open"] and out["promoted"] == [lid]
    assert lessons.get(lid).state == "enforced"
    assert json.loads(lessons.table_path().read_text(encoding="utf-8"))["error"] == {WORD: RIGHT}


def test_shadow_waits_its_days(clock):
    lid = propose()["id"]
    raw({"id": lid, "ev": "promote", "to": "shadow"})
    clock.advance(days=lessons.SHADOW_DAYS - 1)
    assert lessons.promote_due()["promoted"] == []


def test_breaker_opens_below_precision(clock):
    _judged(48, 2, T0 - timedelta(days=30))  # 0.96 over the last 50, all older than 7 days
    lid = _shadow_lesson(clock)
    out = lessons.promote_due()
    assert out["breaker"]["open"] and out["breaker"]["precision"] == pytest.approx(0.96)
    assert out["promoted"] == [] and lessons.get(lid).state == "shadow"


def test_breaker_at_exactly_098_stays_closed(clock):
    _judged(49, 1, T0 - timedelta(days=30))
    lid = _shadow_lesson(clock)
    assert lessons.promote_due()["promoted"] == [lid]


def test_breaker_looks_at_the_last_50_only(clock):
    _judged(0, 2, T0 - timedelta(days=60))
    _judged(50, 0, T0 - timedelta(days=30))
    lid = _shadow_lesson(clock)
    assert lessons.breaker()["precision"] == 1.0
    assert lessons.promote_due()["promoted"] == [lid]


def test_breaker_opens_on_any_wrong_judgement_in_7_days(clock):
    _judged(200, 0, T0 - timedelta(days=30))
    lid = _shadow_lesson(clock)
    _judged(0, 1, clock.now - timedelta(days=2))
    out = lessons.promote_due()
    assert out["breaker"]["open"] and "last 7 days" in out["breaker"]["reasons"][0]
    assert out["promoted"] == []
    clock.advance(days=6)  # the wrong judgement is now 8 days old
    assert lessons.promote_due()["promoted"] == [lid]


def test_open_breaker_does_not_stop_a_teacher(clock):
    _judged(0, 1, clock.now)
    lid = _shadow_lesson(clock)
    assert lessons.breaker()["open"]
    assert lessons.approve(lid, "edo")["state"] == "enforced"


def test_shadow_needs_every_outside_firing_judged_ok(clock, louie):
    lid = propose(ref="own")["id"]
    raw({"id": lid, "ev": "promote", "to": "shadow"})
    lessons.compile()
    _fire("own")  # its own evidence: needs no verdict
    other = _fire("other")
    clock.advance(days=lessons.SHADOW_DAYS + 1)
    assert lessons.promote_due()["promoted"] == []
    lessons.judge(other["fid"], "ok", louie)
    assert lessons.promote_due()["promoted"] == [lid]


def test_a_demoted_lesson_is_not_promoted_again_automatically(clock, louie, monkeypatch):
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    lessons.judge(_fire("r1")["fid"], "wrong", louie)
    clock.advance(days=30)
    assert lessons.promote_due()["promoted"] == []  # the breaker is open: precision 0 over 1 judged
    # Even with the breaker closed, the strike keeps it in shadow until a teacher approves it.
    monkeypatch.setattr(lessons, "breaker", lambda now=None: {"open": False, "reasons": []})
    out = lessons.promote_due()
    assert out["promoted"] == [] and "needs a teacher" in out["waiting"][lid]


def test_tick_without_an_index_verifies_nothing():
    """No index is not an empty index: an unverified candidate must stay a candidate, not become a rule."""
    lessons.propose("მოქცევარი", "მამაკაცი", "nonword", why="არ არსებობს",
                    quote="80 წლის მოქცევარი ადგილზე", by="edo")
    out = lessons.tick()
    assert out["verification"]["unverified"], "a candidate with no index must be reported unverified"
    assert not out["verification"]["coinage"], "nothing may be promoted without an index"
    states = {l.wrong: l.state for l in lessons.fold().values()}
    assert states["მოქცევარი"] == "candidate"


def test_tick_rejects_a_form_the_newsroom_writes(tmp_path):
    """Attestation is the guard against the რეფერანი class of false positive."""
    lessons.propose("დერეფანი", "დერეფანა", "nonword", why="ეჭვი",
                    quote="შუა დერეფანი გაფართოვდა", by="edo")
    idx = tmp_path / "words.tsv"
    idx.write_text("დერეფანი\t21\t21\nდერეფანა\t0\t0\n", encoding="utf-8")
    out = lessons.tick(attest_path=str(idx))
    assert out["verification"]["attested"], "a form in 21 articles must be rejected, not enforced"
    lesson = [l for l in lessons.fold().values() if l.wrong == "დერეფანი"][0]
    assert lesson.state == "rejected"


def test_tick_promotes_a_coinage_to_shadow(tmp_path):
    lessons.propose("მოქცევარი", "მამაკაცი", "nonword", why="არ არსებობს",
                    quote="80 წლის მოქცევარი ადგილზე", by="edo")
    idx = tmp_path / "words.tsv"
    idx.write_text("მოქცევარი\t0\t0\nმამაკაცი\t28\t28\n", encoding="utf-8")
    out = lessons.tick(attest_path=str(idx))
    assert out["verification"]["coinage"]
    lesson = [l for l in lessons.fold().values() if l.wrong == "მოქცევარი"][0]
    assert lesson.state == "shadow", "a coinage whose correction is attested goes to shadow"


# The compiled table and the linter -----------------------------------------------------------------------------

def _right_examples():
    """The ✅ texts tests/test_lint.py lints in strict mode, with their mode."""
    out = []
    for md in sorted(ROOT.glob("skills/*/examples/*.md")):
        mode = {"georgian-social": "social", "georgian-speech": "speech",
                "georgian-ui": "ui"}.get(md.parent.parent.name, "article")
        for line in md.read_text(encoding="utf-8").splitlines():
            m = re.search(r"✅\s*(.+?)(?:\s*\(|$)", line)
            if m and "/" not in m.group(1):
                out.append((re.sub(r"\s*\.\.\.$", "", m.group(1).strip()), mode))
    return out


def test_compiled_table_never_fires_on_a_right_example():
    examples = _right_examples()
    words = sorted({w for text, _ in examples for w in re.findall(r"[ა-ჰ]{4,}", text)})
    assert len(words) > 500
    picked = words[::max(1, len(words) // 60)]
    # Force them past every gate in the log, as a bad job or a hand edit could.
    for i, w in enumerate(picked + [WORD]):
        lid = lessons.lesson_id(w)
        raw({"id": lid, "ev": "propose", "wrong": w, "right": "ბლაბლა", "kind": "nonword", "actor": "x"},
            {"id": lid, "ev": "approve" if i % 2 else "promote", "to": "shadow", "actor": "edo"})
    lessons.compile()
    table = json.loads(lessons.table_path().read_text(encoding="utf-8"))
    assert set(table["error"]) | set(table["warn"]) <= {WORD}
    _, dropped = lessons.build_table()
    assert set(picked) <= set(dropped)
    for text, mode in examples:
        assert not [c for c in checks(text, mode=mode) if c.startswith("learned")], text


def test_empty_ledger_changes_nothing():
    samples = [(t, m) for t, m in _right_examples()][:400] + [
        (QUOTE, "article"), ("Microsoftმა ახალი მოდელი წარადგინა.", "article"), ("5 სტატიები.", "speech")]
    before = [[f.as_dict() for f in lint.check_text(t, m)] for t, m in samples]
    assert not lessons.table_path().exists()
    lessons.compile()  # an empty ledger compiles to an empty table
    assert json.loads(lessons.table_path().read_text(encoding="utf-8"))["error"] == {}
    after = [[f.as_dict() for f in lint.check_text(t, m)] for t, m in samples]
    assert after == before
    assert all(type(f) is lint.Finding for t, m in samples for f in lint.check_text(t, m))
    assert lint.check_text(QUOTE, "article") == lint.check_text(QUOTE, "article", None, False)


def test_learned_form_is_strict_and_learned_hint_is_not():
    assert "learned_form" in lint.STRICT and "learned_hint" not in lint.STRICT


def test_linter_reloads_the_table_without_a_restart():
    lid = propose()["id"]
    assert "learned_form" not in checks(QUOTE)
    lessons.approve(lid, "edo")
    found = [f for f in lint.check_text(QUOTE, strict=True) if f.check == "learned_form"]
    assert found and found[0].lesson == lid and found[0].severity == "error"
    assert found[0].as_dict()["lesson"] == lid
    lessons.retire(lid, "edo", "test")
    assert "learned_form" not in checks(QUOTE)


def test_whole_words_only_and_quotes_skipped():
    lessons.approve(propose()["id"], "edo")
    assert "learned_form" not in checks(f"{WORD}ებმა თქვეს.")
    assert "learned_form" not in checks(f"მან თქვა: „{WORD}“.")
    assert "learned_form" not in checks(f"<a href='/{WORD}'>ბმული</a>")


def test_allow_turns_an_error_into_a_hint():
    lessons.approve(propose()["id"], "edo")
    for allow in (f"წყაროში წერია: {WORD} გარდაიცვალა.", [WORD], ["სხვა ტექსტი", f"აქ {WORD} არის"]):
        found = lint.check_text(QUOTE, allow=allow)
        assert [(f.check, f.severity) for f in found if f.check.startswith("learned")] == [("learned_hint", "warn")]
        assert "learned_form" not in checks(QUOTE, strict=True, allow=allow)
    assert "learned_form" in checks(QUOTE, allow=f"{WORD}ებმა")  # not a whole word: no allowance
    assert "learned_form" in checks(QUOTE, allow=None)


def test_shadow_fires_as_a_hint_only():
    lid = propose()["id"]
    raw({"id": lid, "ev": "promote", "to": "shadow"})
    lessons.compile()
    assert [(f.check, f.severity) for f in lint.check_text(QUOTE)] == [("learned_hint", "warn")]
    assert lint.check_text(QUOTE, strict=True) == []


def test_hand_edited_table_cannot_add_a_phrase():
    lessons.table_path().write_text(json.dumps({"error": {"შუა დერეფანი": "x", "ab": "c"}, "warn": {},
                                                "ids": {}}), encoding="utf-8")
    assert checks("შუა დერეფანი ab", strict=True) == []


def test_canon_stays_enforced_until_wrong_forms_has_it(clock):
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    assert lessons.graduate(lid, "edo")["refused"] == "too_early"
    clock.advance(days=lessons.GRADUATE_DAYS + 1)
    out = lessons.graduate(lid, "edo")
    assert out["state"] == "canon" and out["wrong_forms_line"] == f'"{WORD}": "{RIGHT}",'
    assert "learned_form" in checks(QUOTE, strict=True)


# Usage never blocks --------------------------------------------------------------------------------------------

USAGE = "მერები"
USAGE_QUOTE = "სასამართლომ მერები გაამართლა."


@pytest.mark.parametrize("events", [
    [],
    [{"ev": "promote", "to": "shadow"}],
    [{"ev": "promote", "to": "shadow"}, {"ev": "promote", "to": "enforced"}],
    [{"ev": "approve"}],
    [{"ev": "approve"}, {"ev": "graduate"}],
    [{"ev": "verify", "result": "impossible"}, {"ev": "approve"}],
    [{"ev": "retire", "reason": "test"}, {"ev": "reopen", "reason": "x"}, {"ev": "approve"}],
    [{"ev": "reject", "reason": "test"}],
])
def test_usage_never_produces_an_error(events):
    lid = lessons.propose(USAGE, "ბრალდებულები", "usage", quote=USAGE_QUOTE, by="edo")["id"]
    raw(*({"id": lid, "actor": "edo", **ev} for ev in events))
    lesson = lessons.get(lid)
    assert lesson.kind == "usage" and lesson.state in ("advisory", "retired", "rejected")
    lessons.compile()
    table = json.loads(lessons.table_path().read_text(encoding="utf-8"))
    assert USAGE not in table["error"] and USAGE not in table["warn"]
    for strict in (False, True):
        assert not [f for f in lint.check_text(USAGE_QUOTE, strict=strict) if f.severity == "error"
                    and f.check.startswith("learned")]


def test_a_second_propose_event_cannot_change_the_kind():
    lid = lessons.propose(USAGE, "ბრალდებულები", "usage", quote=USAGE_QUOTE, by="edo")["id"]
    raw({"id": lid, "ev": "propose", "wrong": USAGE, "right": "x", "kind": "nonword", "actor": "x"})
    assert lessons.get(lid).kind == "usage"  # a second propose event cannot change the kind


# Firings -------------------------------------------------------------------------------------------------------

def test_record_firings_deduplicates_retries():
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    found = lint.check_text(QUOTE)
    assert lessons.record_firings(found, "writer", "s1", "article") == 1
    assert lessons.record_firings(found, "writer", "s1", "article") == 0  # a retry with the same sentence
    assert lessons.record_firings([f.as_dict() for f in found], "writer", "s1", "article") == 0
    assert lessons.record_firings(found, "writer", "s2", "article") == 1
    assert lessons.record_firings(lint.check_text("ახალი " + QUOTE), "writer", "s1", "article") == 1
    rows = lessons.firings(lid)
    assert len(rows) == 3 and all(r["id"] == lid and r["agent"] == "writer" for r in rows)
    assert (lessons.firings_dir() / f"{lessons._now():%Y-%m}.jsonl").exists()
    assert lessons.record_firings(lint.check_text("Microsoftმა"), "writer", "s3", "article") == 0


def test_allowed_firing_is_marked():
    lessons.approve(propose()["id"], "edo")
    lessons.record_firings(lint.check_text(QUOTE, allow=[WORD]), "writer", "s1", "article")
    assert lessons.firings()[0]["allowed"] is True


# Memory --------------------------------------------------------------------------------------------------------

def test_memory_top_leaves_out_tombstoned_words():
    memory.learn(WORD, RIGHT, category="lexical", agent="corpus-review")
    memory.learn("კომპანია გამოაცხადა", "კომპანიამ გამოაცხადა", category="case")
    assert {r["wrong"] for r in memory.top(10)} == {WORD, "კომპანია გამოაცხადა"}
    lid = propose()["id"]
    assert {r["wrong"] for r in memory.top(10)} == {WORD, "კომპანია გამოაცხადა"}  # a live lesson stays
    lessons.retire(lid, "edo", "false_positive")
    assert [r["wrong"] for r in memory.top(10)] == ["კომპანია გამოაცხადა"]
    assert [r["wrong"] for r in memory.top(10, "lexical")] == []


def test_memory_top_leaves_out_context_edits():
    """A lane that diffs an editor pass must not look like a language authority.

    Measured 2026-11-19: the shared memory held 442 tt-shorts rows such as "შემდეგ -> შედეგად" and
    "ითვალისწინებს -> ითვალისწინებენ" against 4 real lessons, so ka_mistakes told every writer that
    correct Georgian was wrong. They stay in the file; they stop reaching prompts.
    """
    memory.learn("შემდეგ", "შედეგად", category="style", agent="tt-shorts")
    memory.learn(WORD, RIGHT, category="lexical", agent="corpus-review")
    assert [r["wrong"] for r in memory.top(10)] == [WORD]
    assert {r["wrong"] for r in memory.top(10, exclude_agents=())} == {WORD, "შემდეგ"}
    assert [r["wrong"] for r in memory.top(10, agents=("tt-shorts",))] == ["შემდეგ"]


def test_stats_shape(clock, louie):
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    lessons.judge(_fire("r1")["fid"], "ok", louie)
    _fire("r2")
    s = lessons.stats()
    assert s["precision"] == {"ok": 1, "wrong": 0, "n": 1, "value": 1.0, "last": 50}
    assert s["unjudged_firings"] == 1 and s["firings"] == 2
    assert s["funnel"]["by_state"] == {"enforced": 1} and s["weekly_wrong_refusals"] == 0
    assert s["weekly_line"] == "1 lessons enforced, 1 defects caught (judged ok)"


# Loaded by path, as veasy's tt_shorts/kaeasy.py loads lint.py and memory.py ------------------------------------

def _by_path(name, monkeypatch):
    """Exactly how veasy does it: no package, registered in sys.modules under a flat name."""
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(f"kaeasy_{name}", ROOT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, f"kaeasy_{name}", mod)
    spec.loader.exec_module(mod)
    return mod


def test_standalone_lint_reads_the_compiled_table(monkeypatch):
    standalone = _by_path("lint", monkeypatch)
    assert standalone.check_text(QUOTE, "article") == []
    lid = propose()["id"]
    lessons.approve(lid, "edo")
    found = standalone.check_text(QUOTE, strict=True)
    assert [(f.check, f.lesson) for f in found] == [("learned_form", lid)]


def test_standalone_memory_leaves_out_tombstoned_words(monkeypatch):
    memory.learn(WORD, RIGHT, category="lexical", agent="corpus-review")
    standalone = _by_path("memory", monkeypatch)
    lessons.retire(propose()["id"], "edo", "false_positive")
    assert standalone.top(10) == []


def test_memory_scan_agrees_with_the_fold(clock, louie):
    a = propose()["id"]
    b = propose(wrong=FAKE, right="ბლაბლა", quote=f"ის {FAKE} წავიდა")["id"]
    c = lessons.propose("მერები", "ბრალდებულები", "usage", quote="სასამართლომ მერები გაამართლა.", by="edo")["id"]
    d = propose(wrong="ფუფლუკი", right="ბლაბლა", quote="ის ფუფლუკი წავიდა")["id"]
    steps = [
        lambda: lessons.approve(a, "edo"),
        lambda: lessons.retire(b, "edo", "test"),
        lambda: lessons.reject(c, "corpus-review", "attested"),
        lambda: lessons.reopen(b, "edo", "x"),
        lambda: lessons.judge(_fire("r1")["fid"], "wrong", louie),
        lambda: lessons.judge(_fire("r2", f"სხვა: {QUOTE}")["fid"], "wrong", louie),  # retires a
        lambda: propose(),  # an observation on the tombstone
        lambda: lessons.reject(a, "corpus-review", "x"),  # refused: already retired
        lambda: lessons.retire(d, "edo", "duplicate"),
        lambda: lessons.reopen(d, "edo", "y"),
        lambda: lessons.retire(d, "edo", "context"),
    ]
    for step in steps:
        step()
        assert memory.tombstoned_words() == lessons.tombstoned()
    assert lessons.tombstoned() == {WORD, "მერები", "ფუფლუკი"}
