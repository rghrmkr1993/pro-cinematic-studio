---
name: voice-studio
description: "Make AI and hybrid voice sound genuinely human, especially Tamil and other Indian languages: voiceover, narration, dubbing, TTS, voice cloning, speech-to-speech, singing, and hiring voice artists. Covers ElevenLabs v3 and v4 settings, audio tags, pronunciation, Voice Design, Sarvam Bulbul, IndicF5, Google, Azure, Cartesia and other Tamil options, spoken-Tamil script writing, take selection and splicing, ffmpeg humanising (room tone, reverb, EQ, de-essing, breaths), a decision tree (AI vs speech-to-speech vs clone vs human artist), a naturalness score, a credits ladder, and consent, personality-rights and disclosure rules. Load when a voice sounds robotic or before any voice job."
license: MIT
user-invocable: true
metadata:
  version: "1.0"
  built: "2026-10-13"
---
Part of the cinematic pipeline: entry point creative-studio


# Voice studio (human-sounding voice, Tamil first)

Owner: creative-director (casting, direction), fullstack-engineer (ffmpeg, pipelines), qa-tester (naturalness score), tech-writer (consent and licence log). Labels: F fact (sourced in references/sources.md), E estimate, U unverified, 3P third party and changing fast. Not legal advice.

Do not duplicate, link to:
- ElevenLabs tool names, voice rules, credit gate: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/elevenlabs.md`
- Sound plan, stems, dubbing flow, loudness table: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md`
- Mixing, ducking, loudnorm, Indian and Tamil music, AI music prompts: `${CLAUDE_PLUGIN_ROOT}/skills/music-and-sound/SKILL.md`
- Vocal craft (voice types, registers, vibrato versus gamaka, Tamil diction, technique vocabulary, never imitate a named singer): `${CLAUDE_PLUGIN_ROOT}/skills/music-and-sound/references/vocal-craft.md`
- Indian accents, honorifics, code-switching: `${CLAUDE_PLUGIN_ROOT}/skills/asian-human-reference/references/speech-and-voice.md`
- Indian-language script, phonology, dialect, lipsync and subtitles per language (Tamil, Telugu, Malayalam, Hindi, Kannada, Indian English): `${CLAUDE_PLUGIN_ROOT}/skills/indic-languages/SKILL.md`

## 1. Why AI Tamil sounds robotic (diagnose first)
Ranked by how often it is the real cause (E, from the research in references/sources.md):
1. Script is written Tamil (செந்தமிழ் / news register), not spoken Tamil (பேச்சுத் தமிழ்). Engines follow the text; a formal script gives a news-reader delivery (3P, vendor guides).
2. One long, flat generation: no choice of takes, no phrase-level splicing.
3. Over-stable settings, or a voice that is not native to Tamil (accent leaks, flat pitch).
4. Dry, sterile output with no room tone, no breath, no mix context.
5. Emotion left to the model instead of written into the lines and directed with a few tags.
6. Pronunciation errors in brand, English and number words.
Singing has an extra limit: ElevenLabs Music docs name English, Spanish, German and Japanese for vocals; Tamil is not documented (F), so treat Tamil vocals as U until a test passes (references/hybrid-and-human-artists.md).

## 2. Router (open ONE reference)
| Need | Open |
|---|---|
| ElevenLabs v3 or v4 settings, tags, pronunciation, Voice Design, cloning, STS, failure fixes | `references/elevenlabs-advanced.md` |
| Which tool for Tamil or another Indian language, licence, price | `references/indian-language-tts-options.md` |
| Writing the script, spoken Tamil examples, numbers, punctuation | `references/script-for-voice.md` |
| Post-processing, ffmpeg recipes, room tone, breaths | `references/humanize-post.md` |
| Guide performance, speech-to-speech, hiring Tamil artists, singing | `references/hybrid-and-human-artists.md` |
| Consent, personality rights, disclosure, celebrity rule | `references/voice-ethics.md` |
| Sources, dates, conflicts | `references/sources.md` |

## 3. Decision tree: which route?
Answer in order; stop at the first match.
1. Is the voice a real person's (founder, actor, singer)? Yes: written consent first (voice-ethics.md). Then a clone made with that person, or that person records.
2. Is it a hero line (brand film, TV or OTT ad, emotional scene, any singing)? Quality bar is broadcast. Budget available: human artist, final recorded (hybrid-and-human-artists.md). Budget tight: human guide performance plus speech-to-speech, then polish.
3. Can a person perform the lines (staff, friend, an artist for a short session)? Yes: speech-to-speech (STS). It keeps the performer's timing, breath and emotion and swaps only the timbre, often the most natural AI route (F, ElevenLabs docs: keeps whispers, laughs, subtle cues; the multilingual STS model lists 29 languages and Tamil is U, so test first).
4. Volume content (explainers, social, product pages, many languages)? Quality bar is good web. AI TTS with a spoken-Tamil script, take selection and post (sections 4 to 6).
5. Need one consistent branded voice at scale? Consented clone (PVC, or a Sarvam or Fish clone) or a Voice Design voice, locked per brand.

| Quality bar | Low budget | Mid budget | High budget |
|---|---|---|---|
| Internal draft, animatic | AI TTS, no post | AI TTS plus post | n/a |
| Social, web, explainer | AI TTS, spoken script, post | STS from a guide take | Human artist |
| Ad, brand film, OTT, songs | STS from a strong guide | Human artist, light AI fix | Human artist, studio, director |

Always run the same short Tamil test line through 2 or 3 engines (ElevenLabs, Sarvam Bulbul, one more) before choosing; native listeners score blind.

## 4. Naturalness checklist (0 to 2 each, total out of 10)
| Item | 0 | 1 | 2 |
|---|---|---|---|
| Prosody | Flat or sing-song, wrong stress | Mostly fine, a few odd phrases | Natural rise and fall; question and statement tones right |
| Breath and pauses | None, or in wrong places | Some, slightly regular | Breath at clause edges; pauses carry meaning |
| Pace variation | Same speed throughout | Slight change | Quickens on excitement, slows on weight |
| Emotion | Neutral or exaggerated | Right mood, shallow | Mood shifts inside the line, believable |
| Pronunciation | Names or Tamil sounds (ழ, ற, ண) wrong | Minor slips | Native reviewer approves; brand names right |
| Artifacts | Glitches, metallic ring, pitch jumps, clipped ends | Rare, minor | None on headphones and phone |
Gate: 8 or more ships; 6 to 7 re-take or post-fix; under 6 change route (script, voice, or human). Scorers: one native Tamil speaker plus one non-expert listener, blind to the engine. Log the score.

## 5. Credits ladder (never skip a rung; quote the cost, wait for the user's yes)
1. Rung 0, free: rewrite the script in spoken Tamil, native review, write pronunciation notes. No credits.
2. Rung 1: ONE short test line (2 to 3 sentences, about 150 to 250 characters) holding the hardest content: a retroflex word, a number, a brand name, an emotional beat. Run on 2 or 3 voices or engines, 2 takes each.
3. Rung 2: pick the best voice and settings by score. Lock voice ID, model and settings in the log. One more test on the second-hardest line.
4. Rung 3: generate the full script per line (not per scene): 3 to 5 takes for hero lines, 1 to 2 for the rest. Splice, post, score.
5. Rung 4: finals only after the user approves the scored cut. Re-generate nothing that already passed.
Stop rule: if rung 1 scores under 6 on two engines, stop spending and switch to speech-to-speech or a human artist.

## 6. Pipeline in one view
Spoken script with short lines > test line > voice choice > per-line takes > select and splice > clean (EQ, de-ess, compress) > room tone and subtle reverb > breath and mouth detail > mix under music > loudness check > naturalness score > native QA > consent and disclosure notes in the delivery file.

## 7. Hard rules
- Spend: quote first, the user's yes first. No generation while researching or building.
- Consent: no clone, no sound-alike, no celebrity, no deceased voice without documented rights (voice-ethics.md). No fake testimonials.
- Disclosure: label synthetic voice where platform or law requires (India IT Rules amendment 2026, EU AI Act timing; see voice-ethics.md).
- Confidential scripts and unreleased product claims do not go to a free or unvetted service.
- Product claims in voice scripts come only from the approved claims list; regulatory review stays with qualified staff.
- Client-neutral: never reuse one client's voice, script or brand for another.
- Native Tamil review before any final. Mark untested languages and features U.

Field test 2026-10-13: spoken-Tamil script + v3 + one [softly] tag on native voice Thivi = 3 takes for 363 credits; owner moving to ElevenLabs Enterprise (2026-10-14) for API settings, PVC and licensing.
