import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


class FakeCtx:
    def __init__(self):
        self.skills, self.tools, self.hooks = {}, {}, {}

    def register_skill(self, name, path, description="", frontmatter=None):
        assert Path(path).exists()
        self.skills[name] = Path(path)

    def register_tool(self, name, toolset, schema, handler, **kw):
        self.tools[name] = (schema, handler)

    def register_hook(self, name, cb):
        self.hooks[name] = cb


def test_register(kaeasy):
    ctx = FakeCtx()
    kaeasy.register(ctx)
    manifest = yaml.safe_load((ROOT / "plugin.yaml").read_text(encoding="utf-8"))
    assert set(ctx.tools) == set(manifest["provides_tools"])
    assert set(ctx.hooks) == set(manifest["provides_hooks"])
    assert "georgian-writing" in ctx.skills and len(ctx.skills) >= 8


def test_skill_frontmatter_and_links():
    for skill_md in ROOT.glob("skills/*/SKILL.md"):
        text = skill_md.read_text(encoding="utf-8")
        fm = yaml.safe_load(text.split("---")[1])
        assert fm["name"] == skill_md.parent.name
        assert len(fm["description"]) > 40, skill_md
        assert len(text) < 12000, f"{skill_md} too large for a cheap model's context"
        for ref in re.findall(r"`((?:references|examples)/[^`]+\.md)`", text):
            assert (skill_md.parent / ref).exists(), f"{skill_md.parent.name}: missing {ref}"
        for sib in re.findall(r"kaeasy:([a-z-]+)", text):
            assert (ROOT / "skills" / sib / "SKILL.md").exists(), f"unknown sibling {sib}"


def test_tools_roundtrip(kaeasy):
    ctx = FakeCtx()
    kaeasy.register(ctx)
    lint_out = json.loads(ctx.tools["ka_lint"][1]({"text": "Microsoftმა", "strict": True}))
    assert lint_out["clean"] is False
    learn = ctx.tools["ka_learn"][1]
    for _ in range(2):
        assert "saved" in json.loads(learn({"wrong": "კომპანია გამოაცხადა", "right": "კომპანიამ გამოაცხადა",
                                            "category": "case", "reason": "ერგატივი"}))
    learn({"wrong": "5 სტატიები", "right": "5 სტატია", "category": "agreement"})
    top = json.loads(ctx.tools["ka_mistakes"][1]({"limit": 5}))
    assert top["items"][0]["count"] == 2 and "კომპანიამ" in top["markdown"]
    assert "error" in json.loads(learn({"wrong": "a", "right": "a", "category": "case"}))


def test_learn_masks_secrets(kaeasy):
    row = kaeasy.memory.learn("მომწერე edo@example.com-ზე", "მომწერე ელფოსტაზე", category="other")
    assert "@" not in row["wrong"]


def test_hint_only_on_first_turn(kaeasy, monkeypatch):
    assert kaeasy._hint(is_first_turn=True)["context"].startswith("[kaeasy]")
    assert kaeasy._hint(is_first_turn=False) is None
    monkeypatch.setenv("KAEASY_HINT", "0")
    assert kaeasy._hint(is_first_turn=True) is None
