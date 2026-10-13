# Carnatic deep dive (sruti, gamaka, raga, tala, concert form, manodharma)

Extends `indian-and-tamil-music.md` (basics, melakarta, 16 ragas, eras); read that first and do not repeat it. Labels: F sourced in session research 2026-10-14 (see `sources.md` section "2026-10-14 additions"), E craft knowledge, U unverified or sources disagree. Paraphrased; no lyrics. Never name a composer, singer or composition in a prompt. A raga is a framework, not owned; a composed kriti is. A Carnatic reviewer must sign off hero cues.

## 1. Sruti and the swarasthanas
- Sruti has two senses: (a) the tonic pitch chosen for Sa, (b) the 22 srutis, the ancient division of the octave into finer pitch units (F). Modern practice uses 12 semitone positions; the 22 are a theoretical and expressive reservoir, not 22 keys (F, E). Real intonation of a note shifts with the raga and the gamaka (E).
- The 22 sruti names (traditional list, E): Tivra, Kumudvati, Manda, Chandovati, Dayavati, Ranjani, Raktika, Raudri, Krodha, Vajrika, Prasarini, Priti, Marjani, Kshiti, Rakta, Sandipani, Alapini, Madanti, Rohini, Ramya, Ugra, Kshobhini. Allocation per swara: Sa 4, Ri 3, Ga 2, Ma 4, Pa 4, Da 3, Ni 2 (E).
- 12 swarasthanas (positions, with the 16 swara names; two names share a position):
  1 Shadjam Sa | 2 Shuddha Rishabham R1 | 3 Chatushruti Rishabham R2 = Shuddha Gandharam G1 | 4 Shatshruti Rishabham R3 = Sadharana Gandharam G2 | 5 Antara Gandharam G3 | 6 Shuddha Madhyamam M1 | 7 Prati Madhyamam M2 | 8 Panchamam Pa | 9 Shuddha Dhaivatam D1 | 10 Chatushruti Dhaivatam D2 = Shuddha Nishadam N1 | 11 Shatshruti Dhaivatam D3 = Kaisiki Nishadam N2 | 12 Kakali Nishadam N3 (F, standard scheme).
- Sa and Pa are fixed (achala); the rest have variants. The drone sounds Sa and Pa (or Sa and Ma), so intonation is judged against it (E).
- Western mapping with Sa = C: R1 Db, R2 D, R3 Eb, G3 E, M1 F, M2 F#, Pa G, D1 Ab, D2 A, D3 Bb, N3 B. Just intonation differs slightly from equal temperament; AI tools output equal temperament (E, U).

## 2. Choosing the tonic (kattai)
- Kattai numbers the sruti by harmonium key counted from C: 1 = C, 1.5 = C#, 2 = D, 2.5 = D#, 3 = E, 4 = F, 4.5 = F#, 5 = G, 5.5 = G#, 6 = A, 6.5 = A#, 7 = B (F, teacher and forum consensus; there is no 3.5 or 7.5 because E to F and B to C are single semitones).
- Principle: pick the sruti so the singer sits in the comfortable speaking-voice zone and can reach the upper Sa and the lower Pa (E). It is a comfort choice, not a fixed rule.
- Typical (E, approximate): male roughly 1 to 3 kattai (C to E; many concert male voices near 1 to 2.5); female roughly 4 to 6.5 (F to A#; many near 4.5 to 5.5). The female number is not "an octave below" the male one: 5 kattai is G, which is the Pa of 1 kattai (F). Sources disagree: one academy page gives different ranges and mislabels C# as 1 kattai, so treat any single chart as U.
- Voices differ: a baritone may sit at 1, a light tenor at 3, a deep alto at 3.5 to 4; boys before voice break and high male voices can use female-range kattai. Mixed or duet sessions often compromise near 2 to 2.5 or 4 (E).
- Instruments follow the singer: violin and flute are tuned to the singer's Sa; mridangam and ghatam are tuned to Sa (F). Nadaswaram is a fixed-pitch instrument: the long bari type is reported near 2 kattai and the short timiri near 7 (F per carnatica.net and Wikipedia, U on exact values).
- Brief wording: "Sa at D (2 kattai), male voice, tambura on Sa and Pa". Always state Sa as a Western letter plus kattai.

## 3. Gamaka: why Carnatic sounds human
- A raga lives in its gamakas; the bare scale gives only a skeleton (F). A note is rarely a flat pitch; it is a shaped movement towards, around or away from a target pitch, with controlled speed, width and timing (E). This continuous micro-variation, tied to breath and phrase shape, is what the ear reads as a living voice; flat, quantised or evenly vibrated notes read as machine (E).
- Common types (definitions vary by source and school, U on precision; the classical list has fifteen, "panchadasa"):
  - Kampita: oscillation on a note, varying in speed, width and repeats; resembles vibrato only on the surface; its shape is raga-specific (F).
  - Jaru: smooth slide, rising (arohana) or falling (avarohana) (F).
  - Nokku: stress on a note from above on successive tones; its pair, odukkal, stresses from below (F).
  - Sphurita: a rebound, touching a neighbour and returning; another definition is stress on repeated tones (F, definitions differ).
  - Orikai: a brief flick at the end of a note to a higher tone (F).
  - Others (E): andolita (slow wide swing around a note), pratyahata (strike and return), ravai (quick cluster around one note), khandippu (a clipped, cut note), ullasita (rising lift).
- Raga-specific signature (E): Todi and Kalyani gandhara, Kambhoji and Sahana kampita, Bhairavi ri and dha oscillations. A raga without these sounds wrong to a listener.
- Instruments: voice, violin, veena, flute and nadaswaram render gamakas natively; mridangam and ghatam are tuned percussion; harmonium, piano and keyboards cannot bend pitch (see `heritage-instruments.md`).
- AI prompt vocabulary: "heavy gamaka ornamentation", "slow oscillating kampita on held notes", "smooth jaru glides between notes", "slides into notes from below", "grace-note flicks at phrase ends", "microtonal bends, not piano-like", "breath-shaped phrasing". Negatives: "no straight grid-quantised pitch, no auto-tune, no Western vibrato wobble". Tools approximate gamakas weakly (U): test a 15 s sketch and have a reviewer listen.

## 4. Raga structure
- Arohana: ascending scale; avarohana: descending scale; they may differ in notes and order (F). Vakra ragas zigzag; audava has 5 notes, shadava 6, sampurna 7 (F).
- Melakarta (janaka): 72 parents with all 7 notes, same up and down. Janya: derived ragas using a subset or altered order (F). Detail and katapayadi in `indian-and-tamil-music.md` section 2.
- A raga is also defined by nyasa (rest notes), jiva or graha swara (life and start notes), characteristic phrases (pidi), emphasis and gamaka (E).
- Time-of-day association is strong in Hindustani and looser in Carnatic, where concerts mix ragas freely (E). Treat time as colour, not law.

## 5. Twenty-five common ragas (E, traditional and subjective)
| Raga | Mood | Time (loose) | Typical film or ad use |
|---|---|---|---|
| Mohanam | bright, graceful, open | evening | feel-good ads, hero intro, lullaby, devotion |
| Kalyani | auspicious, grand, uplifting | evening | wedding, festive reveal, aspirational ad |
| Hindolam | gentle, meditative, yearning | late night, dawn | calm scene, wellness, reflective montage |
| Sivaranjani | longing, pathos | night | separation, sad romance, memory |
| Kapi | tender, light, pathos | late evening | romance, light classical, nostalgia |
| Bhairavi | deep devotion, pathos | any, concert closer | emotional climax, prayer, farewell |
| Sankarabharanam | noble, stable (major-like) | any | dignified opening, family warmth |
| Kharaharapriya | compassionate, warm | any | soulful melody, emotional duet |
| Hamsadhwani | festive, bright | auspicious opening | event start, launches, fanfare |
| Madhyamavati | peaceful, closing | evening, concert end | calm resolve, end card |
| Shanmukhapriya | dramatic, intense | any | conflict, heavy emotion |
| Abhogi | soft, dreamy | night | lullaby, intimate, sleep |
| Natabhairavi | sad, serious (natural minor) | night | sorrow, Western-minor crossover |
| Charukesi | bittersweet, tender | morning to evening | romantic longing, nostalgia |
| Reethigowlai | heartfelt, plaintive | evening | earnest pleading, emotional lines |
| Todi | serious, dark, grave | morning (Hindustani cousin) | gravity, dramatic reveal, solemnity |
| Mayamalavagowla | devout, steady, serious | early morning | dawn ritual, first lessons, morning routine |
| Anandabhairavi | tender, soothing, motherly | evening | lullaby, comfort, reassurance |
| Kambhoji | rich, grand, expansive | evening | sweeping scene, expressive devotion |
| Begada | graceful, joyful, smiling | evening | light romance, elegant brand film |
| Bilahari | cheerful, fresh | morning | bright morning, playful energy |
| Saveri | pathos, sincere, quiet | early morning | pensive dawn, humble devotion |
| Sahana | intimate, tender, sweet | late night | heartfelt confession, soft romance |
| Revathi | serene, tranquil | late night | night calm, sleep, spa and wellness |
| Natakurinji | melancholic, wistful | night | quiet sadness, longing (U) |
Rule: pick the raga for emotion, then instrument and tala for setting. In AI prompts also state the notes in words (`indian-and-tamil-music.md` section 10). Parentage and exact note sets for ragas not in the base file are U: verify with a reviewer.

## 6. Tala system
- Suladi sapta tala: 7 parent talas (Dhruva, Matya, Rupaka, Jhampa, Triputa, Ata, Eka), built from laghu (finger-count, length set by jati), dhrutam (clap and wave, 2 counts) and anudrutam (clap, 1 count) (F).
- Five jatis change only the laghu: tisra 3, chatusra 4, khanda 5, misra 7, sankirna 9. 7 talas x 5 jatis = 35 talas (F).
- Five nadais or gatis (how each beat subdivides: 3, 4, 5, 7, 9). 35 x 5 = 175 talas (F). Some sources multiply further by 3 speeds and the totals disagree (U).
- Common: Adi = chatusra-jati Triputa, 8 beats (4+2+2). Rupaka = dhrutam plus laghu, 6 beats in chatusra jati (3 in the tisra-gati film sense). Misra chapu = 7 beats, usually felt 3+2+2 (some schools write 3+4, U). Khanda chapu = 5 beats, 2+3. Tisra chapu = 3 beats (E). Chapu talas stand outside the 35 and are counted by beat groups (F).
- Film simplification (E): adi becomes 4/4; rupaka 6/8 or 3/4; misra chapu 7/8; khanda chapu 5/4 or 5/8; tisra gati reads as triplet or 12/8.
- Nadai in practice (E): tisra nadai gives a lilting triplet pulse, khanda nadai a hiccupping five, misra nadai a seven across the beat. Prompt: "adi tala, chatusra nadai, 90 BPM" or "rolling tisra nadai in 6/8".
- Korvai (muktayam): a fixed rhythmic composition, repeated three times, resolving on the sama (beat 1) of the next cycle (F). Mora: a short cadential phrase repeated three times landing on the sama, often closing a pallavi or korvai (E, U on exact school definitions).
- Eduppu: where a composition starts relative to the sama (before, on, after), a useful cue for a human drummer (E). Syllables are in `rhythm-and-cultural-soundscapes.md`.

## 7. Concert form (kutcheri)
- Varnam: opening piece, structured, warms voice and sets raga; sung in slow, medium and fast passes (E).
- Kriti: the central composition form: pallavi (theme), anupallavi (second part), charanam (closing verses), often with sangatis, graded variations on a line (F).
- Alapana: unmetered raga exploration from low to high, slow phrases opening into richer gamakas; ends before the tala begins (F).
- Tanam: rhythmic but unmetered improvisation, main part of the ragam-tanam-pallavi (E).
- Niraval: improvising on one line of the composition, keeping words and tala, varying the melody (F).
- Kalpanaswaram: improvised swara-name sequences that return to a fixed point of the line (F).
- Thani avartanam: percussion solo, mridangam with ghatam, kanjira, morsing in turn; closes with a korvai and mora (F).
- Ragam-tanam-pallavi (RTP): the main long item. Tillana: rhythmic finale from dance. Devarnama, javali, bhajan, mangalam: light closers (E).
- Typical order (E): varnam, kritis, main raga item with niraval and swaras, thani, light pieces, tillana, mangalam. A 15 to 30 s ad uses a miniature: a short free-time alapana feel, a pallavi-style hook, a mora-like cadence.

## 8. Manodharma (improvisation)
- Manodharma is the performer's creative improvisation inside raga and tala rules: alapana, tanam, niraval, kalpanaswaram, pallavi (F, E). It is learned within a framework, not free jazz (E).
- Marks of good manodharma (E): stays inside the raga, builds slowly from note centres, repeats and varies, shows the raga's gamaka signature, resolves on the target note on time.
- For AI: "improvised alapana, free time, slow breath-length phrases, no beat" for an intro, then "metred pallavi" for the body. Label as AI draft; a human vidwan or vidushi records finals.

## 9. Production notes
- Open with an unmetered alapana over tambura, then enter the tala; this lets the gamaka show.
- Do not auto-tune melodic lines; keep natural pitch drift; vocals and violin forward, fairly dry, short warm hall reverb.
- Standard ensemble (E): vocal, violin, mridangam, ghatam or kanjira or morsing, tambura. Stay close to it for authenticity; see `heritage-instruments.md`.
