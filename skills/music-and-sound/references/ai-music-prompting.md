# AI music prompting (ElevenLabs Music v2.5 first)

Labels: F from ElevenLabs docs, E craft estimate, 3P third-party test reports, FT field test by the studio. Tool names and spend gate: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/elevenlabs.md`. Licensing and AI-disclosure: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md` section 6 and SKILL.md section 6.

## 0. Field test result (2026-10-13, owner judgement) and default policy
- Tested: ElevenLabs Music v2.5 Tamil vocals (a 15 s male solo and a 15 s duet); ElevenLabs Tamil TTS with `eleven_v4` and `eleven_v3` using direction tags.
- Result (FT): the owner judged all of these robotic and AI-sounding. They are not final-quality for Tamil vocals or Tamil voiceover.
- DEFAULT from now on: AI for instrumentals, BGM, SFX, drafts and guide tracks. A human Tamil singer or voice artist for final vocals and final voiceover. This is a hybrid workflow (section 8).
- Re-test when new models ship (a model release, a Tamil-specific vocal update). Log the date, model, prompt, take count, and the owner's verdict in the asset log; update this section.
- Other languages (English, Spanish, German, Japanese vocals are the doc-listed ones, F) may be acceptable for drafts; still judge by ear, and use a human for hero vocals.

## 1. Fact base (F, docs, 2026-10-13)
- Models `music_v2` (default in the interface) and `music_v2_5` (most advanced: better audio quality and prompt adherence). Length 3 s to 10 min. Audio reference up to about 30 s (screened for copyright, guides sound, instruments, tempo, mood; it does not copy).
- Composition plans (API): an ordered list of chunks; each chunk has `text` (lyrics, led by a bracket tag like `[Verse]`), `duration_ms`, `positive_styles`, `negative_styles`, `context_adherence`. Text prompt is for quick prototyping; plans are for exact structure, lyric timing and complex arrangements. A third-party listing says up to 30 sections (3P).
- Export MP3, 44.1 kHz, 128 to 192 kbps; higher fidelity on higher plans. Upsample and master from this; for final audio get stems or a human re-record.
- Vocals need an explicit lyrics instruction (Custom lyrics with a clear vocal prompt); Automatic lyrics produced instrumentals in a 3P test.
- Reported price 900 credits per minute per variation (3P); a 30 s custom-lyrics track cost 450 credits; section regeneration costs more than the share of length suggests (3P). The owner's working figure is about 900 credits for a 15 s take: price shown on screen is the truth, confirm it before each run.
- Terms (3P report, verify): do not use artist names, song titles or recognisable lyrics as input; self-serve plans exclude film, TV and studio games for commercial use.

## 2. Prompt structure
`Genre (+era) > mood > BPM > key or raga > instruments (lead, support, rhythm) > vocals (type, language, delivery) > structure (tags with seconds) > production feel > avoid`
Example (instrumental 30 s): "Warm Tamil-folk-meets-lofi instrumental, tender and nostalgic, 82 BPM, D Dorian. Bamboo flute lead, fingerpicked nylon guitar, soft tabla loop, warm sub bass, tape-saturated pad. Structure: [Intro 0-4 s: flute alone] [Verse 4-14 s: add guitar and tabla] [Lift 14-24 s: add pad, flute rises] [Outro 24-30 s: clean tonic ending]. Dry intimate mix. No vocals, no drums fills, no sudden drops."
- Describe the sound, never an artist or song.
- BPM as a number; key or mode named; one genre plus one flavour.
- Add "clean ending on the tonic, no fade" for short cues and loops: "seamless loop, same chord at start and end".
- Negatives in `negative_styles` or "no X" lists: harsh cymbals, vocals, EDM drops, autotune.
- Describe section by section (intro, verse, chorus, breakdown, outro); build the intro first, prove it, then extend.

## 3. Structure tags and lyrics block
- Tags in brackets before each lyric section: `[Intro]` `[Verse]` `[Pre-Chorus]` `[Chorus]` `[Bridge]` `[Outro]`; third-party guides also use braces for direction like `{soft piano intro}` (3P, not in ElevenLabs docs I read: test before relying).
- Lyrics block: plain text under the tag; one idea per line; 6 to 10 syllables per line is easy to sing (E); avoid long compound words.
- Original lyrics only (own words or commissioned and owned). Never paste existing song lyrics. Never ask the tool to continue a known song. Native reviewer for every language.
- Instrumental drafts: put "instrumental, no vocals" or leave lyrics empty with Custom mode and say no vocals.

## 4. Tamil lyric tips (E; for guide tracks and human singers)
- Syllable fit: Tamil is syllable-based (short kuril and long nedil vowels). Count syllables per line and keep them equal across verses; match the bar: 8 or 16 syllables per 4/4 bar at 8th or 16th feel. Note length: stress and long vowels fall on strong beats.
- Singable vowels: open vowels (aa, ae, o) sustain well on held notes; end lines with a long open vowel or a nasal (m, n); avoid ending held notes on hard consonants or retroflex stops. The Tamil retroflex "zh" (ழ) and the rolled r are hard for models and for pace; place them off long notes.
- Write in Tamil script; add a phonetic Latin line beside it for the singer and for a model test. Colloquial (spoken) Tamil sings more naturally than formal literary Tamil for pop; poetic Tamil for devotional or classical.
- Keep lines short; use repetition (hook phrase repeated); rhyme by ending sound (edugai) and alliteration (monai) in the Tamil tradition (E).
- Reviewer: a native Tamil lyricist or singer checks meaning, scansion, register, regional accent (Chennai, Coimbatore, Madurai), and taboo words.
- Tanglish lines mix English and Tamil; keep the switch at phrase boundaries.

## 5. Avoiding robotic vocals (E; and the reason for the hybrid default)
- Symptoms: even timing, flat vibrato, blurred consonants, no breath, repeated phrase shapes, mispronounced Tamil syllables.
- Mitigations for drafts: lower density (fewer words), longer notes, simple tune, a human-sounding style word ("breathy, intimate, close-mic, slight imperfect timing"), allow rests and breaths, avoid fast patter, avoid too many layers, ask for solo not stacked, use a narrower range, add reverb in the mix, EQ presence and de-ess.
- Honest limit: for Tamil, none of these fixed the artifacts in the 2026-10-13 field test (FT). Do not spend credits trying to polish. Use a human singer for finals (section 8).

## 6. Takes strategy
- Prove the idea with 1 take: shortest length that tests the idea (a 15 s sketch), one variation. If the idea works, extend. If not, change the prompt, not the count.
- Never bulk-generate variations before the first take passes review. Regenerate a section rather than a whole track when only one part fails.
- Log each take: id, model, prompt, plan, credits, verdict (keep, reject, reason).
- Keep the best take and the prompt; derive loops and cutdowns by editing, not by regeneration.

## 7. Credit discipline
1. Estimate credits from the on-screen price (docs: hover on credits) and tell the user; wait for the yes (elevenlabs.md rule 1).
2. Set a cap per brief (for example 3 takes or N credits). When the cap is reached, stop and report.
3. Prefer short test takes (15 s). 900 credits per 15 s means 10 takes is a large spend; plan before you generate.
4. Reuse: stems for reuse (extra credits), loops by editing.
5. Free plans are not commercial (F per product page via 3P): do not ship them.
6. Compare tools per language only on the same short script.

## 8. Hybrid workflow recipe (human final vocals)
1. Brief (SKILL.md section 2): raga or key, BPM, form, language, lyrics (original), length, sync points.
2. AI instrumental and guide: generate the instrumental and a guide track (AI melody and scratch vocal if useful) with 1 take. The guide is for communication only, not for release; mark it GUIDE.
3. Human singer brief: send the guide track and a one-page note: key (Sa pitch), tempo, lyrics in Tamil script plus phonetic line, melody notes or lead sheet if known, mood words, range, where the breaths are, pronunciation notes, delivery spec (dry vocal, 48 kHz 24-bit WAV, 3 takes plus comps, room tone), fee, credit, usage terms in writing, AI-use consent clause for the recording.
4. The human sings over the AI instrumental, or over a re-recorded instrumental if the AI bed is thin or the licence is unclear for the use. Ask for a clean dry vocal and ad-libs.
5. Edit: comp the best takes, tune lightly if the singer agrees, align to picture or bar grid.
6. Mix (`mixing-and-mastering.md`): vocals first, bed under; de-ess; reverb; check mono; ducking under dialogue if needed.
7. Loudness and QA (SKILL.md section 5): measure, true peak, cue sheet, licence snapshot, AI-disclosure note for any AI-generated parts.
8. Same for voiceover: AI TTS for scratch and timing; human Tamil voice artist for the final read; native review.
Cost note: a short human session is usually cheaper than many failed AI takes and carries no robotic risk (E).

## 9. Higgsfield and other tools
Higgsfield has voice, voice change, dubbing, lipsync; a standalone music or SFX generator is not confirmed (3P, Oct 2026). Use it for lipsync and voice-change, not as the music engine, until tested. Suno or Udio type tools: see sound-music-voice.md section 6 for licensing risk.

## 10. Prompt log template
`Date | Brief id | Tool and model | Prompt (saved text) | Duration | Credits | Take verdict | Human review | Licence plan and snapshot | Next step`

## Field test 2 (2026-10-13): what improved Tamil singing
Owner rated this "better": colloquial spoken-style Tamil lyrics, slow tempo (78 BPM), few words per line, long held vowels, "warm natural intimate breathy" vocal, sparse acoustic bed (guitar, flute, shaker). Poetic formal lyrics + dense 80s orchestration sounded robotic. Default recipe for Tamil AI songs uses these traits.

## 11. Carnatic and heritage prompt vocabulary (added 2026-10-14; test each on a 15 s sketch; ragas are weakly respected, U)
Combine with the formula in SKILL.md section 3. Add scale notes in words and the Sa pitch. Never name an artist or song.
1. "Carnatic-inspired instrumental, Sa at D, tambura drone on Sa and Pa, free-time alapana intro, then adi tala at 80 BPM"
2. "heavy gamaka ornamentation, slow kampita on held notes, smooth jaru slides, no straight grid pitch"
3. "Mohanam-like pentatonic scale (Sa Ri Ga Pa Da), bright and graceful, bamboo venu flute lead"
4. "Hindolam-like scale (Sa Ga Ma Da Ni), gentle and meditative, veena and soft mridangam, 66 BPM"
5. "Bhairavi mood, deep devotional pathos, Carnatic violin, slow rubato phrases"
6. "Kalyani-like Lydian raga feel, auspicious and grand, nadaswaram and thavil, wedding celebration, 120 BPM"
7. "periya melam ensemble, paired nadaswaram, thavil rolls, bronze talam cymbals, temple courtyard reverb"
8. "mridangam with ghatam and kanjira, thani avartanam feel, fast korvai ending on the downbeat"
9. "Saraswati veena, warm plucked gamakas, soft sustain, devotional hall reverb"
10. "Carnatic violin sliding between notes, long bows, vocal-like, no Western vibrato"
11. "tisra nadai triplet pulse in 6/8, kanjira and mridangam, lilting"
12. "misra chapu 7 beat feel, 3 plus 2 plus 2, light percussion, folk-classical"
13. "parai and thappu folk beat, raw stick hits, fast rolls, village festival, celebratory, 118 BPM"
14. "kuthu dance beat, parai and thappu with electronic drums, crowd chant, high energy, 130 BPM"
15. "gaana street rhythm, tin and thappu percussion, call and response chorus, witty and raw, 100 BPM"
16. "villupattu bow-song feel, udukku and ghatam, chorus echo, storytelling pace"
17. "harvest Pongal celebration, kolattam clacks, parai, kummi claps, cattle bells, joyful"
18. "string section answers a nadaswaram phrase, thavil and drum kit, Tamil film orchestral fusion"
19. "1980s Tamil film orchestral-folk fusion, flute counter-melody, string runs, folk drum groove, warm analog synth"
20. "temple town morning ambience, distant nadaswaram, bells, crows, bicycle bells" (SFX tool)
Avoid: "authentic" alone, raga names without notes, funeral instruments for joyful briefs, harmonium on a strict Carnatic cue. Context rules: `rhythm-and-cultural-soundscapes.md`, `heritage-instruments.md` section E.

## Pricing fact (2026-10-14, workspace estimate)
ElevenLabs Music v2.5 charged a flat 900 credits per generation for both 15s and 40s prompts. Credit tip: ask for the longest useful length (a full verse or duet) in one take, never several 15s clips.
