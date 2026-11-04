# Statutory Citations in Georgian Law

This reference specifies how to cite, write, and pronounce legal articles, paragraphs, sub-paragraphs, and prime articles in Georgian.

Source:
- Law of Georgia on Normative Acts (*საქართველოს კანონი „ნორმატიული აქტების შესახებ“*, Article 16)
- Legislative Herald of Georgia (*matsne.gov.ge*)

---

## 1. Statutory Hierarchy and Citation Order

Under Article 16 of the Law of Georgia on Normative Acts, statutes are structured hierarchically:
1. **კარი** (Part / Book)
2. **თავი** (Chapter)
3. **მუხლი** (Article)
4. **ნაწილი** / **პუნქტი** (Part in codes / Paragraph in decrees)
5. **ქვეპუნქტი** (Sub-paragraph)

### The Golden Citation Order
In Georgian, when citing a specific rule, the larger unit precedes the smaller unit, joined in the genitive case:
- ✅ `საქართველოს სისხლის სამართლის კოდექსის 180-ე მუხლის მე-2 ნაწილის „ა“ ქვეპუნქტი`
- ✅ `სამოქალაქო კოდექსის 398-ე მუხლის პირველი ნაწილი`
- ❌ `180-ე მუხლის „ა“ ქვეპუნქტის მე-2 ნაწილი` (inverted hierarchy)
- ❌ `180-ე პირველი მუხლი` (confuses article and part; flagged by `legal_citation` rule)
- ❌ `180-ე მუხლის პირველი მუხლი` (repetition error; flagged by `legal_citation` rule)

### Codes vs Decrees: `ნაწილი` vs `პუნქტი`
- In **Codes** (კოდექსი): Articles are divided into **ნაწილები** (Parts), designated by Arabic numerals (organic law on normative acts, 16.7):
  - `მუხლი 180. თაღლითობა`
  - `1. თაღლითობა, ესე იგი...` → `180-ე მუხლის პირველი ნაწილი`
- In **Laws, Government Decrees and Ministerial Orders** (კანონი, დადგენილება, ბრძანება): Articles are divided into **პუნქტები** (Paragraphs):
  - `მთავრობის დადგენილების მე-3 მუხლის მე-2 პუნქტი`
- Sub-divisions of parts or paragraphs are designated by Georgian alphabet letters in quotes:
  - `„ა“ ქვეპუნქტი`, `„ბ“ ქვეპუნქტი`, `„გ“ ქვეპუნქტი`

---

## 2. Prime Articles (პრიმა მუხლები)

When a new article is inserted between existing numbered articles without renumbering the entire code, it receives a numerical superscript index (or Latin-derived denomination):
- The law knows one word: **პრიმ** plus a digit (organic law on normative acts, 16.11). `353¹` is read `პრიმა`, `144³` is read `პრიმა სამი`.

### Why Prime Articles Matter
A prime article constitutes an entirely separate statutory offense or rule:
- Article 353 of the Criminal Code covers *Resistance, threat or violence against an official protector of public order*.
- Article 353¹ covers *Assault on a police officer, special penitentiary officer or other state representative*.
Conflating `353` and `353¹` is a severe legal error that misidentifies the charged crime and penalty.

### Writing and Speaking Prime Articles
- **Written Forms**:
  - `353¹ მუხლი` (the form the codes use)
  - `353¹-ე მუხლი` (also common)
  - `353-ე პრიმა მუხლი` (written in words)
  - `მუხლი 353¹`
- **Spoken Form for TTS (`speech_text`)**:
  - `353¹-ე მუხლი` → `სამას ორმოცდამეცამეტე პრიმა მუხლი`
  - `353¹-ე მუხლის მე-2 ნაწილი` → `სამას ორმოცდამეცამეტე პრიმა მუხლის მეორე ნაწილი`
  - `144³ მუხლი` → `ას ორმოცდამეოთხე პრიმა სამი მუხლი`

---

## 3. Case Declension of Statutory Citations

| Case | Written Citation | Spoken Form (`speech_text`) |
|---|---|---|
| **სახელობითი** (Nom) | `180-ე მუხლის პირველი ნაწილი` | `ას მეოთხმოცე მუხლის პირველი ნაწილი` |
| **მოთხრობითი** (Erg) | `180-ე მუხლის პირველმა ნაწილმა` | `ას მეოთხმოცე მუხლის პირველმა ნაწილმა` |
| **მიცემითი** (Dat) | `180-ე მუხლის პირველ ნაწილს` | `ას მეოთხმოცე მუხლის პირველ ნაწილს` |
| **ნათესაობითი** (Gen) | `180-ე მუხლის პირველი ნაწილის` | `ას მეოთხმოცე მუხლის პირველი ნაწილის` |
| **მოქმედებითი** (Inst) | `180-ე მუხლის პირველი ნაწილით` | `ას მეოთხმოცე მუხლის პირველი ნაწილით` |
| **ვითარებითი** (Adv) | `180-ე მუხლის პირველ ნაწილად` | `ას მეოთხმოცე მუხლის პირველ ნაწილად` |
| **თანდებული `-მდე`** | `180-ე მუხლის პირველ ნაწილამდე` | `ას მეოთხმოცე მუხლის პირველ ნაწილამდე` |
| **თანდებული `-დან`** | `180-ე მუხლის პირველი ნაწილიდან` | `ას მეოთხმოცე მუხლის პირველი ნაწილიდან` |

Notice that the numeral modifying `ნაწილი` or `მუხლი` declines as an attributive adjective:
- In dative and before postpositions (`-მდე`, `-ში`, `-ზე`), `პირველი` truncates its `-ი` → `პირველ ნაწილს`, `პირველ ნაწილამდე`.
- Ordinals ending in `-ე` (`მეორე`, `მესამე`, `ას მეოთხმოცე`) do not drop `-ე`.
