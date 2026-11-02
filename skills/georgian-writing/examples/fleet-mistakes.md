# Real fleet mistakes (SiTech Shorts review, Oct–Nov 2026)

These are not invented. Each pair is a sentence our own agents wrote and the review fixed (from
`sitech-shorts-lab/data/edits.jsonl`, 918 edits, picked by hand). Read them before writing: they show what
DeepSeek-class models actually get wrong in our copy. The full set lives in the mistakes memory (`ka_mistakes`).

## Case and agreement

- ❌ ჩვენი აზრით, ავტომატიზაცია დაცვას უფრო სწრაფს უნდა გახადოს. ✅ ჩვენი აზრით, ავტომატიზაციამ დაცვა უნდა დააჩქაროს. (უნდა + optative is series II: ergative subject, nominative object)
- ❌ ჭორების მიხედვით, NVIDIA შესაძლოა ახალი ვერსია გამოუშვას. ✅ ჭორების მიხედვით, NVIDIA-მ შესაძლოა ახალი ვერსია გამოუშვას. (optative: ergative subject)
- ❌ 15 000 აგზავნიან. ✅ 15 000-ს აგზავნიან. (present tense: dative object, with a hyphenated ending)
- ❌ AI აგენტებმა მხოლოდ ასეულები შექმნეს. ✅ AI აგენტებმა რამდენიმე ასეული შექმნეს. (a count word stays singular)

## Postpositions

- ❌ კარტრიჯი ქსელს გარეთ რჩება. ✅ კარტრიჯი ქსელის გარეთ რჩება. (გარეთ takes the genitive)
- ❌ მილიარდი იენი ინვესტიცია ✅ მილიარდი იენის ინვესტიცია (amount of what: genitive)
- ❌ სატელიტზე TPU-ები ✅ სატელიტის TPU-ები (possession, not location)
- ❌ წინა წლის პერიოდზე გაიზარდა ✅ წინა წლის ანალოგიურ პერიოდთან შედარებით გაიზარდა (compared to: -თან შედარებით)
- ❌ ის Apple-ისა და OpenAI-ს AI მოდელებზეა აგებული. ✅ ის Apple-ისა და OpenAI-ს AI მოდელებს ეყრდნობა. (English "built on")

## Verbs, tense, word order

- ❌ ფასი არ შეცვილა. ✅ ფასი არ შეიცვალა. (wrong verb form)
- ❌ თუ არ დააჩქარეს, ვადა გადაიწევს. ✅ თუ არ დააჩქარებენ, ვადა გადაიწევს. (თუ + future for a condition)
- ❌ ეს ეხება აბონენტებს, თუ კვოტა ჯერ არ ამოწურეს. ✅ ეს ეხება აბონენტებს, ვისაც კვოტა ჯერ არ ამოუწურავს. (perfect: "have not used up yet")
- ❌ AI-ზე 7 216 დოლარზე მეტი დახარჯა. ✅ ოპერატორმა AI-ზე 7 216 დოლარზე მეტი დახარჯა. (name the actor)
- ❌ აგენტმა შეარჩია სამიზნე. ✅ აგენტმა სამიზნე შეარჩია. (object before the verb, verb at the end)
- ❌ ეს კრიტიკული ხარვეზია. ✅ ხარვეზი კრიტიკულია. (say what is critical)

## Calques (English shape in Georgian words)

- ❌ თავდამსხმელი ლოკალურ ქსელში ✅ თავდამსხმელი ადგილობრივ ქსელში (local network)
- ❌ AI აფართოებს თავდასხმის მასშტაბს. ✅ AI ზრდის თავდასხმის მასშტაბს. (scale grows, it does not widen)
- ❌ სიფრთხილისთვის კომპანიამ სერტიფიკატები შეცვალა. ✅ სიფრთხილის ზომად კომპანიამ სერტიფიკატები შეცვალა. (as a precaution)
- ❌ პროდუქტზე ფოკუსი სწორი არჩევანია. ✅ პროდუქტებზე ორიენტირება სწორი არჩევანია. (focus on)
- ❌ ახალგაზრდების ფსონი ✅ ახალგაზრდებზე ფსონი (a bet on someone: -ზე)
- ❌ ხარვეზი არის 16 წლის ბუფერის გადავსება. ✅ ხარვეზი 16 წლის ბუფერის გადავსებაა. (copula -ა instead of English "is")
- ❌ ფასი 2,2-ჯერ მეტია. ✅ ფასი საწყის ფასზე 2,2-ჯერ მეტია. (more than what: -ზე მეტი)

## Words

- ❌ ადმინი ✅ ადმინისტრატორი (slang in news copy)
- ❌ კომპანიამ ტოპ გეგმებს სახელი შეუცვალა. ✅ კომპანიამ ორ უმაღლეს გეგმას სახელი შეუცვალა. (English "top")
- ❌ ბაზისური მოდელი ✅ საბაზისო მოდელი (established term)
- ❌ სისტემაში შეღწევა ✅ სისტემაში შეჭრა (security term)
- ❌ ორბიტაზე AI ცენტრი ✅ ორბიტაზე მონაცემთა ცენტრი (data center)

## Names and numbers

- ❌ ChatGPT ინტეგრაცია ✅ ChatGPT-ს ინტეგრაცია (a brand before a noun takes the genitive; -i sound: -ს)
- ❌ Oracle აპები ✅ Oracle-ის აპები (genitive)
- ❌ PNY ვერსია ✅ PNY-ის ვერსია (genitive)
- ❌ TPU-ები 2027-დან ✅ TPU-ები 2027 წლიდან (a year takes წელი)
- ❌ ოთხი კვირა ✅ 4 კვირა (house style: digits on screen)

## Punctuation and tone

- ❌ NVIDIA ჩაერთვება თუ Nscale ვერ გადაიხდის. ✅ NVIDIA ჩაერთვება, თუ Nscale ვერ გადაიხდის. (comma before a თუ clause)
- ❌ OpenAI IPO-ს გეგმავს, ცნობით. ✅ ცნობით, OpenAI IPO-ს გეგმავს. (the source goes first)
- ❌ ყველა სერვერი დაუცველი არ არის. ✅ ყველა სერვერი დაუცველი არაა. (spoken register in Shorts)
