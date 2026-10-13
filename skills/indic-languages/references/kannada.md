# Kannada (kn)

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Native Kannada review is a gate. Kannada tool coverage is real but thinner than Hindi, with fewer independent quality tests (U).

## 1. Script (Unicode block U+0C80 to U+0CFF, F)
- Abugida descended from the Kadamba script (F, Wikipedia). 13 vowels ಅ ಆ ಇ ಈ ಉ ಊ ಋ ಎ ಏ ಐ ಒ ಓ ಔ, 34 consonants ಕ to ಳ, anusvara ಂ, visarga ಃ. Virama U+0CCD joins consonants; the second takes a subscript form (ottakshara): ಕ್ಷ, ಸ್ತ.
- Look-alike of Telugu. Never allow a Telugu font fallback for Kannada text; verify the caption font actually contains Kannada.
- Pitfalls:
  - Split vowel signs (ೊ ೋ ೌ ೈ) combine around the base; precomposed vs pair varies; normalise NFC.
  - Ra as first element (arkavattu) draws as a tail after the cluster; font dependent; test ಕರ್ನಾಟಕ, ಧರ್ಮ.
  - Obsolete ೞ and ಱ appear in old texts; modern text does not use them (F, merged sounds).
  - Do not strip ZWJ or ZWNJ; count graphemes, not code points, for subtitle limits.
- Caption tools need HarfBuzz/raqm shaping. ffmpeg libass with libharfbuzz handles Kannada; edit-director's Pillow has no raqm (checked 2026-10-14), so route Kannada captions through libass or a browser renderer.

## 2. Phonology (F from Wikipedia Kannada unless marked)
- Vowel length is contrastive for a, i, u, e, o. Unlike Hindi, Kannada has short and long e and o (E), so "e" in a name must be marked in a dictionary if the engine collapses them.
- Retroflex series is prominent; dental ತ ದ vs retroflex ಟ ಡ ಣ ಳ. ಳ (retroflex lateral) is kept; the old zha-like ೞ merged away (F). ಷ often sounds as ಶ outside retroflex clusters (F).
- Aspirates are rare in native words, common in loans, and often dropped in informal speech (F). English /f/ and /z/ are often replaced with /pʰ/ and /dʒ/ in older speech (F); younger urban speakers keep them (E).
- Most consonants geminate; hold doubled letters. Kannada adds a final "-u" to many borrowed words ("bus-u", "car-u") (E); in a script it is the written form that carries the u.
- Rhythm: syllable-timed and even, gentle pace (existing asian-human-reference note). Questions: ending ಆ ("ಬರ್ತೀಯಾ?") and a rise (E).

## 3. Register and dialect
- Written/formal (grantha-based, Sanskritised) vs spoken (ಆಡುಮಾತು); the written standard is uniform, speech varies by region (F). Old, Middle and Modern Kannada (Halegannada, Nadugannada, Hosagannada) are historical periods, not registers (F). Do not call them "formal" and "colloquial".
- Standard speech is based on Mysore-Bangalore; Dharwad (north, firmer consonants, older features), Kalaburagi (Hyderabad-Karnataka, Urdu and Telugu influence), Mangalore and coastal (Tulu and Konkani influence), Kodava, Hatkar (F for the groupings; E for colour).
- Kanglish: Bengaluru Kannada mixes English freely ("ಟೈಮ್ ಇಲ್ಲ", "ಮೀಟಿಂಗ್ ಇದೆ"); typical of IT-sector characters; rural or elder characters use far less.
- Spoken contractions: ಮಾಡುತ್ತಿದ್ದೇನೆ becomes ಮಾಡ್ತಾ ಇದ್ದೀನಿ; ಬರುತ್ತೇನೆ becomes ಬರ್ತೀನಿ (E, native review).

## 4. TTS pronunciation fixes
| Problem | Fix |
|---|---|
| Short vs long e/o collapsed | Dictionary respelling per engine (U); native voice |
| Aspirate over-pronounced in loans | Respell without the aspirate in casual lines |
| Geminate short | Keep doubled letters; no hyphen inside |
| ಳ vs ಲ confusion | Test alone with ಬೆಳಗ್ಗೆ, ಕಲಿ |
| English words | Kannada-script respelling first (ಫೋನ್, ಸೀರಮ್), Latin second |
| Conjunct read letter by letter | Check font and text normalisation first, engine second |
| Numbers | Words; ordinary Arabic digits are read by some engines in Kannada, test |
| Final -u dropped or doubled | Keep the written form; add a comma, not a respelling |

## 5. Honorifics and sensitivities (E)
- ನೀನು (intimate), ನೀವು (polite default), "-ರೀ" in calls ("ಏನ್ರೀ"), "-ಅವರು" after names. Address: ಅಣ್ಣ, ಅಕ್ಕ, ತಮ್ಮ, ತಂಗಿ, ಅಪ್ಪ, ಅಮ್ಮ, ಸರ್, ಮೇಡಂ, ಸ್ವಾಮಿ, ಮಾವ, ಅತ್ತೆ. "ಲೋ/ಲೇ" only for peers.
- Sensitive: Kannada language pride and Hindi imposition, the Cauvery dispute with Tamil Nadu, Kannadiga vs outsider talk in Bengaluru, North vs South Karnataka, caste and community, religion, living politicians and film stars (film fan culture is strong).

## 6. Tools (snapshot 2026-10-14; test every one)
| Tool | Status for Kannada |
|---|---|
| ElevenLabs v3 | Listed (F, official list); v3 only (3P) |
| Sarvam Bulbul v3 and v4-flash | kn-IN supported (F, API docs) |
| Google Chirp 3 HD | kn-IN supported for TTS (F); Chirp 3 speech-to-text lists Kannada as Preview (F, search summary) |
| Azure neural | kn-IN voices (E, check live list) |
| IndicF5, Indic Parler | Open (F) |
| ElevenLabs dubbing | Kannada listed (F, help centre via search) |
3 takes before committing; native listener scores blind.

## 7. Five spoken lines (own drafts, native review required)
1. ಏನ್ರೀ, ಇವತ್ತು ತಡವಾಗಿ ಬಂದ್ರಿ? | enree, ivattu tadavaagi bandri? | What is this, you came late today?
2. ಊಟ ಆಯ್ತಾ? ಬನ್ನಿ, ಕೂತ್ಕೊಳ್ಳಿ. | oota aaytaa? banni, kootkolli. | Have you eaten? Come, sit.
3. ಅರೆ, ಇದು ತುಂಬಾ ಚೆನ್ನಾಗಿದೆ! | are, idu tumba chennaagide! | Oh, this is really nice!
4. ನಾಳೆ ಬೆಳಿಗ್ಗೆ ಒಂಬತ್ತು ಗಂಟೆಗೆ ಸಿಗೋಣ, ಸರಿನಾ? | naale beLigge ombattu gantege sigoNa, sarinaa? | Let us meet tomorrow at nine in the morning, okay?
5. ನನಗೆ ಇದು ಇಷ್ಟ ಆಗಲಿಲ್ಲ... ಆದರೆ ಹೇಳೋಕೆ ಭಯ ಆಗುತ್ತೆ. | nanage idu ishta aagalilla... aadare heLoke bhaya aagutte. | I did not like this, but I am scared to say it.
