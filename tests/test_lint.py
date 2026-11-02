import re
from pathlib import Path

import pytest
from kaeasy import lint

SKILLS = Path(__file__).resolve().parent.parent / "skills"


def checks(text, **kw):
    return {f.check for f in lint.check_text(text, **kw)}


@pytest.mark.parametrize("text,check", [
    ("მაიკროსოფტმა ახალი მოდელი წარადგინა.", "translit"),
    ("Microsoftმა ახალი მოდელი წარადგინა.", "ending_hyphen"),
    ("Microsoft -მა ახალი მოდელი წარადგინა.", "ending_hyphen"),
    ('მან თქვა "ჩვენ ვჩერდებით" და წავიდა.', "quotes"),
    ("ფასი 20 % -ით გაიზარდა.", "percent"),
    ("შემოსავალი 2.5 მილიარდი დოლარია.", "decimal"),
    ("5 სტატიები გამოქვეყნდა.", "number_plural"),
    ("სამი კომპანიები განაცხადებს.", "number_plural"),
    ("კომპანია — ბაზრის ლიდერი.", "dash"),
    ("შეხვედრამ ადგილი მიიღო თბილისში.", "calque"),
    ("მნიშვნელოვანია აღინიშნოს, რომ ფასი გაიზარდა.", "ai_filler"),
    ("ოფისი Germany-ში გაიხსნა.", "country"),
    ("კომპანია და და პროდუქტი.", "dup_word"),
    ("ტექსტი пример აქ.", "cyrillic"),
])
def test_detects(text, check):
    assert check in checks(text)


@pytest.mark.parametrize("text", [
    "Microsoft-მა ახალი მოდელი წარადგინა.",
    "OpenAI-მ და NVIDIA-მ თანამშრომლობა გამოაცხადეს.",
    "კომპანიამ 2,5 მილიარდი დოლარი მოიზიდა, შემოსავალი 36%-ით გაიზარდა.",
    "ფასები 2020-2024 წლებში გაიზარდა.",
    "მან თქვა: „ჩვენ ვჩერდებით“.",
    "ხუთმა კომპანიამ განაცხადა, რომ 300 თანამშრომელს დაიქირავებს.",
    "გამოქვეყნდა და მალე გავრცელდა.",
    "მეტად მნიშვნელოვანი გადაწყვეტილება მიიღეს.",
    "საიტი sitech.ge და ვერსია 3.8 მუშაობს.",
])
def test_clean(text):
    assert lint.check_text(text) == []


def test_speech_mode_allows_georgian_brands_and_flags_latin_digits():
    assert lint.check_text("მაიკროსოფტმა ოცდათექვსმეტი პროცენტით გაზარდა.", mode="speech") == []
    assert "latin_in_speech" in checks("Microsoft-მა 36%-ით გაზარდა.", mode="speech")


def test_title_period():
    assert "title_period" in checks("ტექსტი.", title="Apple-მა ახალი iPhone წარადგინა.")
    assert "title_period" not in checks("ტექსტი.", title="Apple-მა ახალი iPhone წარადგინა")


def test_offsets_point_at_the_match():
    text = "ბევრი ტექსტი. Microsoftმა წარადგინა."
    (f,) = lint.check_text(text)
    assert text[f.start:f.end] == "Microsoftმა"


def test_html_tags_do_not_create_spacing_findings():
    assert lint.check_text("<b>ფასი</b> <i>გაიზარდა</i>. <span>სიტყვა</span>.") == []


def test_strict_drops_noisy_rules():
    assert "calque" not in checks("შეხვედრამ ადგილი მიიღო.", strict=True)


def _right_examples():
    """Every ✅ form in the skills' examples files must lint clean in strict mode (false-positive guard)."""
    out = []
    for md in SKILLS.glob("*/examples/*.md"):
        for line in md.read_text(encoding="utf-8").splitlines():
            m = re.search(r"✅\s*(.+?)(?:\s*\(|$)", line)
            if m and "/" not in m.group(1):
                # A trailing "..." in an example means "sentence continues", not an ellipsis.
                text = re.sub(r"\s*\.\.\.$", "", m.group(1).strip())
                out.append((md.parent.parent.name, text))
    return out


@pytest.mark.parametrize("skill,text", _right_examples())
def test_examples_right_side_is_clean(skill, text):
    mode = "social" if skill == "georgian-social" else "article"
    assert [f.message for f in lint.check_text(text, mode=mode, strict=True)] == []
