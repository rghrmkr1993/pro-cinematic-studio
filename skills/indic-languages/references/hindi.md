# Hindi (hi)

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Native Hindi review is a gate. Hindi has the strongest tool support of the six (existing film-studio note), but quality still depends on register and script choice.

## 1. Script (Devanagari, U+0900 to U+097F, F)
- Abugida with inherent "a". Vowels अ आ इ ई उ ऊ ऋ ए ऐ ओ औ with matras; 33 consonants क to ह plus the conjunct letters क्ष त्र ज्ञ श्र; anusvara ं, chandrabindu ँ, visarga ः, halant ् (U+094D), nukta ़ (U+093C).
- Conjuncts form with the halant; a half form shows the first consonant as a stem-less shape (क्‍ष vs क्ष). ZWJ (U+200D) asks for a half form, ZWNJ (U+200C) breaks a conjunct and shows the halant (E, standard Unicode behaviour; do not strip them).
- Pitfalls:
  - The short-i matra ि is stored after the consonant but drawn before it; a renderer without shaping shows it in the wrong place. Same for reph (र् drawn above).
  - Nukta letters क़ ख़ ग़ ज़ ड़ ढ़ फ़ have precomposed code points U+0958 to U+095F that are composition exclusions: NFC turns them into base + nukta. Compare text after normalising, and do not lose the nukta: ज़ is a different sound from ज (E, standard).
  - Devanagari digits vs Latin digits: pick one per deliverable.
  - The danda । ends a sentence; some engines read a full stop better, test.
- Caption tools need HarfBuzz/raqm shaping. ffmpeg libass with libharfbuzz shapes Devanagari (checked 2026-10-14); edit-director's Pillow has raqm False, so Hindi through PIL shows misplaced matras. Use libass or a browser renderer.

## 2. Phonology (F from Wikipedia Hindustani phonology)
- Four-way stop contrast: plain, voiced, aspirated, murmured (प, ब, फ, भ). Aspiration is the key naturalness cue; TTS that drops it sounds Dravidian-accented or flat.
- Dental त थ द ध vs retroflex ट ठ ड ढ; dental is laminal at the teeth, retroflex apical postalveolar. Flaps ड़ ढ़ are separate sounds (ढ़ often de-aspirates in colloquial Western Hindi).
- Perso-Arabic sounds /f z q x ɣ/ (फ़ ज़ क़ ख़ ग़): kept by Urdu speakers, often replaced in plain Hindi (क़ to क, फ़ to फ) (F). Choose by register; a Hindustani film character keeps them.
- Vowel length: अ इ उ short, others long; word-final close vowels are long. Nasalised vowels matter: हैं vs है, कहाँ vs कहा.
- Schwa deletion: written inherent अ is often silent: कमल is "kamal" not "kamala"; "samajh". The commonest TTS error is pronouncing the final or medial schwa. Fix by respelling with a halant in a dictionary entry or by using a different spelling that engines read right.
- Stress is weak; the heaviest syllable is stressed (F). Hindi is syllable-timed; content words start low and rise (F). Questions: a rising end on a yes or no question ("क्या" optional); wh-words stay in place and carry the peak (E).
- Verb agreement marks gender and number: जाता/जाती, गया/गई. A male voice reading a female line must be a script decision, not a tool accident.

## 3. Register and dialect
- Shuddh (Sanskritised) Hindi: news, textbook, devotional. Hindustani: everyday and Bollywood, with Urdu loans. Urdu register: Persian and Arabic loans, nukta sounds. Vocabulary can signal religion or class; choose deliberately and do not over-Sanskritise casual dialogue (film-studio note).
- Regional colour: Delhi and Khari Boli (standard), Mumbai Bambaiyya ("apun", "bhidu"), Haryanvi, Rajasthani-influenced, Bhojpuri and Awadhi-influenced speech, Punjabi-influenced Delhi (E, U on specifics). Hindi spoken by Tamil, Telugu or Bengali speakers has its own accent; cast it, never mimic it as a joke.
- Hinglish: Hindi grammar with English nouns and verbs, "update kar do", "meeting kab hai?". Script rule: write Hindi words in Devanagari and English words in Latin in the same line (mixed script); Roman Hinglish is read as English by most engines (E, test).

## 4. TTS pronunciation fixes
| Problem | Fix |
|---|---|
| Schwa not deleted | Respell or add dictionary entry; test with कमल, समझ, चलना |
| Aspiration lost | Keep the aspirate letters; avoid replacing with plain stops |
| Nukta dropped | Keep ज़ फ़ क़ in text; confirm the engine reads them |
| English word | Latin for known words (engine reads English), Devanagari respelling for names |
| Numbers | Write words: एक सौ पचास; Indian grouping lakh and crore: 1,50,000 is "डेढ़ लाख" |
| Gender of narrator | Match verb endings to the voice |
| Wrong register | Rewrite, not retime |
| Pause | Comma or full stop; danda test |

## 5. Honorifics and sensitivities (E)
- आप (respect), तुम (familiar), तू (intimate or rude). Suffix जी (शर्मा जी), भैया, दीदी, सर, मैडम, साहब, माँ, पापा, चाचा, बुआ, नानी, दादी. Address and verb must agree (आप आइए, तुम आओ, तू आ).
- Sensitive: religion-coded vocabulary (Urdu vs Sanskrit words), caste slurs and surnames, Hindi imposition when dubbing for southern markets (offer regional versions), regional stereotypes (Bihari, Punjabi, "Madrasi"), gendered insults, sacred texts and bhajans (rights and accuracy), living politicians and stars.

## 6. Tools (snapshot 2026-10-14; test every one)
| Tool | Status for Hindi |
|---|---|
| ElevenLabs v3 and older models | Supported on every current model (3P); voice library deep |
| Sarvam Bulbul v3 and v4-flash | hi-IN (F, API docs); also en-IN code-mix |
| Google Chirp 3 HD | hi-IN supported (F, docs) |
| Azure neural | hi-IN voices (E, check) |
| Higgsfield audio and translate | Hindi named in an older Higgsfield Audio post (3P) |
| IndicF5, Indic Parler | Open (F) |
| ElevenLabs dubbing | Hindi listed (F, help centre via search) |
Best default: Bulbul for Indian-accent narration, ElevenLabs for emotion; test both.

## 7. Five spoken lines (own drafts, native review required)
1. अरे, आज इतनी देर कैसे हो गई? | are, aaj itni der kaise ho gayi? | Hey, how come so late today?
2. खाना खाया? आओ, बैठो। | khaana khaaya? aao, baitho. | Have you eaten? Come, sit.
3. वाह, ये तो बहुत बढ़िया है! | waah, ye to bahut badhiya hai! | Wow, this is really great!
4. कल सुबह नौ बजे मिलते हैं, ठीक है? | kal subah nau baje milte hain, theek hai? | Let us meet tomorrow at nine in the morning, okay?
5. मुझे ये पसंद नहीं आया... पर बोलने में डर लगता है। | mujhe ye pasand nahin aaya... par bolne mein dar lagta hai. | I did not like this, but I am scared to say it.
