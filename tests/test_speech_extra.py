"""ka_speech cases added in Kaeasy (test_speech.py is the Shorts port and stays in sync with it)."""
import pytest
from kaeasy import lint
from kaeasy.speech import speak_token, speech


@pytest.mark.parametrize("token,want", [
    ("06:00-დან", "ექვსი საათიდან"),
    ("15:30-მდე", "თხუთმეტ საათსა და ოცდაათ წუთამდე"),
    ("14:05", "თოთხმეტი საათი და ხუთი წუთი"),
    ("10:00-ზე", "ათ საათზე"),
    ("09:15-ის", "ცხრა საათისა და თხუთმეტი წუთის"),
    ("-1-დან", "მინუს ერთიდან"),
    ("+1-მდე", "პლუს ერთამდე"),
    ("-5", "მინუს ხუთი"),
])
def test_times_and_signs(token, want):
    assert speak_token(token) == want


@pytest.mark.parametrize("text", [
    "UTC-ით 06:00-დან 15:30-მდე ბირჟამ 4.6%-ით ნაკლები გადაიხადა.",
    "ქულები -1-დან +1-მდე იყო, Microsoft-მა და OpenAI-მ 2026 წელს 36%-ით გაზარდეს.",
    "PayPal-მა და BMW-მ 2 250 მომხმარებელს 1-ელი ნოემბრიდან მისწერეს.",
])
def test_real_narration_comes_out_clean(text):
    assert lint.check_text(speech(text), mode="speech", strict=True) == []


def test_bmw_uses_the_established_german_letters():
    assert speak_token("BMW-მ") == "ბე-ემ-ვემ"
