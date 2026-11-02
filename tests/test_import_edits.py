from kaeasy import memory
from kaeasy.scripts import import_edits


def test_parse_keeps_language_edits_only():
    p = import_edits.parse("ქსელს გარეთ → ქსელის გარეთ (K7)")
    assert p == {"wrong": "ქსელს გარეთ", "right": "ქსელის გარეთ", "category": "postposition", "reason": "K7"}
    assert import_edits.parse("NVIDIA შესაძლოა → NVIDIA-მ შესაძლოა (K5, K4)")["category"] == "case"
    for skipped in [
        "წარმოების სიმძლავრეს 5-ჯერ → 2025 წლის დონესთან შედარებით 5-ჯერ (K10)",  # a fact, not language
        "take lines: ეს აპებს → ეს სამუშაოს (K3)",                              # a scene part
        "ასისტენტს დახმარება შეუძლია. → (ამოღებულია) (K9)",                    # a deletion
        "Google TPU / OCI-ზე → Google TPU-ები / მოდის OCI-ზე (K13, K21)",        # a screen layout
        "no arrow here (K3)",
    ]:
        assert import_edits.parse(skipped) is None, skipped


def test_import_writes_to_memory(tmp_path):
    edits = tmp_path / "edits.jsonl"
    edits.write_text('{"lang": "ka", "changes": ["ქსელს გარეთ → ქსელის გარეთ (K7)", "x → y (K10)"]}\n'
                     '{"lang": "en", "changes": ["a → b (K3)"]}\nnot json\n', encoding="utf-8")
    assert import_edits.main([str(edits)]) == 0
    (row,) = memory.top(10)
    assert row["right"] == "ქსელის გარეთ" and row["category"] == "postposition"
