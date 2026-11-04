---
name: georgian-legal
description: Writing, checking and summarizing Georgian (ka) legal texts, court reporting, contracts, legislation, official citations and procedural terms. Load when a text involves laws, articles, court verdicts, criminal or civil procedures, or contract clauses.
---

# Legal Georgian (კანონმდებლობა და იურიდიული ქართული)

This skill guides agents writing or reviewing Georgian legal texts, court reports, law analyses, contract clauses, and legislative citations (first designed for Saul). Legal accuracy takes precedence over stylistic variation: never alter the statutory meaning of a legal term to make it sound more colloquial.

Sources:
- Legislative Herald of Georgia (*matsne.gov.ge*: official consolidated laws, codes, and court acts)
- Supreme Court and Constitutional Court of Georgia official jurisprudence
- Akaki Shanidze, *Grammar of the Georgian Language*

---

## 1. Statutory Citations: Hierarchy and Order

Statutory articles must follow strict hierarchical order in text and speech:
**მუხლი → ნაწილი → პუნქტი → ქვეპუნქტი**

- ✅ `353-ე მუხლის პირველი ნაწილი` (spoken: `სამას ორმოცდამეცამეტე მუხლის პირველი ნაწილი`)
- ❌ `353-ე პირველი მუხლი` (confuses article and part; flagged by linter `legal_citation`)
- ❌ `353-ე მუხლის პირველი მუხლი` (flagged by linter `legal_citation`)
- ✅ `საქართველოს სისხლის სამართლის კოდექსის 353¹-ე მუხლი`

### Prime Articles (პრიმა მუხლები: 353¹, 126¹)
Superscript prime numbers denote distinct statutory articles added during amendment:
- `353¹` is a completely different offence from `353` (e.g. assault on police officer vs resistance).
- Spoken form: `353¹-ე მუხლი` → `სამას ორმოცდამეცამეტე პრიმა მუხლი`.
- Written with superscript index or word: `353¹-ე მუხლი` or `353-ე პრიმა მუხლი`.
- Subparts of prime articles: `353¹-ე მუხლის მე-2 ნაწილი` (spoken: `სამას ორმოცდამეცამეტე პრიმა მუხლის მეორე ნაწილი`).

---

## 2. Main Codes and Disambiguation

Main statutory codes on *matsne.gov.ge*:
1. **საქართველოს კონსტიტუცია** (Constitution of Georgia)
2. **საქართველოს სამოქალაქო კოდექსი** (Civil Code — abbreviation `სსკ`)
3. **საქართველოს სისხლის სამართლის კოდექსი** (Criminal Code — abbreviation `სსკ`)
   - ⚠️ **Critical Ambiguity**: `სსკ` stands for BOTH the Civil Code and the Criminal Code. Agents must never leave `სსკ` ambiguous in news or advisory text; explicitly state `სამოქალაქო კოდექსი` or `სისხლის სამართლის კოდექსი`.
4. **საქართველოს ადმინისტრაციულ სამართალდარღვევათა კოდექსი** (Misdemeanors / Administrative Offences — `ასკ`)
5. **საქართველოს ზოგადი ადმინისტრაციული კოდექსი** (General Administrative Code — `სზაკ`)
6. **საქართველოს სამოქალაქო საპროცესო კოდექსი** (Civil Procedure Code — `სსპკ`)
7. **საქართველოს სისხლის სამართლის საპროცესო კოდექსი** (Criminal Procedure Code — `სსსკ`)
8. **საქართველოს შრომის კოდექსი** (Labour Code of Georgia)
9. **საქართველოს საგადასახადო კოდექსი** (Tax Code of Georgia)
10. **საქართველოს კანონი „პერსონალურ მონაცემთა დაცვის შესახებ“** (Law on Personal Data Protection)

---

## 3. Confusable Legal Pairs

Never swap these distinct legal terms:

| Incorrect / Confused | Correct Legal Term | Why |
|---|---|---|
| `ეჭვმიტანილი` | `ბრალდებული` | A suspect becomes `ბრალდებული` (the accused) once formal charges/indictment are filed. |
| `ბრალდებული` | `მსჯავრდებული` | An accused becomes `მსჯავრდებული` (convict) only upon a final guilty court verdict. |
| `განაჩენი` | `გადაწყვეტილება` | `განაჩენი` (verdict/sentence) is strictly criminal; civil/administrative court issues `გადაწყვეტილება`. |
| `განჩინება` | `გადაწყვეტილება` | `განჩინება` is an interim/procedural ruling; `გადაწყვეტილება` resolves the main dispute. |
| `მოსარჩელე` | `დაზარალებული` | In civil court the claimant is `მოსარჩელე`; `დაზარალებული` is the victim in criminal court. |
| `ჯარიმა` | `პირგასამტეხლო` | `ჯარიმა` is state statutory fine; `პირგასამტეხლო` is contractual liquidated damages. |
| `ხელშეკრულება` | `შეთანხმება` | `ხელშეკრულება` is the main contract; `შეთანხმება` is an addendum or mutual accord. |
| `მესაკუთრე` | `მფლობელი` | `მესაკუთრე` has legal title; `მფლობელი` has actual physical custody or possession. |
| `ვადა` | `ხანდაზმულობა` | `ვადა` is duration/deadline; `ხანდაზმულობა` is statutory limitation period extinguishing claims. |
| `ძალადაკარგული` | `ბათილი` | `ძალადაკარგული` is repealed prospectively (ex nunc); `ბათილი` is void from inception (ab initio). |

---

## 4. Courts, Institutions and Law Enforcement

- **სასამართლო ინსტანციები** (Courts):
  - 1st instance: `საქალაქო სასამართლო` / `რაიონული სასამართლო`
  - 2nd instance: `სააპელაციო სასამართლო`
  - 3rd instance: `საქართველოს უზენაესი სასამართლო` (Court of Cassation)
  - Constitutional: `საქართველოს საკონსტიტუციო სასამართლო` (located in Batumi)
- **სამართალდამცავი და საჯარო ორგანოები** (Public Bodies):
  - `საქართველოს პროკურატურა` / `გენერალური პროკურატურა`
  - `საქართველოს შინაგან საქმეთა სამინისტრო` / `საქართველოს პოლიცია`
  - `საქართველოს იუსტიციის სამინისტრო`
  - `აღსრულების ეროვნული ბიურო` (National Bureau of Enforcement)
  - `საჯარო რეესტრის ეროვნული სააგენტო` (National Agency of Public Registry)
  - `საქართველოს ნოტარიუსთა პალატა` (Notary Chamber of Georgia)

---

## 5. Contract Drafting and Boilerplate

Georgian contracts follow standard structure under the Civil Code:
1. **მხარეები** (Parties: იურიდიული პირი / ფიზიკური პირი / წარმომადგენელი)
2. **ხელშეკრულების საგანი** (Subject matter of contract)
3. **მხარეთა უფლება-მოვალეობები** (Rights and obligations)
4. **ანგარიშსწორების წესი** (Payment terms and pricing)
5. **მხარეთა პასუხისმგებლობა და პირგასამტეხლო** (Liability and liquidated damages)
6. **დაუძლეველი ძალა / ფორსმაჟორი** (Force majeure, Civil Code §398)
7. **ხელშეკრულების მოქმედების ვადა და შეწყვეტა** (Term and termination)
8. **დავების გადაწყვეტა** (Dispute resolution: negotiation, court or arbitration)
9. **დასკვნითი დებულებები** (Final provisions)

Avoid unadapted Russian and English legalese calques:
- ❌ `დოგავორი` → ✅ `ხელშეკრულება`
- ❌ `ისკი` → ✅ `სარჩელი`
- ❌ `ნეუსტოიკა` → ✅ `პირგასამტეხლო`
- ❌ `დავნოსტი` → ✅ `ხანდაზმულობა`
- ❌ `ფორს-მაჟორი` → ✅ `ფორსმაჟორი` / `დაუძლეველი ძალა`

---

## 6. Strict Accuracy Rules for Agents

1. **Never invent article numbers**: Do not hallucinate article numbers, statutory deadlines or penalty ranges not present in verified source text.
2. **Preserve statutory nuances**: Do not replace formal legal terms with casual synonyms (`მსჯავრდებული` is not simply `დამნაშავე`; `სარჩელი` is not `საჩივარი`).
3. **Preserve presumption and attribution**: Always preserve `ბრალდების თანახმად`, `გამოძიების ვერსიით`, `სასამართლოს გადაწყვეტილებით`, `შესაძლოა`. Never state unadjudicated charges as proven facts.

---

## Deeper References & Examples

- `references/citations.md`: Detailed citation hierarchy, subparts, prime articles, speech rules.
- `references/codes-acts.md`: Complete names, Matsne links, abbreviations and scopes of main Georgian codes.
- `references/courts-institutions.md`: Judicial hierarchy, jurisdiction, public registries, prosecution.
- `references/confusable-terms.md`: 25+ legal confusable pairs with definitions and context examples.
- `references/contracts.md`: Contract structure, clauses, liabilities, force majeure, and calque avoidance.
- `examples/legal-fixes.md`: 150+ wrong → right examples in modern Georgian legal copy.
