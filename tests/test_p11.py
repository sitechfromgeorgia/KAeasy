"""Tests for P11: Legal Georgian, Numbers/Dates/Ordinals, Georgian Companies."""
import json
from pathlib import Path

from kaeasy import fix, lint, speech

ROOT = Path(__file__).resolve().parent.parent


def test_ordinals_above_100():
    assert speech.speech("180-ე მუხლი") == "ას მეოთხმოცე მუხლი"
    assert speech.speech("353-ე მუხლი") == "სამას ორმოცდამეცამეტე მუხლი"
    assert speech.speech("1001-ე მუხლი") == "ათას მეერთე მუხლი"
    assert speech.speech("2000-ე მუხლი") == "მეორიათასე მუხლი"
    assert speech.speech("2026-ე მუხლი") == "ორი ათას ოცდამეექვსე მუხლი"


def test_dates_speech():
    assert speech.speech("22 ნოემბერს") == "ოცდაორ ნოემბერს"
    assert speech.speech("22-ე ნოემბერს") == "ოცდაორ ნოემბერს"
    assert speech.speech("22 ნოემბერი") == "ოცდაორი ნოემბერი"
    assert speech.speech("1 ნოემბერს") == "პირველ ნოემბერს"
    assert speech.speech("1-ელი ნოემბერი") == "პირველი ნოემბერი"
    assert speech.speech("1-ელ ნოემბერს") == "პირველ ნოემბერს"
    assert speech.speech("10-14 ოქტომბერს") == "ათიდან თოთხმეტ ოქტომბრამდე"


def test_prime_articles_speech():
    assert speech.speech("353¹-ე მუხლი") == "სამას ორმოცდამეცამეტე პრიმა მუხლი"


def test_georgian_abbreviations_speech():
    assert speech.speech("სზაკ-ის") == "საქართველოს ზოგადი ადმინისტრაციული კოდექსის"
    assert speech.speech("შსს-ს") == "შინაგან საქმეთა სამინისტროს"
    assert speech.speech("შსს-მ") == "შინაგან საქმეთა სამინისტრომ"
    assert speech.speech("სუს-ის") == "სახელმწიფო უსაფრთხოების სამსახურის"
    assert speech.speech("სებ-ის") == "საქართველოს ეროვნული ბანკის"
    assert speech.speech("სსკ-ის") == "ეს ეს კას"


def test_company_speech_and_lexicon():
    assert speech.speech("TBC") == "თიბისი"
    assert speech.speech("TBC-მ") == "თიბისიმ"
    assert speech.speech("IT") == "აი-თი"


def test_lint_ordinal_date():
    # True positives (must flag)
    bad_examples = [
        "შეხვედრა 22-ე ნოემბერს გაიმართება.",
        "კონფერენცია ოცდამეორე ნოემბერს ჩატარდება.",
        "ეს მოხდა მეთხუთმეტე მარტს.",
        "დღეს 8-ე აპრილია.",
    ]
    for text in bad_examples:
        findings = lint.check_text(text, strict=True)
        assert any(f.check == "ordinal_date" for f in findings), f"Failed to flag: {text}"

    # True negatives (must NOT flag)
    good_examples = [
        "შეხვედრა 22 ნოემბერს გაიმართება.",
        "შეხვედრა ოცდაორ ნოემბერს გაიმართება.",
        "1-ელი ნოემბერი უქმე დღეა.",
        "პირველ ნოემბერს შევიკრიბებით.",
        "ზედიზედ მეორე მარტს აღინიშნა რეკორდი.",
        "ეს არის მე-5 მუხლი.",
    ]
    for text in good_examples:
        findings = lint.check_text(text, strict=True)
        assert not any(f.check == "ordinal_date" for f in findings), f"False positive on: {text}"


def test_lint_wrong_name():
    # True positives
    bad_examples = [
        "ანგარიში „ტიბისი“ ბანკშია გახსნილი.",
        "ტიბისიმ ახალი სერვისი გაუშვა.",
    ]
    for text in bad_examples:
        findings = lint.check_text(text, strict=True)
        assert any(f.check == "wrong_name" for f in findings), f"Failed to flag: {text}"

    # True negatives
    good_examples = [
        "ანგარიში „თიბისი“ ბანკშია გახსნილი.",
        "თიბისიმ ახალი სერვისი გაუშვა.",
        "TBC-მ ახალი სერვისი გაუშვა.",
    ]
    for text in good_examples:
        findings = lint.check_text(text, strict=True)
        assert not any(f.check == "wrong_name" for f in findings), f"False positive on: {text}"


def test_fix_ordinal_date():
    fixed, changes = fix.fix_text("შეხვედრა 22-ე ნოემბერს გაიმართება.")
    assert fixed == "შეხვედრა 22 ნოემბერს გაიმართება."
    assert any("ordinal_date" in c for c in changes)

    # 1-ელი remains untouched
    fixed_first, changes_first = fix.fix_text("1-ელი ნოემბერი ოფიციალური დღეა.")
    assert fixed_first == "1-ელი ნოემბერი ოფიციალური დღეა."
    assert not changes_first


def test_speech_numbers_golden():
    golden_path = ROOT / "tests" / "fixtures" / "speech_numbers_golden.jsonl"
    assert golden_path.exists()

    with open(golden_path, encoding="utf-8") as f:
        pairs = [json.loads(line) for line in f if line.strip()]

    assert len(pairs) >= 200, f"Expected 200+ pairs, got {len(pairs)}"

    for i, pair in enumerate(pairs):
        w = pair["written"]
        expected = pair["spoken"]
        actual = speech.speech(w)
        assert actual == expected, f"Row {i}: written='{w}', expected='{expected}', got='{actual}'"
        # Golden spoken forms must pass strict speech lint
        findings = lint.check_text(expected, mode="speech", strict=True)
        assert findings == [], f"Row {i} spoken '{expected}' failed lint: {findings}"


def test_skill_sizes_and_glossary_counts():
    legal_skill = ROOT / "skills" / "georgian-legal" / "SKILL.md"
    assert legal_skill.exists()
    assert len(legal_skill.read_text(encoding="utf-8")) < 12000

    law_json = ROOT / "data" / "glossary" / "law.json"
    law_items = json.loads(law_json.read_text(encoding="utf-8"))
    assert len(law_items) >= 200

    companies_json = ROOT / "data" / "glossary" / "georgia-companies.json"
    company_items = json.loads(companies_json.read_text(encoding="utf-8"))
    assert len(company_items) >= 150
