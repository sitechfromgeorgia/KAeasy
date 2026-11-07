"""Regressions found reviewing P11. Each case here failed on the merged P11 code."""
import json
from pathlib import Path

import pytest
from kaeasy import fix, lint, speech

ROOT = Path(__file__).resolve().parent.parent
COMPANIES = json.loads((ROOT / "data" / "glossary" / "georgia-companies.json").read_text(encoding="utf-8"))
COMPANIES_MD = ROOT / "skills" / "georgian-names-numbers" / "references" / "glossary-georgia-companies.md"


def wrong_names(text):
    return [f for f in lint.check_text(text, strict=True) if f.check == "wrong_name"]


def date_findings(text):
    return [f for f in lint.check_text(text, strict=True) if f.check == "date_ordinal"]


def declined(name):
    """Case forms of a name, the ones an agent will write in news copy."""
    if name.endswith("ი"):
        stem = name[:-1]
        return [name, stem + "მა", stem + "ის", stem + "ს", stem + "ით", stem + "ზე", stem + "ში"]
    return [name, name + "მ", name + "ს", name + "ზე", name + "ში"]


@pytest.mark.parametrize("name", [r["preferred"] for r in COMPANIES])
def test_a_company_name_never_flags_itself(name):
    for form in declined(name):
        assert not wrong_names(f"{form} განაცხადა."), form


@pytest.mark.parametrize("text", [
    "ბინა 100 მ2 ფართობისაა.",
    "ნოე ჟორდანია პრემიერი იყო.",
    "არქიმედეს კანონი ყველამ იცის.",
    "პავლე ინგოროყვას წიგნი გამოიცა.",
    "ლუკოილმა ფასი დააკლო.",
    "საქსტატის მონაცემებით ინფლაცია შემცირდა.",
    "თსუ-ს სტუდენტები შეიკრიბნენ.",
    "საზოგადოებრივი მაუწყებელი გადაცემას აჩვენებს.",
    "სპარს ჯარს მეფე მეთაურობდა.",
    "ლიბერტი მედიამ ანგარიში გამოაქვეყნა.",
])
def test_wrong_name_leaves_correct_text_alone(text):
    assert not wrong_names(text)


@pytest.mark.parametrize("text", [
    "ტიბისიმ განაცხადა.", "ტი ბი სი", "ტელასმა განაცხადა.", "ტელასის მომხმარებლები.", "მაგტის აბონენტები.",
    "სილკნეტმა განაცხადა.", "ლიბერტი ბანკში.", "ჰალიკ ბანკმა.", "როუმპეტროლის სადგური.",
])
def test_wrong_name_catches_declined_misspellings(text):
    assert wrong_names(text)


def test_every_company_row_is_in_the_markdown_view():
    view = COMPANIES_MD.read_text(encoding="utf-8")
    assert all(f"**{r['preferred']}**" in view for r in COMPANIES)


@pytest.mark.parametrize("text", [
    "მე-2 ოქტომბრის სხდომა.", "ოცდამეორე ნოემბრის შეხვედრა.", "22-ე ნოემბრის ღონისძიება.",
    "მეხუთე დეკემბრიდან.", "მეცამეტე იანვარს.", "დღეს მეოთხე თებერვალია.", "22-ე ოქტომბრამდე.",
])
def test_date_ordinal_catches_shortened_month_stems(text):
    assert date_findings(text)


@pytest.mark.parametrize("text", [
    "მეორე მარტივი გზა ჯობია.", "მესამე მაისური იყიდა.", "მეორე მარტო დარჩა.", "2-ე მარტივი რიცხვი.",
    "2024-ე ნოემბერი არ არსებობს.",
])
def test_date_ordinal_needs_a_real_month(text):
    assert not date_findings(text)


def test_month_forms_are_the_same_in_lint_and_speech():
    assert lint.MONTH_FORM[3:-1] in speech.MONTHS.pattern


@pytest.mark.parametrize(("written", "fixed"), [
    ("22-ე ნოემბრის", "22 ნოემბრის"),
    ("მე-22 ნოემბერს", "22 ნოემბერს"),
    ("მე-22-ე ნოემბერს", "22 ნოემბერს"),
    ("2-ე ოქტომბრამდე", "2 ოქტომბრამდე"),
    ("2-ე მარტივი რიცხვი", "2-ე მარტივი რიცხვი"),
    ("2024-ე ნოემბერი", "2024-ე ნოემბერი"),
])
def test_fix_date_ordinals(written, fixed):
    assert fix.fix_text(written)[0] == fixed


@pytest.mark.parametrize(("written", "spoken"), [
    ("მე-1 ივნისს", "პირველ ივნისს"),
    ("20-22 ნოემბრის", "ოციდან ოცდაორ ნოემბრამდე"),
    ("2-ე მარტივი რიცხვი", "მეორე მარტივი რიცხვი"),
    ("1 მარტივი რიცხვი", "ერთი მარტივი რიცხვი"),
    ("1000000-ე", "მემილიონე"),
    ("BOG-მა", "საქართველოს ბანკმა"),
    ("GWP", "ჯივიპი"),  # Louie 2026-11-07: said as letters run together
    ("GWP-მ", "ჯივიპიმ"),
    ("GWP-ის", "ჯივიპის"),
    ("სებ-მა", "საქართველოს ეროვნულმა ბანკმა"),
    ("სებ-ს", "საქართველოს ეროვნულ ბანკს"),
    ("სებ-ის", "საქართველოს ეროვნული ბანკის"),
    ("შპს", "შე პე ეს"),
    ("სს თიბისი ბანკი", "ეს ეს თიბისი ბანკი"),
    ("PSP", "პე ეს პე"),
    ("სსსკ-ის", "ეს ეს ეს კას"),
    ("სსკ-ის", "ეს ეს კას"),
    ("ასკ", "ა ეს კა"),
    ("სასკ-ის", "საქართველოს ადმინისტრაციული საპროცესო კოდექსის"),
    ("სასკ-ს", "საქართველოს ადმინისტრაციულ საპროცესო კოდექსს"),
    ("სზაკ-მა", "საქართველოს ზოგადმა ადმინისტრაციულმა კოდექსმა"),
    ("144³ მუხლი", "ას ორმოცდამეოთხე პრიმა სამი მუხლი"),
])
def test_speech_review_cases(written, spoken):
    assert speech.speech(written) == spoken


@pytest.mark.parametrize("written", ["შპს", "შპს-ს", "PSP", "PSP-ს", "BMW"])
def test_speech_output_passes_speech_lint(written):
    assert not lint.check_text(speech.speech(written), mode="speech", strict=True)


@pytest.mark.parametrize("name", [r["spoken"] for r in COMPANIES])
def test_every_spoken_company_name_passes_speech_lint(name):
    assert not lint.check_text(name, mode="speech", strict=True), name
