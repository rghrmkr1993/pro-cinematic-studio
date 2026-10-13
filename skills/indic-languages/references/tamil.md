# Tamil (ta)

Labels: F sourced (sources.md), 3P third party, E estimate or craft norm, U unverified. Native Tamil review is a gate. Do not repeat: formal vs spoken table, number words and punctuation for breath are in `voice-studio/references/script-for-voice.md`; tool prices and the blind test are in `voice-studio/references/indian-language-tts-options.md`; UI strings are in `i18n-tamil-hindi`.

## 1. Script (Unicode block U+0B80 to U+0BFF, F)
- 12 vowels (uyir), 18 consonants (mei), the aytam ஃ (U+0B83), and 216 consonant-vowel combinations. Grantha letters ஜ ஷ ஸ ஹ serve loanwords; க்ஷ and ஸ்ரீ are the only real conjuncts (F, r12a).
- Pulli (U+0BCD) kills the inherent vowel; it marks codas, geminates and clusters. There are no stacked conjuncts, unlike the other four scripts.
- One letter per stop: க is k, g or h depending on position; there is no aspirated or voiced series. Consequence: English "b d g j" and "ph th" have no native letters. Write English words in Tamil script as people say them, or the engine guesses.
- Pitfalls:
  - Two-part vowel signs ொ ோ ௌ (U+0BCA to 0BCC) exist precomposed and as pairs; store precomposed (F). Vowel signs follow the consonant in storage but draw on both sides, so a naive character counter or a split at a code point breaks them.
  - The sri ligature forms only with ீ; elsewhere a visible pulli shows (F). Do not split க்ஷ or ஸ்ரீ in line breaks.
  - Ra tail, u and uu ligatures vary by font; Malaysia and Singapore expect the tailed ra everywhere (F). Tamil needs extra line height (F).
  - Never use ஃ as a visual pulli. Never strip ZWJ or ZWNJ in clean-up scripts (rare in Tamil, but harmless to keep). Normalise to NFC before diffing text.
  - Browsers and some tools backspace one code point at a time; test edits on a conjunct.
- Subtitle and caption tools need HarfBuzz/raqm shaping. ffmpeg with libass and libharfbuzz shapes correctly (checked on this machine 2026-10-14); Pillow here has raqm False, and edit-director's Pillow text paths therefore break Tamil, so burn Tamil captions through libass (see subtitles-and-transliteration.md).

## 2. Phonology (F from Wikipedia Tamil phonology unless marked)
- Places of the coronal series that TTS blurs: dental த (t̪), alveolar ற (r or t in ற்ற), retroflex ட (ʈ). Nasals: dental ந, alveolar ன, retroflex ண. Laterals: ல alveolar, ள retroflex. Initial ந is dental; ன never starts a word (E).
- ழ (zha) is a retroflex approximant [ɻ], the sound in "Tamiḻ"; it can merge with ள or ய in some modern or non-native speech (F). It is the first thing a native listener tests. Say it as "zh" with the tongue curled back and no lateral touch.
- Vowel length is phonemic, five short and five long plus ஐ ஔ; long is about twice as long as short (3P acoustic papers). Short u at word end is reduced (E); do not let a voice add a full "u".
- Gemination: doubled consonants are held, and voiceless. Single stops between vowels or after nasals are voiced or fricated: பகல் sounds like "pagal" (F). TTS often voices geminates or devoices singles; fix by testing ப்ப, த்த, க்க words.
- Rhythm: syllable-timed in practice, light stress on the first syllable, no contrastive stress (E). Questions: yes or no ends with ஆ and a rise (வருவீங்களா?); statements fall; wh-words carry a mid-sentence peak, then fall (E).
- Retroflex shape at the lips is invisible, so lipsync cannot show ட vs த; see lipsync-and-dubbing.md.

## 3. Register and dialect
- Written/literary centamil (செந்தமிழ்) vs spoken koduntamil or pechu Tamil. Spoken forms are not misspellings; film and ads use spoken forms (F, existing voice-studio note). Pick one register per character.
- Chennai (Madras bashai): clipped, English and Hindi loan words, slang like "semma", "mokka", "machan"; the sentence-end "-a/-nga" (E). Madurai and the south (Tirunelveli): longer vowels, "ஏலே", "-ங்கோ"; drawling, lower-pitched rural colour (E, U on specifics). Coimbatore (Kongu): "-ங்க", "ஏனுங்க", "அப்பு" and soft, deferential tone (E). Jaffna and Sri Lankan Tamil: older forms, different vocabulary and verb endings ("போனனான்" for "போனேன்"), distinct intonation (E); never use it for a Chennai character. Singapore and Malaysia Tamil: own loans and a tailed ra.
- Tanglish: English nouns and verbs inside Tamil grammar, Tamil verbs "பண்ணு" and "ஆகு" carry it ("check பண்ணு", "late ஆயிடுச்சு"). Switch at phrase edges, 1 or 2 English words per clause for urban youth; more for IT-sector characters; less for rural or elder.

## 4. TTS pronunciation fixes
| Problem | Fix |
|---|---|
| ழ read as ள or ய | Test the word alone; add it to the pronunciation dictionary with a respelling that works (U, per engine) or pick a native voice (Bulbul and native ElevenLabs voices handle it better, 3P) |
| English word read in Tamil letter-by-letter or with wrong stress | Tamil-script respelling: வைட்டமின் சி, சீரம்; try Latin as second option |
| b, d, g, j, f missing | Use ப/ட/க with a voiced context, or ஜ and ஃப; keep the form that scores best, store it |
| Number misread | Write words: ஆயிரத்து எண்ணூற்று ஐம்பது; use round numbers (E, native check) |
| Pulli dropped, final consonant swallowed | Add a half-beat comma or a space after the word |
| Geminate too short | Keep the doubled form in text; avoid a hyphen inside the word |
| Flat questions | Keep ஆ and the question mark; end on a short word |
Use spacing as the last resort; mid-word hyphens or spaces change the sound.

## 5. Honorifics and sensitivities (E, native review)
- நீ (intimate, children), நீங்க (polite, default), நீங்கள் (formal or written). "-ங்க" after verbs softens: சொல்லுங்க. Kin and address: அண்ணா, அக்கா, தம்பி, தங்கச்சி, அம்மா, அப்பா, ஐயா, சார், மேடம், மாமா, அத்தை, பாட்டி, தாத்தா. "டா/டி" only for close peers; to an elder it is rude.
- Sensitive: caste names and caste-coded surnames or slurs, Hindi imposition and language politics, the Sri Lankan Tamil conflict, "Madrasi" as a pejorative, religious festival accuracy (Pongal, Deepavali, Ramzan, Christmas in Tamil Nadu), political leaders and film-star names (no living real person; flag to Manager), Thirukkural and devotional lines (quote only with a source).

## 6. Tools (snapshot 2026-10-14; test every one)
| Tool | Status for Tamil |
|---|---|
| ElevenLabs v3 | Listed (F, official language list); 20+ Tamil library voices; best tags and STS; pronunciation weaker than Bulbul on names (3P) |
| Sarvam Bulbul v3 and v4-flash | ta-IN supported (F, API docs); good on names and Tanglish (3P vendor); 2,500 character limit |
| Google Chirp 3 HD | ta-IN supported, not Preview (F, docs) |
| Azure neural | ta-IN Pallavi and Valluvar (F, per tts-options file) |
| IndicF5 and Parler | Open, self-host (F) |
| Cartesia, Smallest, Fish | Cartesia and Smallest list Tamil (F, vendor); Fish U |
| Lipsync tools | Audio-driven models accept any audio; test (see lipsync-and-dubbing.md) |
Routing: narration and names, Bulbul or ElevenLabs by blind test; emotional scenes, ElevenLabs v3 with at most one tag, or STS from a human actor. 3 takes before committing.

## 7. Five spoken lines (own drafts, native review required)
1. என்னங்க, இன்னைக்கு லேட்டா வந்திருக்கீங்க? | ennanga, innaikku late-aa vandhirukkeenga? | What is this, you have come late today?
2. சாப்பிட்டீங்களா? வாங்க, உக்காருங்க. | saappitteengalaa? vaanga, ukkaarunga. | Have you eaten? Come, sit down.
3. அட, இது ரொம்ப நல்லா இருக்கே! | ada, idhu romba nallaa irukke! | Oh, this is really good!
4. நாளைக்கு காலைல ஒம்பது மணிக்கு பாக்கலாம், சரியா? | naalaikku kaalaila ombadhu manikku paakkalaam, sariyaa? | Let us meet tomorrow at nine in the morning, okay?
5. எனக்கு இது புடிக்கல... ஆனா சொல்றதுக்கு பயமா இருக்கு. | enakku idhu pudikkala... aana soldradhukku bayamaa irukku. | I did not like this, but I am scared to say it.
Line 4 uses the spoken "ஒம்பது" for "ஒன்பது"; check the region.
