"""Regressions found by comparing production Shorts narration before updating the Shorts app."""
import pytest
from kaeasy import speech


@pytest.mark.parametrize(("written", "spoken"), [
    ("AMD-ი ამბობს", "ეი ემ დი ამბობს"),
    ("Google-მა PLC-ი გადაპროგრამა", "გუგლმა პი ელ სი გადაპროგრამა"),
    ("SMS-ი მოვიდა", "ეს ემ ესი მოვიდა"),
    ("VPN დანამატი გაუქმდა", "ვი პი ენ დანამატი გაუქმდა"),
    ("DNS ზონების აგება", "დი ენ ეს ზონების აგება"),
    ("SM დანაყოფები", "ეს ემ დანაყოფები"),
    ("RTX 5090 გამოვიდა", "არ ტი ექს ხუთი ათას ოთხმოცდაათი გამოვიდა"),
    ("დაცული VPN", "დაცული ვი პი ენი"),
    ("დაცული VPN, სწრაფი DNS.", "დაცული ვი პი ენი, სწრაფი დი ენ ესი."),
    ("Broadcom-ის ვიცე-პრეზიდენტი", "ბროდკომის ვიცე-პრეზიდენტი"),
])
def test_acronym_endings(written, spoken):
    assert speech.speech(written) == spoken
