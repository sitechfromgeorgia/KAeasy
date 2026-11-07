"""The exact-form rules: `wrong_form` (strict) and `dated_form` (advice only)."""
import pytest

import lint


def checks(text, strict=True):
    return [f.check for f in lint.check_text(text, strict=strict)]


@pytest.mark.parametrize("wrong", sorted(lint.WRONG_FORMS))
def test_wrong_form_is_flagged_in_strict(wrong):
    assert "wrong_form" in checks(f"ტექსტში წერია {wrong} და მეტი.")


@pytest.mark.parametrize("wrong,right", sorted(lint.WRONG_FORMS.items()))
def test_right_form_is_clean(wrong, right):
    assert "wrong_form" not in checks(f"ტექსტში წერია {right} და მეტი.")


@pytest.mark.parametrize("wrong", sorted(lint.DATED_FORMS))
def test_dated_form_is_advice_only(wrong):
    text = f"ტექსტში წერია {wrong} და მეტი."
    assert "dated_form" in checks(text, strict=False)
    assert "dated_form" not in checks(text, strict=True)


def test_the_two_lists_do_not_overlap():
    assert not set(lint.WRONG_FORMS) & set(lint.DATED_FORMS)


def test_finding_names_the_right_form():
    finding = next(f for f in lint.check_text("ის კარგათ მუშაობს.", strict=True) if f.check == "wrong_form")
    assert finding.severity == "error"
    assert "კარგად" in finding.message


@pytest.mark.parametrize("text", [
    "„რაც სჩანს, ის არ მინდა“, — წერდა ავტორი.",  # a quotation keeps the old form
    "`სჩანს` ძველი ფორმაა.",  # code is not prose
    "მათ ალბათ იციან.",
    "მუშაობა ჩემ მიერ დასრულდა.",
    "ჩემი მიერთების პრობლემა.",  # მიერთება is not მიერ
    "მან ცხადყო, რომ მოვა.",
    "მიუხედავად იმისა, რომ გვიანია, ვრჩებით.",
])
def test_no_false_positive(text):
    assert "wrong_form" not in checks(text)


def test_a_longer_word_is_not_matched():
    assert "wrong_form" not in checks("კარგათვის წერია.")


def test_extra_spaces_in_a_phrase_still_match():
    assert "wrong_form" in checks("ეს ჩემი  მიერ დაიწერა.")
