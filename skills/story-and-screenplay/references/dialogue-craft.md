# Dialogue craft

For Tamil, Telugu, Malayalam, Kannada, Hindi and Indian English detail, open `../../indic-languages/SKILL.md` and its single language file (tamil.md, telugu.md, hindi.md and so on). For faces and gestures that go with speech, `../../asian-human-reference/SKILL.md`. This file covers the writing method.

## 1. Rules that apply in every language
1. Dialogue is action: each line tries to get something (comfort, win, hide, tease, push). If a line only informs, rewrite it as pursuit.
2. Short. One to two sentences, 6 to 12 words when a generated clip must speak it in 4 to 8 s.
3. Subtext first: people talk around the thing. Let objects and pauses carry the rest.
4. Interruptions, trailing off and repeats are natural; perfect grammar is not.
5. No speeches, no "as you know" exposition, no name in every line.
6. Read aloud and time it. If it needs a breath mid-line, split it.
7. A line fixed in the script is fixed in the prompt; do not paraphrase it later.

## 2. Voice per character
Give each speaker a sound the audience can identify with the name hidden.
| Handle | Variation |
|---|---|
| Length | Terse versus rambling |
| Register | Rural, urban, formal, slang, student, elder |
| Habit | A tag word (da, machan, ayyo, arre, yaar), a question habit, a proverb |
| Rhythm | Short bursts, long trailing, repeated words |
| What they avoid | Never says sorry, never says the name, never answers directly |
Sheet per character: age, region, class, education, one verbal habit, one forbidden word, how they speak to elders versus peers. Wide age gaps change pronouns and endings; see the language file.

## 3. Spoken versus written register
- Spoken language drops endings, merges words, uses fillers and half sentences. Written (literary) forms sound like a newsreader or a school textbook.
- Tamil: use the colloquial (koduntamil) forms. Written "Neenga enna seikireergal?" becomes spoken "Neenga enna panreenga?"; written "Naan varugiren" becomes "Naan varen". Keep da, di, pa, ma, nga, la, ae and clipped verb endings where real speakers do. Regional flavour (Madurai, Kongu, Chennai, Tirunelveli, Jaffna) is a deliberate choice, not a random mix; ask the language file.
- Telugu: spoken forms differ across Telangana and coastal Andhra; use the dialect that matches the setting; colloquial endings and particles (ra, ndi, le) not the textbook (grandhika) forms.
- Hindi: Hindustani spoken style, not Sanskritised newsreader Hindi; use Hinglish where the character would (city, college, office).
- Malayalam and Kannada: colloquial forms differ strongly from written; use native speakers' review for anything long.
- English: Indian English patterns (see section 5) when the character is Indian.
- Rule of thumb: if the line looks correct in a textbook, it is probably wrong on screen.

## 4. Tanglish and code-mixing
- Tanglish is Tamil with English words (and Tamil written in Roman). Use it as the owner speaks it. Mix where real speakers mix: tech, office, school, brand and emotional emphasis words.
- Keep the grammar frame in Tamil and slot English nouns and verbs into it: "Meeting-ku late aayidichu da." Do not translate natural English insertions into formal Tamil.
- Write Tanglish in Roman only, with the English gloss in `[EN: ...]` (see `screenplay-format.md`).
- Same method for Hinglish, Tenglish and Manglish.

## 5. Indian dialogue patterns (techniques)
- Address and kinship: people use relation words, not names (amma, appa, anna, akka, thatha, paati, mama, chithi in Tamil; bhaiya, didi, beta, chacha in Hindi). Titles and suffixes (garu, ji, sir) carry respect and distance; changing from formal to informal is a story beat.
- Elders versus peers: plural forms and honorifics for elders; singular and slang for friends. A character who drops the honorific has just made a statement.
- Indirectness: refusals are softened ("we will see", "let me ask at home"); anger often hides behind politeness or silence.
- Food as language: "Did you eat?" means care. A meal offered after a quarrel is an apology.
- Proverbs and film-style punch lines work for mass or comic moments; use sparingly and invent new ones. Do not quote existing film dialogue.
- Honour, family name and money pressure are common stakes; talk about them by implication.
- Code-switch under stress: a character may slip into the home language when emotional.
- Indian English: "only" and "itself" for emphasis, "na" tag, "what is this?" for protest, present-continuous for habit ("I am knowing him"). Use with care, as characterisation, not caricature.

## 6. Writing a line, step by step
1. What does the speaker want from the listener right now?
2. What would they say plainly? Write it, then do not use it.
3. What would a real person of that age, region and class say instead?
4. Cut to the shortest form; move meaning into a gesture or object.
5. Write the native script, the spoken transliteration and the gloss.
6. Read aloud twice; time it against the shot length.

## 7. Dialogue for generators
- One speaker per shot is safest; use reverse shots for exchanges.
- Mark the speaking character and the eyeline; lipsync quality depends on a front or three-quarter face.
- Short vowels and stops in Tamil and Hindi can run long; budget extra time or shorten the line. Check lipsync with `../../indic-languages/references/lipsync-and-dubbing.md`.
- Offer one alternate shorter line for any line over 10 words.
- Keep sensitive terms (religion, caste, politics) neutral and in line with platform rules; flag, do not decide.

## 8. Quick self-check
Read-aloud pass, subtext pass, length pass, region pass (right dialect and kinship term), consistency pass (same speech habit every scene), and a native-speaker review flag for anything shipping to the public.
