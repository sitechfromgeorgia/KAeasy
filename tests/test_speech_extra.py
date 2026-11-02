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


@pytest.mark.parametrize("text,want", [
    # A root ი stays before an ending (latin_endings.json "i-sound", spelled letters): v0.3 dropped it (ტმ, სონმ).
    ("ChatGPT-მ უპასუხა", "ჩატ ჯი პი ტიმ უპასუხა"),
    ("AMD-ს გრაფიკა", "ეი ემ დის გრაფიკა"),
    ("Sony-მ დაანონსა", "სონიმ დაანონსა"),
    ("ASML-მა დაამზადა", "ეი ეს ემ ელმა დაამზადა"),
    ("მოკლე SMS", "მოკლე ეს ემ ესი"),
    ("სექტორი B2B", "სექტორი ბი თუ ბი"),
    ("v3.8", "ვერსია სამი წერტილი რვა"),
    # Units and currency signs written as their own word.
    ("10 ₾", "ათი ლარი"),
    ("100 ₾-ად", "ას ლარად"),
    ("$50-ით", "ორმოცდაათი დოლარით"),
    ("60 კმ/სთ", "სამოცი კილომეტრი საათში"),
    ("25°C-მდე", "ოცდახუთ გრადუსამდე"),
    ("20 ევროდ", "ოც ევროდ"),
    ("17 მლრდ დოლარი", "ჩვიდმეტი მლრდ დოლარი"),
    # Halves, dates, times before საათი, ranges before a counted noun, phone numbers.
    ("1,5%-ით", "ერთნახევარი პროცენტით"),
    ("1-ელ იანვარს", "პირველ იანვარს"),
    ("1 ივნისს", "პირველ ივნისს"),
    ("09:00 საათზე", "ცხრა საათზე"),
    ("18:30 საათზე.", "თვრამეტ საათსა და ოცდაათ წუთზე."),
    ("10-15 წუთი", "ათიდან თხუთმეტ წუთამდე"),
    ("2020-2024 წლებში", "ორი ათას ოციდან ორი ათას ოცდაოთხ წლამდე"),
    ("+995 577 00 11 22", "პლუს ცხრაას ოთხმოცდათხუთმეტი, ხუთი შვიდი შვიდი, ნული ნული, თერთმეტი, ოცდაორი"),
])
def test_v04_speech_fixes(text, want):
    assert speech(text) == want
    assert lint.check_text(speech(text), mode="speech", strict=True) == []


@pytest.mark.parametrize("token,want", [
    ("Microsoft-მდე", "მაიკროსოფტამდე"),
    ("Microsoft-დან", "მაიკროსოფტიდან"),
    ("NVIDIA-მდე", "ენვიდიამდე"),
])
def test_consonant_stem_takes_the_full_ending(token, want):
    assert speak_token(token) == want


def test_acronym_before_a_model_number_keeps_the_bare_letter():
    assert speech("RTX 20 სერია") == "არ ტი ექს ოცი სერია"
    assert speech("ახალი RTX.") == "ახალი არ ტი ექსი."
