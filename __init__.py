"""Kaeasy Hermes plugin: Georgian writing skills, a zero-cost linter and a shared mistakes memory.

Registers every skills/<name>/SKILL.md as `kaeasy:<name>`, three tools (ka_lint, ka_learn, ka_mistakes) and a
pre_llm_call hook that tells the agent, once per session, that the skills exist (plugin skills are not listed in
<available_skills>, so without the hint nobody loads them). No LLM calls, no network, no secrets.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from . import lint, memory

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent / "skills"

HINT = (
    "[kaeasy] If this turn involves Georgian (ქართული) text that a person will read (article, headline, post, "
    "video script, UI string, message to Edo), first load skill_view('kaeasy:georgian-writing') and follow it. "
    "Before publishing, run ka_lint on the final text and fix every error."
)

KA_LINT = {
    "name": "ka_lint",
    "description": "Check Georgian text for mechanical errors (brand spelling and hyphens, numerals, quotes, "
                   "dashes, calques, AI filler). Free, deterministic. Run on final text before publishing.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Georgian text to check (plain, Markdown or HTML)."},
            "mode": {"type": "string", "enum": list(lint.MODES), "default": "article",
                     "description": "speech = text for TTS (Georgian letters only, numbers in words)."},
            "title": {"type": "string", "description": "Headline, checked separately (optional)."},
            "strict": {"type": "boolean", "default": False,
                       "description": "Only near-zero false-positive rules (use as a publish gate)."},
        },
        "required": ["text"],
    },
}

KA_LEARN = {
    "name": "ka_learn",
    "description": "Record a Georgian correction (a human or a review fixed your text) so every agent avoids "
                   "it next time. One short phrase per call, not whole articles.",
    "parameters": {
        "type": "object",
        "properties": {
            "wrong": {"type": "string", "description": "The wrong phrase, as short as possible."},
            "right": {"type": "string", "description": "The corrected phrase."},
            "reason": {"type": "string", "description": "One-line reason in Georgian."},
            "category": {"type": "string", "enum": list(memory.CATEGORIES)},
            "agent": {"type": "string", "description": "Your profile name."},
        },
        "required": ["wrong", "right", "category"],
    },
}

KA_MISTAKES = {
    "name": "ka_mistakes",
    "description": "List the fleet's most frequent Georgian mistakes (wrong → right). Read before writing.",
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 20},
            "category": {"type": "string", "enum": list(memory.CATEGORIES)},
        },
    },
}


def _ka_lint(args: dict, **kwargs) -> str:
    try:
        text = args.get("text") or ""
        findings = lint.check_text(text, mode=args.get("mode") or "article", title=args.get("title"),
                                   strict=bool(args.get("strict")))
        return json.dumps({"clean": not findings, "summary": lint.summary(findings),
                           "findings": [f.as_dict() for f in findings[:100]]}, ensure_ascii=False)
    except Exception as e:  # handlers must never raise
        return json.dumps({"error": f"ka_lint failed: {e}"}, ensure_ascii=False)


def _ka_learn(args: dict, **kwargs) -> str:
    try:
        row = memory.learn(args.get("wrong", ""), args.get("right", ""), args.get("reason", ""),
                           args.get("category", "other"), args.get("agent", ""))
        return json.dumps({"saved": row}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"ka_learn failed: {e}"}, ensure_ascii=False)


def _ka_mistakes(args: dict, **kwargs) -> str:
    try:
        rows = memory.top(int(args.get("limit") or 20), args.get("category"))
        return json.dumps({"markdown": memory.as_markdown(rows), "items": rows}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"ka_mistakes failed: {e}"}, ensure_ascii=False)


def _hint(is_first_turn: bool = False, **kwargs):
    if not is_first_turn or os.environ.get("KAEASY_HINT", "1") == "0":
        return None
    return {"context": HINT}


def register(ctx):
    for child in sorted(SKILLS_DIR.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)
    ctx.register_tool(name="ka_lint", toolset="kaeasy", schema=KA_LINT, handler=_ka_lint)
    ctx.register_tool(name="ka_learn", toolset="kaeasy", schema=KA_LEARN, handler=_ka_learn)
    ctx.register_tool(name="ka_mistakes", toolset="kaeasy", schema=KA_MISTAKES, handler=_ka_mistakes)
    ctx.register_hook("pre_llm_call", _hint)
