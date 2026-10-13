# Telugu (te)

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Native Telugu review is a gate. Telugu has no Tamil-style written/spoken file in voice-studio, so the register notes here are the base; for the ear rules see `voice-studio/references/script-for-voice.md` (the principles carry over).

## 1. Script (Unicode block U+0C00 to U+0C7F, F)
- Abugida with an inherent "a". Vowels: అ ఆ ఇ ఈ ఉ ఊ ఋ ఎ ఏ ఐ ఒ ఓ ఔ, plus anusvara ం, candrabindu ఁ, visarga ః. Consonants in the five varga rows (క చ ట త ప) plus య ర ల వ శ ష స హ ళ and ఱ (archaic), క్ష.
- Virama U+0C4D joins consonants; the second consonant takes a subscript form (vattu), so clusters stack below the first: స్త, క్ష. Telugu and Kannada look alike; never fall back to a Kannada font for Telugu text.
- Pitfalls:
  - Vowel signs ై ొ ో ౌ and the length marks U+0C55 and U+0C56 are combining; pairs vs precomposed can differ across tools. Normalise to NFC, test the font.
  - Subscript ra, ya and other vattu shapes depend on the font; test కృ, క్ర, స్త్ర in your caption font.
  - Do not strip ZWJ or ZWNJ; they steer conjunct shapes.
  - Counting characters for subtitles by code points overstates length; count grapheme clusters (see subtitles-and-transliteration.md).
- Caption tools need HarfBuzz/raqm shaping. ffmpeg libass with libharfbuzz shapes Telugu; edit-director's Pillow lacks raqm (checked 2026-10-14), so route Telugu captions through libass, not PIL.

## 2. Phonology (F from Wikipedia Telugu language page)
- Dental త ద vs retroflex ట డ ణ ళ. Retroflex consonants sit mostly between vowels or next to another retroflex, a few begin words. In casual speech ణ and ళ often merge into న and ల except next to retroflex stops (F).
- Aspirated and breathy consonants (ఖ ఘ ఛ ఝ ఠ ఢ థ ధ ఫ భ) arrive mainly through Sanskrit loans and are lighter in colloquial speech; Telangana speech uses fewer (F). Native Telugu essentially has none, so TTS over-aspirating a loan word is a real defect.
- Vowel length is phonemic for i u e o a (short vs long). Native words do not end in a long vowel; words end in a vowel (E). Short, open syllables give a rhythmic, vowel-ending sound.
- Gemination is phonemic between vowels: అటు (that side) vs అట్టు (pancake, F). Hold the doubled consonant; TTS often shortens it.
- No contrastive stress; listeners perceive prominence on the penult or final (F, with speaker variation). Yes or no questions end with ఆ ("వస్తావా?") and rise (E); wh-questions fall.
- Final -m often nasalises to a [w̃] sound in speech; ś often reads as s (F).

## 3. Register and dialect
- Written/literary (grandhika) vs spoken (vyavaharika). The modern written standard follows spoken forms from educated Coastal Andhra speakers (F, based on the central dialect). Spoken contraction example: చేస్తున్నాను becomes చేస్తున్నా; "మీరు" polite with "-అండి" (E, U on specifics).
- Telangana: Hyderabad flavour with Urdu and Hindi loans ("జర", "గట్ల", "ఇట్ల", "ఏంది", "బాగున్నావా"), less aspiration, ś to ṣ merging (F for sound facts). Coastal Andhra: the film and TV default; "ఏంటి", "ఎందుకు". Rayalaseema: "ఏమ్రా", sound variants of "eyes" such as kaṇḍḷu or kaṇḷu against Coastal kaḷḷu (F), strong, direct tone (E). North Andhra (Uttarandhra, Srikakulam): own vocabulary and lilt (E, U).
- Mixing Telangana and Andhra idiom without intent reads as an error to natives; also a political marker since the 2014 state split (E). Decide per character and keep the voice's accent matched.
- Tenglish: English nouns inside Telugu grammar, "ఓకే", "సరే", verb "చేయి" or "అవ్వు" ("update చేయి", "late అయింది"). Hyderabad IT characters use more; keep switching at phrase edges (E).

## 4. TTS pronunciation fixes
| Problem | Fix |
|---|---|
| Over-aspirated or voiced loan sounds | Respell the loan in native-adapted form or test the Latin variant; keep what scores |
| Geminate collapsed | Keep the doubled consonant; avoid splitting with spaces |
| ణ ళ pronounced in a colloquial line | Write the colloquial న ల form if the character speaks casually |
| English words | Telugu-script respelling first (ఫోన్, సీరం), Latin second |
| Numbers | Spell as words; avoid mixed digit strings |
| Final vowels clipped | Keep full word endings; add a comma where a breath is wanted |
| Question flat | Keep ఆ and the mark |

## 5. Honorifics and sensitivities (E)
- నువ్వు (familiar), మీరు (polite default), "-గారు" after names (రావుగారు), "-అండి" in requests. Kin and address: అన్న, అక్క, తమ్ముడు, చెల్లి, అమ్మ, నాన్న, బాబాయ్, మామయ్య, అత్త, సార్, మేడం. "రా/రే" only for close peers.
- Sensitive: caste and surname codes, Andhra and Telangana identity and the 2014 split, regional films and fan culture, religious accuracy, living politicians and film stars, derisive use of "ఆంధ్రా".

## 6. Tools (snapshot 2026-10-14; test every one)
| Tool | Status for Telugu |
|---|---|
| ElevenLabs v3 | Listed (F, official list); v3 only, not on older models (3P) |
| Sarvam Bulbul v3 and v4-flash | te-IN supported (F, API docs) |
| Google Chirp 3 HD | te-IN supported (F, docs) |
| Azure neural | te-IN voices exist (E, check the live list) |
| IndicF5, Indic Parler | Open, self-host (F) |
| Cartesia, Smallest | U for Telugu quality; test |
| ElevenLabs dubbing | Telugu listed in v1 and v2 (F, help centre, via search) |
Telugu dubs run long against English; see lipsync-and-dubbing.md. 3 takes before committing.

## 7. Five spoken lines (own drafts, native review required)
1. ఏం చేస్తున్నావ్? భోజనం చేసావా? | em chestunnaav? bhojanam chesaavaa? | What are you doing? Have you eaten?
2. రండి, కూర్చోండి. కాఫీ తీసుకుంటారా? | randi, koorchondi. kaafee teesukuntaaraa? | Come, sit. Will you have coffee?
3. అబ్బా, ఇది చాలా బాగుంది! | abbaa, idi chaalaa baagundi! | Wow, this is really nice!
4. రేపు పొద్దున్నే తొమ్మిదింటికి కలుద్దాం, సరేనా? | repu poddunne tommidintiki kaluddaam, sarenaa? | Let us meet tomorrow morning at nine, okay?
5. నాకు నచ్చలేదు... కానీ చెప్పాలంటే భయంగా ఉంది. | naaku nachchaledu... kaani cheppaalante bhayangaa undi. | I did not like it, but I am scared to say it.
