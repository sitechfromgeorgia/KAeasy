"""The teach CLI and the ka_teach tool."""
import json

import pytest
from kaeasy import lessons, lint, memory, teach

WORD, RIGHT = "მოქცევარი", "მამაკაცი"
QUOTE = "80 წლის მოქცევარი გარდაიცვალა."


def cli(capsys, *argv):
    code = teach.main([*argv, "--json"])
    return code, json.loads(capsys.readouterr().out)


def cli_text(capsys, *argv):
    code = teach.main(list(argv))
    return code, capsys.readouterr().out


def propose_args(by="edo", **kw):
    args = ["propose", kw.get("wrong", WORD), kw.get("right", RIGHT), "--kind", kw.get("kind", "nonword"),
            "--quote", kw.get("quote", QUOTE)]
    return args + (["--by", by] if by is not None else [])


@pytest.fixture
def louie():
    lessons.teachers_path().write_text(json.dumps({"edo": "owner", "louie": "reviewer"}), encoding="utf-8")
    return "louie"


def test_propose_and_show(capsys):
    code, out = cli(capsys, *propose_args(), "--why", "ასეთი სიტყვა არ არსებობს", "--ref", "24886")
    assert code == 0 and out["created"] and out["state"] == "candidate"
    code, text = cli_text(capsys, "show", WORD)
    assert code == 0 and out["id"] in text and "candidate" in text and "ref=24886" in text and "history:" in text
    code, shown = cli(capsys, "show", out["id"])
    assert shown["lesson"]["wrong"] == WORD and shown["fired"] == 0


def test_state_changes_need_a_teacher(capsys):
    with pytest.raises(SystemExit):  # argparse: --by is required
        teach.main(propose_args(by=None))
    capsys.readouterr()
    code, out = cli(capsys, *propose_args(by="corpus-review"))
    assert code == 1 and out["refused"] == "not_a_teacher"
    assert json.loads(teach.handle("propose", wrong=WORD, right=RIGHT, kind="nonword",
                                   quote=QUOTE))["refused"] == "no_actor"
    assert not lessons.log_path().exists() or lessons.log_path().read_text(encoding="utf-8") == ""


def test_teachers_json_decides(capsys):
    lessons.teachers_path().write_text(json.dumps({"louie": "reviewer"}), encoding="utf-8")
    assert cli(capsys, *propose_args(by="edo"))[1]["refused"] == "not_a_teacher"
    assert cli(capsys, *propose_args(by="Louie"))[1]["state"] == "candidate"


@pytest.mark.parametrize("action,args", [
    ("approve", ["--by", "bob"]),
    ("retire", ["--by", "bob", "--reason", "test"]),
    ("reopen", ["--by", "bob", "--reason", "x"]),
    ("graduate", ["--by", "bob"]),
])
def test_every_teacher_action_refuses_strangers(capsys, action, args):
    lid = cli(capsys, *propose_args())[1]["id"]
    code, out = cli(capsys, action, lid, *args)
    assert code == 1 and out["refused"] == "not_a_teacher"


def test_approve_retire_reopen(capsys):
    lid = cli(capsys, *propose_args())[1]["id"]
    assert cli(capsys, "approve", lid, "--by", "edo")[1]["state"] == "enforced"
    assert "learned_form" in [f.check for f in lint.check_text(QUOTE, strict=True)]
    assert cli(capsys, "reopen", lid, "--by", "edo", "--reason", "x")[1]["refused"] == "not_tombstoned"
    code, text = cli_text(capsys, "retire", lid, "--by", "edo", "--reason", "false_positive")
    assert code == 0 and "enforced -> retired" in text
    assert lint.check_text(QUOTE, strict=True) == []
    assert cli(capsys, *propose_args())[1]["note"] == "reopen needs a teacher"
    assert cli(capsys, "reopen", lid, "--by", "edo", "--reason", "owner says it is wrong")[1]["state"] == "candidate"


def test_retire_needs_a_known_reason(capsys):
    lid = cli(capsys, *propose_args())[1]["id"]
    assert json.loads(teach.handle("retire", id=lid, by="edo", reason="meh"))["refused"] == "bad_reason"


def test_judge_records_the_actor_and_refuses_own_ok(capsys, louie):
    lid = cli(capsys, *propose_args())[1]["id"]
    cli(capsys, "approve", lid, "--by", "edo")
    lessons.record_firings(lint.check_text(QUOTE), "writer", "s1", "article")
    fid = lessons.firings()[0]["fid"]
    assert cli(capsys, "judge", fid, "ok", "--by", "edo")[1]["refused"] == "own_proposal"
    code, text = cli_text(capsys, "judge", fid, "wrong", "--by", louie, "--note", "correct word here")
    assert code == 0 and "now shadow" in text
    ev = lessons.judgements()[fid]
    assert ev["actor"] == "louie" and ev["note"] == "correct word here"
    shown = cli(capsys, "show", lid)[1]
    assert shown["firings"][0]["verdict"] == "wrong"


def test_list_filters(capsys):
    cli(capsys, *propose_args())
    cli(capsys, *propose_args(wrong="მერები", right="ბრალდებულები", kind="usage",
                              quote="სასამართლომ მერები გაამართლა."))
    assert cli(capsys, "list")[1]["count"] == 2
    assert [r["wrong"] for r in cli(capsys, "list", "--state", "advisory")[1]["lessons"]] == ["მერები"]
    assert [r["wrong"] for r in cli(capsys, "list", "--kind", "nonword")[1]["lessons"]] == [WORD]
    assert cli(capsys, "list", "--since", "2999-01-01")[1]["count"] == 0
    assert "2 lesson(s)" in cli_text(capsys, "list")[1]


def test_stats_text(capsys):
    code, text = cli_text(capsys, "stats")
    assert code == 0 and "correct text refused this week: 0" in text and "breaker: closed" in text


def test_graduate_refuses_too_early(capsys):
    lid = cli(capsys, *propose_args())[1]["id"]
    cli(capsys, "approve", lid, "--by", "edo")
    assert cli(capsys, "graduate", lid, "--by", "edo")[1]["refused"] == "too_early"


def test_import_memory(capsys):
    memory.learn(WORD, RIGHT, reason="არ არსებობს", category="lexical", agent="corpus-review")
    memory.learn(WORD, RIGHT, category="lexical", agent="corpus-review")
    memory.learn("ნოემბერს", "ნოემბერში", category="style", agent="tt-shorts")  # an editor diff
    memory.learn("შუა დერეფანი", "შუა დირექტორი", category="lexical", agent="corpus-review")  # a phrase
    code, out = cli(capsys, "import-memory")
    assert code == 0 and not out["applied"]
    assert [(r["wrong"], r["result"]) for r in out["rows"]] == [(WORD, {"needs": ["quote", "kind"]})]
    args = ["import-memory", "--quote", f"{WORD}={QUOTE}", "--kind", f"{WORD}=nonword"]
    assert cli(capsys, *args)[1]["rows"][0]["result"] == {"would_propose": "nonword"}
    assert not lessons.fold()
    assert cli(capsys, *args, "--apply")[1]["refused"] == "no_actor"
    assert cli(capsys, *args, "--apply", "--by", "edo")[1]["rows"][0]["result"]["state"] == "candidate"
    lesson = lessons.get(WORD)
    assert lesson.sources[0]["actor"] == "corpus-review" and lesson.sources[0]["imported"]["by"] == "edo"
    assert cli(capsys, *args, "--apply", "--by", "edo")[1]["rows"][0]["result"] == {"exists": "candidate"}


def test_handle_never_raises():
    out = json.loads(teach.handle("nope"))
    assert out["ok"] is False and "unknown action" in out["error"]
    out = json.loads(teach.handle("stats", last="abc"))
    assert out["ok"] is False and "ka_teach failed" in out["error"]
    out = json.loads(teach.handle("show", id="არაფერი", task_id="ignored"))
    assert out["refused"] == "unknown_lesson" and out["text"].startswith("refused")


def test_tool_is_registered(kaeasy):
    tools = {}

    class Ctx:
        def register_skill(self, *a, **k):
            pass

        def register_tool(self, name, toolset, schema, handler, **kw):
            tools[name] = (schema, handler)

        def register_hook(self, *a, **k):
            pass

    kaeasy.register(Ctx())
    schema, handler = tools["ka_teach"]
    assert set(schema["parameters"]["properties"]["action"]["enum"]) == set(teach.ACTIONS)
    out = json.loads(handler({"action": "propose", "wrong": WORD, "right": RIGHT, "kind": "nonword",
                              "quote": QUOTE, "by": "edo"}))
    assert out["ok"] and out["state"] == "candidate" and "created" in out["text"]
    assert json.loads(handler({"action": "approve", "id": WORD, "by": "edo"}))["state"] == "enforced"
    lint_out = json.loads(tools["ka_lint"][1]({"text": QUOTE, "strict": True}))
    assert lint_out["findings"][0]["check"] == "learned_form" and lint_out["findings"][0]["lesson"] == out["id"]
    assert "error" in json.loads(handler(None))
