# Malayalam (ml)

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Native Malayalam review is a gate. Malayalam is the hardest of the six for script rendering and the least covered by TTS reviews (all quality claims here are U until a native listener scores a test).

## 1. Script (Unicode block U+0D00 to U+0D7F, F)
- Abugida. Vowels അ ആ ഇ ഈ ഉ ഊ ഋ എ ഏ ഐ ഒ ഓ ഔ; consonants ക to ഹ plus ഴ (zha), ള, റ; anusvara ം, visarga ഃ. The virama (chandrakkala, U+0D4D) kills the vowel or forms conjuncts.
- Chillus: stand-alone final consonants ൻ ർ ൽ ൾ ൺ ൿ (U+0D7A to 0D7F). Use the atomic code points; the old spelling consonant + virama + ZWJ is deprecated and not canonically equal (F, r12a). A scraped or old text may hold the old form: normalise before TTS and captions.
- Conjuncts: stacked (ക്ല) or side by side (ക്ഷ), by font. "nta": ന്റ is the safe form; ൻ്റ is preferred in theory but many fonts fail (F). Modern reformed orthography uses visible chandrakkala and fewer ligatures; older books use traditional ligatures; ZWJ and ZWNJ switch between them (F). Do not strip ZWJ or ZWNJ.
- Pitfalls: the pre-base ra and the dot reph (U+0D4E); words are long, so line breaks fall mid-word at syllable edges; never split a conjunct when justifying or highlighting words in karaoke captions (F). Fonts: Noto Sans Malayalam, Manjari, Noto Serif Malayalam render both chillu forms (F).
- Caption tools need HarfBuzz/raqm shaping. ffmpeg libass with libharfbuzz handles Malayalam; edit-director's Pillow has no raqm (checked 2026-10-14), so Malayalam through PIL will show broken conjuncts. Use libass or a browser renderer.

## 2. Phonology (F from Wikipedia Malayalam phonology unless marked)
- Large consonant inventory with true subapical retroflexes and phonemic vowel length (F). Three nasals ന (dental), ണ (retroflex), plus alveolar forms; three coronal stops dental ത, retroflex ട, alveolar റ (റ്റ is the geminate "tt").
- ഴ (zha) [ɻ], retroflex approximant, as in ആഴം, also in "Kozhikode" and "mazha" (rain). ള is the retroflex lateral [ɭ] and is kept apart from ഴ; Kannada and Telugu merged theirs (F). Native listeners test ഴ first.
- Aspirates survive in Sanskrit loans more than in Tamil (ഭ ഖ ഥ), but speakers vary (E).
- Gemination is frequent and meaning-bearing: പല (many) vs പല്ല് (tooth) (E, check). Hold p, m, k, t closures longer; this shows on the lips as a longer closure (lipsync-and-dubbing.md).
- Word-final short "u" (samvruthokaram) is a reduced central vowel, not a full "u" (E, widely taught). TTS adding a full u sounds foreign.
- Rhythm: fast, rolling, geminate-heavy; no strong stress (E). Questions: -ഓ or -ആ ending with a rise ("വരുമോ?", "ആണോ?") (E).

## 3. Register and dialect
- Written (formal, Sanskritised) vs spoken colloquial; films and ads use spoken forms. Keep one register per character; formal news-reader Malayalam in a casual scene is the usual defect.
- Dialects shift by region and community: Thiruvananthapuram (south, lilting, "-ല്ലാ"), Central/Kochi (the film default), Thrissur (own rhythm and vocabulary), Malabar (Kozhikode and Kannur, Mappila colour with Arabic loans), plus Christian (Nasrani) and Brahmin variants (E, U on specifics). Do not interchange Thrissur, Kannur and Kochi forms without intent (existing film-studio note).
- Manglish (Malayalam with English words) is dense; note that film-studio and asian-human-reference also use "Manglish" for Malaysian English, so write "Malayalam-English" in briefs to avoid confusion. Gulf-returnee speech adds Arabic and Hindi loans (E).

## 4. TTS pronunciation fixes
| Problem | Fix |
|---|---|
| Chillu mispronounced or shown as box | Convert to atomic chillu code points; check font |
| ഴ read as ള or ര | Test alone; dictionary respelling per engine (U); native voice |
| Final u too full | Respell with the chandrakkala form of the word as written in modern text; test |
| Geminate short | Keep ക്ക, മ്മ, ല്ല etc.; do not hyphenate |
| Long words run together | Add a comma or a space at a natural word boundary only |
| English words | Malayalam-script respelling first, Latin second |
| Numbers | Words; avoid Malayalam digits unless asked |

## 5. Honorifics and sensitivities (E)
- നീ (intimate), നിങ്ങൾ (polite default), താങ്കൾ (formal). Address: ചേട്ടാ/ചേട്ടൻ, ചേച്ചി, മോനേ, മോളേ, അമ്മ, അച്ഛൻ, സാർ, മാഡം; community terms: ഇക്ക, ഇത്ത, ഉമ്മ, ഉപ്പ (Muslim families), അമ്മച്ചി, അപ്പച്ചൻ (Christian), തിരുമേനി (clergy). Wrong community term is a visible error.
- Sensitive: religion and community markers, caste, party politics, Gulf migration stereotypes, "Mallu" (used within the community, can offend as an outsider label), sacred and temple or church or mosque details (consult an adviser).

## 6. Tools (snapshot 2026-10-14; test every one)
| Tool | Status for Malayalam |
|---|---|
| ElevenLabs v3 | Listed (F, official list); v3 only (3P) |
| Sarvam Bulbul v3 and v4-flash | ml-IN supported (F, API docs) |
| Google Chirp 3 HD | ml-IN supported (F, docs) |
| Azure neural | ml-IN voices exist (E, check live list) |
| IndicF5, Indic Parler | Open, self-host (F) |
| ElevenLabs dubbing | Malayalam listed (F, help centre via search) |
Expect weaker lipsync and TTS here than Hindi (U); keep scripts short and test 3 takes.

## 7. Five spoken lines (own drafts, native review required)
1. എന്താ ചേട്ടാ, ഇന്ന് വൈകിയോ? | enthaa chettaa, innu vaikiyo? | What is it, brother, are you late today?
2. ഭക്ഷണം കഴിച്ചോ? വാ, ഇരിക്ക്. | bhakshanam kazhichho? vaa, irikku. | Have you eaten? Come, sit.
3. ആഹാ, ഇത് കൊള്ളാമല്ലോ! | aahaa, ithu kollaamallo! | Oh, this is good!
4. നാളെ രാവിലെ ഒമ്പത് മണിക്ക് കാണാം, ശരിയല്ലേ? | naale raavile ombathu manikku kaanaam, shariyalle? | Let us meet tomorrow at nine in the morning, alright?
5. എനിക്കിത് ഇഷ്ടപ്പെട്ടില്ല... പക്ഷേ പറയാൻ പേടിയാണ്. | enikkithu ishtappettilla... pakshe parayaan pediyaanu. | I did not like this, but I am afraid to say it.
