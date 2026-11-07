"""KAeasy Hermes plugin: Georgian writing skills, a zero-cost linter and a shared mistakes memory.

Registers every skills/<name>/SKILL.md as `kaeasy:<name>`, five tools (ka_lint, ka_fix, ka_speech, ka_learn,
ka_mistakes) and a
pre_llm_call hook that tells the agent, once per session, that the skills exist (plugin skills are not listed in
<available_skills>, so without the hint nobody loads them). No LLM calls, no network, no secrets.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from . import fix, lint, memory, speech

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent / "skills"

HINT = (
    "[kaeasy] If this turn involves Georgian (ქართული) text that a person will read (article, headline, post, "
    "video script, UI string, message to Edo), first load skill_view('kaeasy:georgian-writing') and follow it. "
    "Before publishing, run ka_lint on the final text and fix every error (ka_fix repairs the mechanical ones). "
    "For text a TTS voice will read, convert it with ka_speech instead of writing numbers in words yourself."
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
            "fields": {"type": "object", "additionalProperties": {"type": "string", "enum": list(lint.MODES)},
                       "description": "When text is JSON (a video script): mode per key, e.g. "
                                      "{\"say\": \"speech\", \"*\": \"social\"}. Each string field is checked "
                                      "in its own mode; keys mapped to \"skip\" are ignored."},
        },
        "required": ["text"],
    },
}

KA_FIX = {
    "name": "ka_fix",
    "description": "Auto-fix mechanical Georgian errors: „…“ quotes, brand hyphens (Metaის → Meta-ის), "
                   "transliterated brands (მაიკროსოფტმა → Microsoft-მა), decimal comma, dashes, spacing. Never "
                   "touches grammar. Run, then re-check with ka_lint.",
    "parameters": {
        "type": "object",
        "properties": {"text": {"type": "string", "description": "Georgian text (plain, Markdown or HTML)."}},
        "required": ["text"],
    },
}

KA_SPEECH = {
    "name": "ka_speech",
    "description": "Turn written Georgian into speech text for TTS: numbers into words with the right case "
                   "(36%-ით → ოცდათექვსმეტი პროცენტით, 2012 წელს → ორი ათას თორმეტ წელს), Latin brands into "
                   "Georgian letters (Microsoft-მა → მაიკროსოფტმა), acronyms spelled (GPU → ჯი პი იუ). "
                   "Deterministic, free.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Written Georgian narration."},
            "say": {"type": "object", "additionalProperties": {"type": "string"},
                    "description": "Spoken forms for names the lexicon does not know, e.g. {\"ARTEX\": \"არტექსი\"}."},
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
        strict = bool(args.get("strict"))
        if args.get("fields"):
            findings = lint.check_json(json.loads(text), args["fields"], strict=strict)
        else:
            findings = lint.check_text(text, mode=args.get("mode") or "article", title=args.get("title"),
                                       strict=strict)
        return json.dumps({"clean": not findings, "summary": lint.summary(findings),
                           "findings": [f.as_dict() for f in findings[:100]]}, ensure_ascii=False)
    except Exception as e:  # handlers must never raise
        return json.dumps({"error": f"ka_lint failed: {e}"}, ensure_ascii=False)


def _ka_fix(args: dict, **kwargs) -> str:
    try:
        fixed, changes = fix.fix_text(args.get("text") or "")
        left = lint.check_text(fixed, strict=True)
        return json.dumps({"text": fixed, "changes": changes, "remaining": [f.as_dict() for f in left[:50]]},
                          ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"ka_fix failed: {e}"}, ensure_ascii=False)


def _ka_speech(args: dict, **kwargs) -> str:
    try:
        text, say = args.get("text") or "", args.get("say") or {}
        spoken = speech.speech(text, say)
        left = lint.check_text(spoken, mode="speech", strict=True)
        return json.dumps({"speech": spoken, "unspoken": speech.unspoken(text, say),
                           "remaining": [f.as_dict() for f in left[:50]]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"ka_speech failed: {e}"}, ensure_ascii=False)


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
    ctx.register_tool(name="ka_fix", toolset="kaeasy", schema=KA_FIX, handler=_ka_fix)
    ctx.register_tool(name="ka_speech", toolset="kaeasy", schema=KA_SPEECH, handler=_ka_speech)
    ctx.register_tool(name="ka_learn", toolset="kaeasy", schema=KA_LEARN, handler=_ka_learn)
    ctx.register_tool(name="ka_mistakes", toolset="kaeasy", schema=KA_MISTAKES, handler=_ka_mistakes)
    ctx.register_hook("pre_llm_call", _hint)
