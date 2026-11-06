import json
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
    ("Microsoft მა ახალი მოდელი წარადგინა.", "ending_hyphen"),
    ("Google ს ახალი პოლიტიკა აქვს.", "ending_hyphen"),
    ("Linux ზე სისტემა მუშაობს.", "ending_hyphen"),
    ("Docker ში გაეშვა.", "ending_hyphen"),
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
    ("ამას შესახებ ინფორმაცია არ გვაქვს.", "postposition_dative"),
    ("ამას გამო პროექტი შეფერხდა.", "postposition_dative"),
    ("ამას მიხედვით გადაწყვეტენ.", "postposition_dative"),
    ("იმას შესახებ არაფერი უთქვამს.", "postposition_dative"),
    ("იმას გამო კომპანია დაიხურა.", "postposition_dative"),
    ("იმას მიხედვით იმსჯელებენ.", "postposition_dative"),
    ("რას შესახებ საუბრობთ?", "postposition_dative"),
    ("მონაცემებს მიხედვით სისტემა მზადაა.", "postposition_dative"),
    ("კომპანიებს შესახებ ახალი კანონი მიიღეს.", "postposition_dative"),
    ("შეცდომებს გამო სერვისი გაითიშა.", "postposition_dative"),
    ("API ებს გადასცემენ.", "ending_hyphen"),
    ("Meta თი სარგებლობენ.", "ending_hyphen"),
    ("353 პირველი მუხლით გასამართლდა.", "legal_citation"),
    ("353 მუხლის პირველი მუხლი არ არსებობს.", "legal_citation"),
    ("მეორე ოქტომბერს დაიწყო.", "date_ordinal"),
    ("ოცდამეცხრე ნოემბერს გაგრძელდება.", "date_ordinal"),
    ("ვერცერთი არ შესრულდა.", "negation"),
    ("არცერთი არ მოვიდა.", "negation"),
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
    "Python ის ენაა, რომელსაც ყველა იყენებს.",
    "353-ე მუხლის პირველი ნაწილით გასამართლდა.",
    "353-ე პრიმა მუხლის პირველი ნაწილით წაუყენეს ბრალი.",
    "ორ ოქტომბერს დაიწყო და ოცდაცხრა ნოემბერს გაგრძელდება.",
    "Tesla Model S გამოვიდა.",
    "May თვის ანგარიში გამოქვეყნდა.",
    "ამის შესახებ დოკუმენტში წერია.",
    "იმის გამო გადაიდო, რომ წვიმდა.",
    "მონაცემების მიხედვით სისტემა მზადაა.",
    "კომპანიების შესახებ ანგარიში მომზადდა.",
    "ვის შესახებ საუბრობთ?",
    "ყველას შესახებ ვიცით.",
    "ჩვენს შესახებ გვერდი განახლდა.",
    "გიორგის შესახებ მოვისმინეთ.",
    "შოთას შესახებ დაწერეს.",
    "მეტროს შესახებ სტატია გამოქვეყნდა.",
    "Meta-ს შესახებ ინფორმაცია გავრცელდა.",
    "ვერცერთი შესრულდა.",
    "არცერთი მოვიდა.",
    "არავინ არ იცის.",
    "არავინ არ იცის პასუხი.",
])
def test_clean(text):
    assert lint.check_text(text) == []


def test_postposition_dative():
    findings = lint.check_text("ამას შესახებ და მონაცემებს მიხედვით.")
    assert len(findings) == 2
    assert findings[0].check == "postposition_dative"
    assert "„ამას შესახებ“ → „ამის შესახებ“" in findings[0].message
    assert findings[1].check == "postposition_dative"
    assert "„მონაცემებს მიხედვით“ → „მონაცემების მიხედვით“" in findings[1].message


def test_speech_mode_allows_georgian_brands_and_flags_latin_digits():
    assert lint.check_text("მაიკროსოფტმა ოცდათექვსმეტი პროცენტით გაზარდა.", mode="speech") == []
    assert "latin_in_speech" in checks("Microsoft-მა 36%-ით გაზარდა.", mode="speech")


def test_speech_mode_russian_letters():
    assert "russian_letter" in checks("ახალი ჯი პი ტე გამოვიდა.", mode="speech")
    assert "russian_letter" in checks("ახალი გე პე უ წარადგინეს.", mode="speech")
    assert "russian_letter" in checks("ბე ბი სის რეპორტაჟი.", mode="speech")
    assert checks("ბე-ემ-ვე-მ ახალი მოდელი წარადგინა.", mode="speech") == set()
    assert "russian_letter" in checks("ა პე ი განახლდა.", mode="speech")
    assert checks("ახალი ჯი პი ტი გამოვიდა.", mode="speech") == set()
    assert checks("ახალი ჯი პი იუ წარადგინეს.", mode="speech") == set()
    assert checks("ტექნოლოგია და ტელეფონი განახლდა.", mode="speech") == set()
    assert checks("პერსონალი და ბერკეტი მზადაა.", mode="speech") == set()
    assert checks("სისტემა გამართულად მუშაობს.", mode="speech") == set()
    assert "russian_letter" not in checks("ტექნოლოგია სწრაფად ვითარდება.", mode="article")


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
    mode = {"georgian-social": "social", "georgian-speech": "speech", "georgian-ui": "ui"}.get(skill, "article")
    assert [f.message for f in lint.check_text(text, mode=mode, strict=True)] == []


def test_brands_match_latin_endings():
    root = Path(__file__).resolve().parent.parent
    data_path = root / "data" / "latin_endings.json"
    assert data_path.exists(), "data/latin_endings.json missing"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    classes = data["classes"]
    names = data["names"]

    brands_md = SKILLS / "georgian-names-numbers" / "references" / "brands.md"
    assert brands_md.exists(), "brands.md missing"
    text = brands_md.read_text(encoding="utf-8")
    table_lines = [l for l in text.splitlines() if re.match(r"^\|\s*\d+\s*\|", l)]
    assert len(table_lines) == 120, f"Expected 120 brands in brands.md, got {len(table_lines)}"

    for l in table_lines:
        parts = [p.strip() for p in l.split("|")[1:-1]]
        _, name, erg, gen, dat = parts[:5]
        assert name in names, f"Brand '{name}' from brands.md not found in data/latin_endings.json"
        sound_class = names[name]
        assert sound_class in classes, f"Unknown sound class '{sound_class}' for brand '{name}'"
        c = classes[sound_class]
        assert erg == f"{name}{c['erg']}", f"Ergative mismatch for {name}: expected {name}{c['erg']}, got {erg}"
        assert gen == f"{name}{c['gen']}", f"Genitive mismatch for {name}: expected {name}{c['gen']}, got {gen}"
        assert dat == f"{name}{c['dat']}", f"Dative mismatch for {name}: expected {name}{c['dat']}, got {dat}"


def test_latin_names_reference_table():
    root = Path(__file__).resolve().parent.parent
    data_path = root / "data" / "latin_endings.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    classes = data["classes"]
    names = data["names"]

    latin_names_md = SKILLS / "georgian-names-numbers" / "references" / "latin-names.md"
    assert latin_names_md.exists(), "latin-names.md missing"
    text = latin_names_md.read_text(encoding="utf-8")
    table_lines = [
        l for l in text.splitlines()
        if l.startswith("|") and not l.startswith("| written") and not l.startswith("|---")
        and not l.startswith("| #") and not l.startswith("| **") and not l.startswith("| Grammatical")
    ]
    assert len(table_lines) >= 200, f"Expected at least 200 names in latin-names.md, got {len(table_lines)}"

    for l in table_lines:
        parts = [p.strip() for p in l.split("|")[1:-1]]
        if len(parts) < 9:
            continue
        written, sound_class, erg, dat, gen, instr, in_post, plural = parts[:8]
        assert written in names, f"Name '{written}' not in data/latin_endings.json"
        assert sound_class == names[written], f"Class mismatch for '{written}'"
        c = classes[sound_class]
        assert erg == f"{written}{c['erg']}"
        assert dat == f"{written}{c['dat']}"
        assert gen == f"{written}{c['gen']}"
        assert instr == f"{written}{c['instr']}"
        assert in_post == f"{written}{c['in']}"
        assert plural == f"{written}{c['plural']}"



@pytest.mark.parametrize("text,check,want", [
    ("OpenAI-მა ახალი მოდელი გამოუშვა.", "latin_ergative", "OpenAI-მ"),
    ("Meta-მა განაცხადა.", "latin_ergative", "Meta-მ"),
    ("Microsoft-მ ფასი გაზარდა.", "latin_ergative", "Microsoft-მა"),
    ("Stability AI-მა მოდელი გახსნა.", "latin_ergative", "Stability AI-მ"),
    ("OpenAI-ის მოდელი", "latin_case", "OpenAI-ს"),
    ("ChatGPT-თი დაწერეს.", "latin_case", "ChatGPT-ით"),
    ("NVIDIA-ით გაიზარდა.", "latin_case", "NVIDIA-თი"),
])
def test_latin_name_endings(text, check, want):
    found = [f for f in lint.check_text(text) if f.check == check]
    assert found and f"„{want}“" in found[0].message
    assert (check in {f.check for f in lint.check_text(text, strict=True)}) == (check == "latin_ergative")


@pytest.mark.parametrize("text", [
    "OpenAI-მ, Meta-მ და Microsoft-მა განაცხადეს.",
    "OpenAI-ს, NVIDIA-ს და Google-ის მოდელები.",
    "ChatGPT-ით, NVIDIA-თი და Microsoft-ით.",
    "Meta-სთვის და Microsoft-ისთვის.",
    "ბლოგი my-OpenAI-მა-test.example-ზე.",
])
def test_latin_name_endings_clean(text):
    assert [f for f in lint.check_text(text) if f.check.startswith("latin_")] == []


def test_negation_and_split():
    # Both incorrect sentences trigger the error
    f1 = lint.check_text("ვერცერთი არ შესრულდა.")
    assert any(f.check == "negation" and f.severity == "error" for f in f1)
    assert any("ვერცერთი/არცერთი თავად უარყოფითია, ზმნას არ არ სჭირდება" in f.message for f in f1)

    f2 = lint.check_text("არცერთი არ მოვიდა.")
    assert any(f.check == "negation" and f.severity == "error" for f in f2)
    assert any("ვერცერთი/არცერთი თავად უარყოფითია, ზმნას არ არ სჭირდება" in f.message for f in f2)

    # Both correct sentences are clean
    assert lint.check_text("ვერცერთი შესრულდა.") == []
    assert lint.check_text("არცერთი მოვიდა.") == []

    # არავინ არ იცის is still clean and unchanged
    assert lint.check_text("არავინ არ იცის.") == []
    assert lint.check_text("არავინ არ იცის პასუხი.") == []

    # Strict mode includes negation
    assert "negation" in checks("ვერცერთი არ შესრულდა.", strict=True)
    assert "negation" in checks("არცერთი არ მოვიდა.", strict=True)

    # Separate warning for split spelling: ვერც ერთი and არც ერთი
    w1 = lint.check_text("არც ერთი მოვიდა.")
    assert any(f.check == "negation_split" and f.severity == "warn" for f in w1)

    w2 = lint.check_text("ვერც ერთი შესრულდა.")
    assert any(f.check == "negation_split" and f.severity == "warn" for f in w2)

    # Exception: when ერთი is a numeral, e.g. ვერც ერთ ღამეს
    w3 = lint.check_text("ვერც ერთ ღამეს არ უძინია.")
    assert not any(f.check == "negation_split" for f in w3)
