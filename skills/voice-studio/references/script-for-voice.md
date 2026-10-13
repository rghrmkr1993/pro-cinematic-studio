# Script for voice (write for the ear, spoken Tamil first)

Labels: F sourced (sources.md), E estimate, U unverified. All Tamil examples below are my own drafts: a native Tamil speaker must review spelling, register and region (Chennai, Madurai, Kongu, Jaffna, Singapore differ) before use. Product claims in scripts come only from the approved claims list.

## 1. Core rule
Formal written Tamil (செந்தமிழ், news and textbook style) read by a TTS gives a news-reader delivery, a major cause of the robotic sound (3P, vendor guides: engines follow your text and do not convert register). Write spoken Tamil (பேச்சுத் தமிழ், everyday speech). Pick one register per script and keep it; do not mix formal and colloquial in one line (3P).
Region: choose the voice's accent first, then write in that region's spoken forms. Tanglish (Tamil with English nouns) is natural for modern urban audiences; use English words people really say, not forced ones.

## 2. Formal vs spoken (E, native review needed)
| Formal (robotic) | Spoken (natural) | Meaning |
|---|---|---|
| இந்த சோப்பு இயற்கையான பொருட்களால் தயாரிக்கப்பட்டுள்ளது. | இந்த சோப்பு முழுக்க இயற்கையான பொருள்லயே செஞ்சது. | This soap is made only with natural ingredients. |
| நீங்கள் இதை தாராளமாகப் பயன்படுத்தலாம். | நீங்க இதை தாராளமா யூஸ் பண்ணலாம். | You can use this freely. |
| நான் உங்களுக்கு ஒன்று சொல்ல விரும்புகிறேன். | உங்ககிட்ட ஒண்ணு சொல்லணும். | I want to tell you something. |
| என்ன செய்வது என்று தெரியவில்லை. | என்ன பண்றதுன்னே தெரியல. | I do not know what to do. |
| மிகவும் மகிழ்ச்சி. | ரொம்ப சந்தோஷம். | Very happy. |
| அவர் வந்து கொண்டிருக்கிறார். | அவரு வந்துட்டு இருக்காரு. | He is coming. |
| உங்கள் சருமத்திற்கு ஏற்றது. | உங்க சருமத்துக்கு நல்லா பொருந்தும். | Suits your skin. |
| தயவுசெய்து காத்திருங்கள். | கொஞ்சம் இருங்க, வந்துடுறேன். | Please wait a moment. |
Patterns: -ஆல் / -இல் endings become -ல; "நீங்கள்" becomes "நீங்க"; "-கிறேன்" becomes "-றேன்"; "என்று" becomes "-னு" or "-ன்னு"; drop formal verb chains ("செய்து கொண்டிருக்கிறார்" becomes "செஞ்சுட்டு இருக்காரு").

## 3. Write for the ear (any language)
- One idea per sentence, 6 to 14 words; longer lines only when the emotion needs a run-on.
- Read aloud before you generate. If you run out of breath, split it.
- Front-load the key word; spoken Tamil puts the verb last, so keep the thing to stress just before it.
- Use direct address: "நீங்க" and "நம்ம", questions to the listener, short reactions ("ஆமா", "சரி", "அட!").
- Repeat a key word instead of using a synonym; ears like repetition.
- Avoid stacked abstract nouns, brochure phrases, passive constructions, ingredient lists in one breath (split into 3 items, each its own line).
- Cut acronyms and symbols; say them as words.
- Vary line length: short, short, long, short creates natural rhythm (E).

## 4. Punctuation for breath (v3 and v4, E for Tamil)
- Full stop: a clear stop and drop of pitch.
- Comma: a quick breath, pitch holds.
- Ellipsis `...`: a longer pause, hesitation, trailing feeling. Use 1 or 2 per paragraph, not more.
- Dash `-`: a lighter, quicker break (less consistent).
- Question mark: raises pitch; in spoken Tamil a yes or no question often ends with "-ஆ" (வருவீங்களா?). Keep the "ஆ" and the mark.
- Exclamation: more energy; one per paragraph at most.
- New line per breath group. A blank line gives a longer pause.
- No `<break>` on v3 and v4 (F); older models only. Many breaks in one generation can destabilise output (F).

## 5. Numbers, dates, symbols
Write them as spoken words in the chosen register; engines misread currency, phone numbers, dates, units (F).
- 899 rupees: standard `எண்ணூற்று தொண்ணூற்று ஒன்பது ரூபாய்`; a spoken variant is shorter, ask the native reviewer which the voice's region uses (U).
- Round numbers are safest: 100 `நூறு`, 50 `ஐம்பது`, 5 percent `ஐந்து சதவீதம்`.
- Phone digits: one by one with commas between groups: `ஒன்பது, எட்டு, ஏழு... `.
- Dates: `அக்டோபர் பதிமூணாம் தேதி` (October 13th, spoken form; reviewer check, U).
- Units: 100 g `நூறு கிராம்`, 2 minutes `ரெண்டு நிமிஷம்`.
- Free shipping thresholds, prices and offers: take the exact value from the client brief, then spell it; never guess.
- Test: generate the number line alone in rung 1.

## 6. English and brand words
- Try three spellings in the test line: Tamil script transliteration (`வைட்டமின் ஈ`), phonetic respelling, Latin. Keep the best per engine and store it in a pronunciation dictionary (elevenlabs-advanced.md section 6).
- Keep brand names identical in every line; spell once in the dictionary.
- English words inside a Tamil sentence work better in Tamil script on most engines (E, test).
- Never invent a Tamil name for a product; use the registered name.

## 7. Disfluencies (sparingly)
Real speech has them; too many sounds fake. Rule of thumb: 1 per 4 to 6 lines, only in casual or emotional speech, never in a product claim or legal line.
- Fillers: `வந்து...`, `அது வந்து...`, `அதாவது`, `இல்லையா?`, `சரி`.
- Restarts: `நான்... இல்ல, நாங்க அதை ஆரம்பிச்சோம்.` (I... no, we started it.)
- Breath word: `ம்ம்`, `ஹா`, a soft `[exhales]` tag before an emotional line.
- Do not put fillers where the engine speaks them in a robotic, even way; if so, remove and use an ellipsis and let breath layering add the feel (humanize-post.md).

## 8. Emotion arcs (write the shift into the words)
Plan 3 beats per 30 s: set up (calm), turn (energy rises or drops), landing (resolve).
Example, 28 s product story (draft, native review):
1. `காலைல எழுந்ததும்... முகம் கொஞ்சம் இறுக்கமா இருக்கும், இல்லையா?` (calm, a shared feeling)
2. `எங்க பாட்டி அதுக்கு ஒரு சின்ன வழி வெச்சிருந்தாங்க.` (warming)
3. `[warm] அதே மாதிரி, முழுக்க இயற்கையா... இப்போ உங்க கையில.` (landing, slower, smile)
Direction notes per line (not spoken): pace slow, smile, lower pitch on the last phrase.

## 9. Examples by use (Tamil drafts, spoken, native review required)
Ad hook (5 s): `ஒரு நிமிஷம்! இதை பாத்தீங்களா?` (One minute! Have you seen this?)
Warm narration: `சில விஷயங்கள் மெதுவா தான் நடக்கும். அதுதான் அழகு.` (Some things happen slowly. That is the beauty.)
Emotional character, sad: `நான்... அப்படி நினைக்கல. [sighs] ஆனா இப்போ எல்லாம் மாறிடுச்சு.` (I did not think so, but now everything changed.)
Angry character: `போதும்! இன்னும் எவ்ளோ நாள் இதே கதையா?` (Enough! How long the same story?)
Tanglish explainer: `இந்த serum-ல வைட்டமின் சி இருக்கு. ஒரு நாளைக்கு ரெண்டு drop போதும்.` (This serum has vitamin C. Two drops a day is enough. Dosage and claim must come from approved copy.)
Call to action: `இன்னைக்கே ட்ரை பண்ணி பாருங்க.` (Try it today.)

## 10. Script checklist before rung 1
- Every line is spoken Tamil in one register, reviewed by a native speaker.
- Lines 6 to 14 words, one breath each.
- Numbers, dates, units written as words.
- Brand and English words have a chosen spelling and a dictionary entry.
- At most 1 tag per phrase where the feeling changes; no tag in neutral lines.
- 1 emotion arc planned; direction note per hero line.
- Claims match the approved list; no testimonial voiced by a synthetic voice.
- Hardest-content test line chosen (credits ladder rung 1).
