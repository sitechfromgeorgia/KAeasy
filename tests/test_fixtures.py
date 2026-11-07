"""Tests for adversarial text fixtures and speech golden dataset.

Proves that ka_lint, ka_fix, and ka_speech never break real text.
Run after v0.3 (when ka_speech and ka_fix exist).

If a tool fails a case, the tool is NOT changed; instead, the failure is listed
in docs/TOOL-BUGS.md (input, expected, actual) so Claude can fix the code.
"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

try:
    from kaeasy import lint
except ImportError:
    repo_root = Path(__file__).resolve().parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    import lint

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
ADVERSARIAL_DIR = FIXTURES_DIR / "adversarial"
SPEECH_GOLDEN_PATH = FIXTURES_DIR / "speech_golden.jsonl"
BUGS_DOC_PATH = Path(__file__).resolve().parent.parent / "docs" / "TOOL-BUGS.md"

# Known tool bugs (docs/TOOL-BUGS.md), marked xfail until fixed. All six found in P9 are fixed in v0.4.
KNOWN_LINT_BUGS: dict[str, str] = {}


def _discover_ka_fix():
    """Detect if ka_fix tool/function is implemented in kaeasy."""
    for mod_name in ("kaeasy.fix", "fix"):
        try:
            mod = importlib.import_module(mod_name)
            for attr in ("fix_text", "ka_fix", "fix"):
                fn = getattr(mod, attr, None)
                if callable(fn):
                    return fn
        except ImportError:
            pass
    try:
        import kaeasy
        fn = getattr(kaeasy, "ka_fix", None) or getattr(kaeasy, "_ka_fix", None)
        if callable(fn):
            return fn
    except (ImportError, AttributeError):
        pass
    return None


def _discover_ka_speech():
    """Detect if ka_speech tool/function is implemented in kaeasy."""
    for mod_name in ("kaeasy.speech", "speech"):
        try:
            mod = importlib.import_module(mod_name)
            for attr in ("to_speech", "speech_text", "ka_speech", "speech"):
                fn = getattr(mod, attr, None)
                if callable(fn):
                    return fn
        except ImportError:
            pass
    try:
        import kaeasy
        fn = getattr(kaeasy, "ka_speech", None) or getattr(kaeasy, "_ka_speech", None)
        if callable(fn):
            return fn
    except (ImportError, AttributeError):
        pass
    return None


KA_FIX_FN = _discover_ka_fix()
KA_SPEECH_FN = _discover_ka_speech()


def load_adversarial_fixtures():
    """Load all adversarial test cases and their expected JSON files."""
    fixtures = []
    if not ADVERSARIAL_DIR.exists():
        return fixtures
    for exp_path in sorted(ADVERSARIAL_DIR.glob("*.expected.json")):
        name = exp_path.name.replace(".expected.json", "")
        txt_path = ADVERSARIAL_DIR / f"{name}.txt"
        if not txt_path.exists():
            continue
        text = txt_path.read_text(encoding="utf-8")
        expected = json.loads(exp_path.read_text(encoding="utf-8"))
        fixtures.append((name, text, expected))
    return fixtures


def load_speech_golden():
    """Load golden speech dataset lines."""
    if not SPEECH_GOLDEN_PATH.exists():
        return []
    cases = []
    with open(SPEECH_GOLDEN_PATH, encoding="utf-8") as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if line:
                cases.append((idx, json.loads(line)))
    return cases


ADVERSARIAL_FIXTURES = load_adversarial_fixtures()
SPEECH_CASES = load_speech_golden()


def test_adversarial_fixtures_count():
    """Verify that all 25 adversarial fixtures are present."""
    assert len(ADVERSARIAL_FIXTURES) >= 25, f"Expected at least 25 adversarial fixtures, got {len(ADVERSARIAL_FIXTURES)}"


def test_speech_golden_count():
    """Verify that speech golden dataset contains at least 300 lines."""
    assert len(SPEECH_CASES) >= 300, f"Expected at least 300 lines in speech_golden.jsonl, got {len(SPEECH_CASES)}"


@pytest.mark.parametrize("name,text,expected", ADVERSARIAL_FIXTURES, ids=[x[0] for x in ADVERSARIAL_FIXTURES])
def test_adversarial_lint(name, text, expected):
    """Run ka_lint strict check on adversarial real text.

    If a tool fails a case, it is logged in docs/TOOL-BUGS.md and marked xfail here.
    """
    findings = lint.check_text(text, strict=True)
    actual_findings = [f.as_dict() for f in findings]
    expected_findings = expected.get("findings", [])

    if name in KNOWN_LINT_BUGS and actual_findings != expected_findings:
        pytest.xfail(f"Known tool bug in ka_lint ({name}): {KNOWN_LINT_BUGS[name]}")

    assert actual_findings == expected_findings, (
        f"ka_lint strict false positive on '{name}':\n"
        f"Expected: {expected_findings}\n"
        f"Actual: {actual_findings}"
    )


@pytest.mark.parametrize("name,text,expected", ADVERSARIAL_FIXTURES, ids=[x[0] for x in ADVERSARIAL_FIXTURES])
def test_adversarial_fix(name, text, expected):
    """Run ka_fix on adversarial real text to ensure text is never broken."""
    if KA_FIX_FN is None:
        pytest.skip("ka_fix is not yet implemented (scheduled for v0.3)")

    expected_fixed = expected.get("fixed", text)
    actual_fixed = KA_FIX_FN(text)
    if isinstance(actual_fixed, tuple):
        actual_fixed = actual_fixed[0]
    elif isinstance(actual_fixed, dict):
        actual_fixed = actual_fixed.get("fixed", actual_fixed.get("text", text))

    if name in KNOWN_LINT_BUGS:
        pytest.xfail(f"Known tool bug in ka_fix ({name}): {KNOWN_LINT_BUGS[name]}")

    assert actual_fixed == expected_fixed, (
        f"ka_fix broke adversarial text in '{name}':\n"
        f"Expected: {expected_fixed}\n"
        f"Actual: {actual_fixed}"
    )


@pytest.mark.parametrize("idx,case", SPEECH_CASES, ids=[f"speech_{x[0]:03d}" for x in SPEECH_CASES])
def test_speech_golden(idx, case):
    """ka_speech on every golden pair."""
    if KA_SPEECH_FN is None:
        pytest.skip("ka_speech is not yet implemented (scheduled for v0.3)")

    written = case["written"]
    expected_spoken = case["spoken"]
    actual_spoken = KA_SPEECH_FN(written)
    if isinstance(actual_spoken, dict):
        actual_spoken = actual_spoken.get("spoken", actual_spoken.get("text", ""))

    assert actual_spoken == expected_spoken, (
        f"ka_speech mismatch on item {idx} ('{written}'):\n"
        f"Expected: {expected_spoken}\n"
        f"Actual: {actual_spoken}"
    )


def test_speech_golden_targets_lint_clean():
    """Verify that every target spoken sentence in speech_golden passes speech mode lint."""
    dirty = []
    for idx, case in SPEECH_CASES:
        spoken = case["spoken"]
        findings = lint.check_text(spoken, mode="speech", strict=True)
        if findings:
            dirty.append((idx, case, [f.as_dict() for f in findings]))

    assert not dirty, f"Found {len(dirty)} dirty speech golden targets: {dirty[:5]}"


def run_standalone():
    """Standalone diagnostic runner for adversarial and speech fixtures."""
    print("=" * 70)
    print("KAeasy Fixture Test Runner")
    print("=" * 70)

    print(f"\n1. Adversarial Fixtures ({len(ADVERSARIAL_FIXTURES)} files):")
    lint_failures = []
    for name, text, expected in ADVERSARIAL_FIXTURES:
        findings = lint.check_text(text, strict=True)
        actual_findings = [f.as_dict() for f in findings]
        exp_findings = expected.get("findings", [])
        if actual_findings != exp_findings:
            lint_failures.append((name, text, exp_findings, actual_findings))
            print(f"  [FAIL] {name}: {len(actual_findings)} findings (expected {len(exp_findings)})")
        else:
            print(f"  [OK]   {name}")

    print("\n2. Tool Status:")
    print(f"  ka_lint:   ACTIVE ({len(ADVERSARIAL_FIXTURES) - len(lint_failures)}/{len(ADVERSARIAL_FIXTURES)} passed)")
    print(f"  ka_fix:    {'ACTIVE' if KA_FIX_FN else 'NOT IMPLEMENTED (v0.3)'}")
    print(f"  ka_speech: {'ACTIVE' if KA_SPEECH_FN else 'NOT IMPLEMENTED (v0.3)'}")

    print(f"\n3. Speech Golden Dataset: {len(SPEECH_CASES)} lines loaded.")
    speech_errors = [
        (idx, c) for idx, c in SPEECH_CASES
        if lint.check_text(c["spoken"], mode="speech", strict=True)
    ]
    if speech_errors:
        print(f"  [FAIL] {len(speech_errors)} lines have speech lint errors")
    else:
        print(f"  [OK]   All {len(SPEECH_CASES)} lines pass strict speech mode linter")

    if lint_failures:
        print(f"\n4. Bugs documented in docs/TOOL-BUGS.md: {len(lint_failures)}")
        for name, _, _, findings in lint_failures:
            print(f"  - {name}: {[f['check'] for f in findings]}")

    print("\nDone.")
    return 0 if not speech_errors else 1


if __name__ == "__main__":
    sys.exit(run_standalone())
