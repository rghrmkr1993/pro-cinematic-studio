---
name: music-and-sound
description: "Professional music, score, jingle, sound design and mixing for any project: music briefs, tempo, key, raga and instrumentation, AI music prompting (ElevenLabs Music v2.5, ElevenLabs sound effects, Higgsfield audio tools), briefing human composers and musicians, film scoring and spotting, Foley and ambience, mixing, loudness (LUFS, true peak, ffmpeg loudnorm), Indian, Carnatic and Tamil film music, global genres by decade, and rights rules. Load for any request to create, direct, prompt, brief, score, mix or QA music, a song, a jingle, a soundtrack, SFX or ambience."
license: MIT
user-invocable: true
metadata:
  version: "1.0"
  built: "2026-10-13"
---
Part of the cinematic pipeline: entry point creative-studio


# Music and sound (studio skill)

Owner: creative-director (intent, brief), fullstack-engineer (stems, ffmpeg), qa-tester (loudness, sync), tech-writer (licence log). Labels: F fact (sourced), E estimate, U unverified, 3P third party and changing fast. Not legal advice.

Do not duplicate these, link to them:
- Sound plan, stems, dubbing, AI music licensing, loudness table by platform: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md`
- ElevenLabs tool names, voice rules, credit gate: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/elevenlabs.md`
- ffmpeg loudnorm two-pass, final QC: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/editing-and-assembly.md` section 4
- Voice accents and Indian speech: `${CLAUDE_PLUGIN_ROOT}/skills/asian-human-reference/references/speech-and-voice.md`

## 1. Router (open ONE reference, not all)
| Need | Open |
|---|---|
| Melody, chords, scales, meter, BPM per mood, song forms, hooks, motifs | `references/theory-and-tune.md` |
| Genre or decade sound (lofi, EDM, hip-hop, jazz, K-pop, Afrobeats, 1950s to 2020s) | `references/genres-and-generations.md` |
| Carnatic, Hindustani, Tamil folk, devotional, Tamil and other Indian film eras | `references/indian-and-tamil-music.md` |
| Which instrument, range, timbre, AI wording | `references/instruments.md` |
| Score, spotting, stingers, ad music 6s, 15s, 30s, scoring per genre | `references/film-scoring.md` |
| Ambience, Foley, whooshes, risers, SFX prompts, Indian ambiences | `references/sound-design-and-foley.md` |
| Gain, EQ, compression, ducking, stems, loudness, ffmpeg | `references/mixing-and-mastering.md` |
| Writing the actual prompt, lyrics block, takes, credits | `references/ai-music-prompting.md` |
| Carnatic depth: sruti, kattai, gamaka, 25 ragas, tala, concert form, manodharma | `references/carnatic-deep.md` |
| Heritage instruments in depth (ghatam to parai), pairings, mixing, cultural care | `references/heritage-instruments.md` |
| Western orchestra ranges, articulations, East-West film fusion | `references/western-instruments-deep.md` |
| Voice types, registers, vibrato vs gamaka, Tamil diction, singer technique vocabulary | `references/vocal-craft.md` |
| Tamil rhythm by occasion, ambience layers, solkattu | `references/rhythm-and-cultural-soundscapes.md` |
| Where a claim came from | `references/sources.md` |
Voice work (singers, voiceover, TTS): `${CLAUDE_PLUGIN_ROOT}/skills/voice-studio/SKILL.md` plus `references/vocal-craft.md`.
Typical chains: jingle = film-scoring (ad part) + ai-music-prompting + mixing. Film cue = film-scoring + theory + ai-music-prompting. Tamil song = indian-and-tamil-music + theory + ai-music-prompting. Visual side of a music video: `10-music-video` and `higgsfield-master`.

## 2. Music brief template (fill before any generation or commission)
```
MUSIC BRIEF  id: MUS-<project>-<nn>   owner:   date:
1. Purpose: where it plays (ad, film cue, app, reel, podcast bed), what it must do for the viewer
2. Emotion arc: start feeling > turn > end feeling, with timestamps (0-5s curious, 5-12s lift, 12-15s resolve)
3. Tempo: BPM (or range), feel (straight, swing, half-time), meter (4/4, 3/4, 6/8, 7/8)
4. Key or mode, or raga + tala (E.g. D minor; or Mohanam, adi tala). Mood words, not only labels
5. Instrumentation: lead, harmony, rhythm, bass, texture; what to EXCLUDE
6. Vocal type: none, hum, choir, solo (range, tone, age feel), spoken. No named real artists
7. Language and script: Tamil, Hindi, English, none; native-speaker reviewer named
8. Length: exact seconds or bars; loop needed yes or no; cutdowns (30, 15, 6 s); sting needed
9. Sync points: list of timecodes or bars that must hit (logo reveal 11.5 s, cut at 6.0 s, silence 9-9.5 s)
10. Loudness target and format: platform from sound-music-voice.md section 8; 48 kHz 24-bit WAV; stems yes or no
11. Reference: describe sound, era or feel in words; no song names, no artist names
12. Rights path: commissioned, library, AI (tool, plan, licence snapshot), cue sheet owner
13. Budget: credits cap and number of takes allowed; approval gate (who says yes)
```
For a human musician add: reference clips described in words, a click or tempo map, key, chord chart or lead sheet if known, delivery spec, deadline, revision count, usage and buyout terms in writing, credit line. See `film-scoring.md` section 9.

## 3. AI music prompt formula
`[Genre + era] + [mood] + [BPM + key or raga] + [lead instrument + support + rhythm] + [vocal or none] + [language] + [structure with lengths] + [mix feel] + [avoid]`
Example (instrumental, 15 s, original wording): "Warm acoustic pop with a tiny electronic pulse, hopeful and fresh, 108 BPM, G major, plucked guitar lead, soft claps, light bass, airy pad, no vocals, 2 s intro, 10 s lift, 3 s clean ending on the tonic, dry intimate mix, no harsh cymbals, no drops."
Rules: name purpose and mood first; one genre blend at most; BPM in numbers; end instruction for any short cue ("clean ending, no fade"); negatives as a short list; build long songs section by section and prove the idea first. Full detail and the ElevenLabs composition plan fields: `references/ai-music-prompting.md`.

## 4. Tool notes (3P, verify live, 2026-10-13)
- DEFAULT (field test 2026-10-13, owner judgement): AI for instrumentals, BGM, SFX, drafts and guide tracks. Human Tamil singer or voice artist for final vocals and voiceover (hybrid recipe: `ai-music-prompting.md` section 8). Tested and judged robotic: ElevenLabs Music v2.5 Tamil vocals (15 s male solo, 15 s duet) and ElevenLabs Tamil TTS (`eleven_v4`, `eleven_v3` with direction tags). Re-test when new models ship.
- ElevenLabs Music: models `music_v2` and `music_v2_5` (F, docs); 3 s to 10 min; docs name English, Spanish, German, Japanese vocals as examples; Tamil vocals fail the field test above. Export is MP3, 44.1 kHz, 128 to 192 kbps (F). Advertised price 900 credits per minute per variation (3P); owner working figure about 900 credits for a short take: confirm the price shown before each run and wait for the user's yes (elevenlabs.md rule 1).
- ElevenLabs sound effects: model `eleven_text_to_sound_v2`, up to 30 s, loop option, prompt influence 0 to 1 (default 0.3) (3P docs summary).
- Higgsfield audio: voice, voice change, dubbing, lipsync (F, elevenlabs.md); a standalone music or SFX generator is not confirmed (3P conflict, Oct 2026): treat music and SFX there as bundled, test first.
- Self-serve ElevenLabs plans are reported to exclude film, television and studio games for commercial use (3P): read Music Terms before any film or OTT use.

## 5. QA checklist (all must pass; log in the delivery note)
- QA note 2026-10-13: any AI Tamil vocal or Tamil TTS in a final fails QA unless the owner approves it by ear; swap in a human take (hybrid recipe).
- Brief fields 1 to 13 filled; take matches purpose and arc; ending lands where the sync list says
- Tempo within 2 percent of brief; key or raga correct by ear or by a named musician (Carnatic: reviewer)
- No lyric or melody resemblance to any known song (listen; run a similarity check where the tool allows)
- No named artist, song or lyric in the prompt; prompt saved with tool, model, date, plan, credits spent
- No clipping; true peak under ceiling after final encode; loudness measured and logged
- Dialogue stays intelligible with the bed under it (music 12 to 20 dB below dialogue peaks is a start, E)
- Loop points clean; no pops at cuts; stems labelled; 48 kHz 24-bit master kept
- Vocals: no robotic artefacts, no swallowed words, pronunciation checked by a native reviewer
- Cue sheet and licence snapshot filed; AI disclosure note written; temp music removed
- Checked on phone speaker, laptop, headphones

## 6. Rights rules (non-negotiable)
1. No copyrighted lyrics or melodies, ever: not pasted, not paraphrased closely, not hummed back. Never ask a tool to continue, remix or imitate a specific song.
2. No named real-artist voice imitation or soundalike, in prompts or in voice settings. ElevenLabs Music Terms prohibit artist names, song titles and recognisable lyrics as input (3P report, verify).
3. "In the style of an era or genre" is fine ("1970s orchestral folk-fusion film song feel"). Never a specific song, album or artist.
4. A raga, a scale, a tala and a chord progression are building blocks, not owned. A specific composed tune is owned. Keep a human check that the result is not a near copy.
5. Licence: use paid tiers with a written commercial licence; snapshot the terms page and invoice; check territory, term, media (film and OTT may be excluded). Library and commissioned music for hero themes. Existing songs need sync plus master licence.
6. AI disclosure: label AI-generated music or voices where the platform, broadcaster or OTT requires it; note it in the delivery note. In the US AI output with no human authorship is not copyrightable (sound-music-voice.md section 6): add human composition or editing for hero themes.
7. Voice: no cloning without written consent; no synthetic voice for a real customer, doctor or expert quote.
8. Human musicians: written agreement on fee, usage, credit and buyout before work; session players and singers consent to any AI use of their recordings.
9. Confidential scripts, unreleased products and customer data are not uploaded to a music tool without approval.

## 7. Workflow (one line each)
Brief > references described in words > prove idea with 1 short take > review against checklist > extend or commission > stems > mix > loudness > QA > cue sheet and licence log > deliver. Spend gate: quote credits, wait for yes.
Hybrid recipe for vocals: AI instrumental plus guide track (marked GUIDE) > human singer brief (key, tempo, lyrics in script plus phonetic line, delivery spec, terms) > human sings over the AI or a re-recorded instrumental > mix > loudness and QA. Same for voiceover.

## 8. Authenticity checklist for Indian music (run before any Carnatic, Tamil or folk cue ships)
1. Sruti: Sa stated (Western letter plus kattai) and suits the voice (male about 1 to 3, female about 4 to 6.5, E); drone present on Sa and Pa.
2. Gamaka: the raga's signature ornaments are present; no flat grid pitch, no auto-tune on melodic lines.
3. Raga fits the mood and time-of-day colour (carnatic-deep.md section 5); notes written in words in the prompt; reviewer confirms.
4. Instrument pairing matches tradition (nadaswaram with thavil; voice with violin and mridangam; parai with thappu); no harmonium on a serious Carnatic concert cue.
5. Tala and nadai correct and counted (adi 8, rupaka, misra chapu 7, khanda chapu 5); the sama lands on resolution.
6. Form fits (alapana then pallavi, or kriti sections); sangati-style repeats build; a mora or korvai cadence if the ending is rhythmic.
7. Tamil diction: kuril and nedil lengths, retroflex and zha handled by a native singer; no TTS vocal in a final.
8. Occasion respected: auspicious and funeral instruments not swapped; oppari and urumi melam not used as colour; parai and thappu credited and consulted.
9. No named artist, song or lyric; technique vocabulary only; no voice cloning.
10. Human check: a Carnatic or folk reviewer signs off hero cues; stems, kattai and licence logged.
