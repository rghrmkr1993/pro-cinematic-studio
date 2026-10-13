# Hybrid workflows and human voice artists

Labels: F documented, 3P third party, E estimate, U unverified. Rates are ESTIMATES from public marketplace and vendor pages (2026-10-13); get written quotes. Consent and law: voice-ethics.md. Sound plan, stems, dubbing: `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/sound-music-voice.md`. Indian and Tamil music craft: `${CLAUDE_PLUGIN_ROOT}/skills/music-and-sound/references/indian-and-tamil-music.md`.

## 1. Why hybrid wins for Tamil
AI voices handle timbre well but handle performance (timing, breath, emotional intent, regional stress) weakly in Tamil. A human supplies the performance; AI supplies the voice, the language fix, or the retake. The result is often the most natural route short of a full human session (F for STS keeping subtle cues; E for the ranking).

## 2. Workflow A: guide performance plus speech-to-speech (STS)
1. Write the spoken-Tamil script (script-for-voice.md), native reviewed.
2. Pick a performer: staff member, a friend with good Tamil diction, or a paid artist for a 30 to 60 minute guide session. Any gender; the target voice is chosen later.
3. Record dry, close, 48 kHz, 24-bit WAV, in a quiet soft room (section 5). Perform at full emotion, exact words, one line per take, 2 to 3 takes.
4. Test ONE line through STS first (credits ladder rung 1): `eleven_multilingual_sts_v2` (29 languages; Tamil U). Max 5 minutes per segment; set `remove_background_noise=true` if the room is noisy (F).
5. Convert to the chosen library, designed or consented cloned voice. Listen for: guide accent leaking, pitch wobble, swallowed Tamil sounds (ழ, ற), breath loss.
6. Score with the naturalness checklist. If under 6, check the input recording, then try another target voice or go to a human final.
7. Post (humanize-post.md) and mix.
Cost control: STS bills about 1,000 characters per minute of audio (F). A 30 s hero line is cheap; test first, quote, wait for the user's yes.
Rights: the performer signs a release for the guide recording and for the conversion (voice-ethics.md). Using someone's performance as a guide with a different voice still needs their consent for the performance.

## 3. Workflow B: human voice artist for finals
Use for broadcast ads, brand film, OTT, anything with a face or a famous-sounding feel, and all singing.
1. Brief (section 4), audition 3 artists with the same 20 to 30 second script, same direction.
2. Book, send script with pronunciation notes and a reference (a mood reference or the AI scratch version, labelled TEMP).
3. Directed session (live link or in studio), 3 takes per hero line, alternate readings (warmer, faster, quieter).
4. Delivery: dry WAV per line plus a full-read WAV, named per the shot or line ID (film-studio naming: `AUD-S03-SC07-SH020-DLG-T02.wav`).
5. AI roles that remain: AI scratch track for timing and edit, AI fix-ins for one changed word (only if the artist agrees in the contract), AI dubbing into other languages from the human master (needs the artist's consent for any cloning).

## 4. How to brief a Tamil voice artist
Send: client-neutral project name, usage (platform, duration, territory, term), language and region (Chennai, Madurai, Kongu, Jaffna, Tanglish), register (spoken, not formal), character or brand tone (3 adjectives), age range, pace (words per minute or seconds), reference clip, full script with line IDs, pronunciation list (brand, ingredient, English words), emotion arc, delivery spec, deadline, number of revisions, and payment terms.
Direction words that work: warm, close, smiling, tired, curious, confident, whisper-close, shy, cheeky. Avoid "natural" alone; it means nothing. Give a picture ("she is telling a friend at the kitchen table").
Audition rubric: score each artist with the naturalness checklist plus fit (regional accent, tone, diction, clean read, direction response).
Safety: a script with product claims is approved by the client and regulatory staff before recording; the artist does not improvise claims.

## 5. Recording and delivery specs
- File: 48 kHz, 24-bit WAV, mono for voice, no lossy codecs, no processing (no reverb, no noise gate, no auto-tune, no compression), peaks around -12 to -6 dBFS, no clipping (F, film-studio sound standard).
- Room: dry, treated (a padded closet with clothes, or a booth), no fans, AC, fridge, traffic; 10 to 15 cm from a cardioid condenser, pop filter; record 10 s of room tone at the start and end.
- Slate each take with line ID; leave 1 s of silence between takes; mark good takes.
- Provide: dry takes, a selects reel, a clean full read, the room tone, the script with notes, the signed release.
- QC on receipt: peaks, noise floor (under -60 dBFS), mouth clicks, sync to script, correct pronunciation.

## 6. Where to find Tamil artists (3P, check each platform)
- Casting platforms: Voicesbazaar (Gold, Silver, Platinum tiers), Voice123, Voices.com, Voquent (global, filter Tamil).
- Freelance marketplaces: Upwork, Fiverr, Freelancer, Truelancer (budget, quality varies; always audition).
- Local: Chennai dubbing studios and ad-film audio houses; dubbing artists with Tamil film and ad credits; radio and news-presenter circuits; theatre groups (E).
- Ask for a demo reel in spoken Tamil in your tone, not only formal news reading.
- Do not approach a celebrity or famous dubbing artist and ask for a sound-alike; hire them directly under a licence if you want them.

## 7. Rate estimates (E, rough, INR, public listings 2026; confirm in writing)
| Work | Estimate |
|---|---|
| Budget freelance Tamil, marketplace listings | about Rs 70 to 100 per minute; hourly bids Rs 750 to 1,250 |
| Corporate or e-learning professional (any Indian language) | about Rs 1,000 per minute, 15-minute minimum common |
| Ad and brand artist (casting platform, Gold tier) | from about Rs 17,000 for up to 1 minute, with extra minutes at around half; Silver from about Rs 8,000 |
| Documentary, up to 10 minutes (professional) | up to about Rs 18,000 |
| IVR prompt | from about Rs 400 per prompt |
| Studio time | extra, billed on actuals; usage and term fees on broadcast work |
Pricing depends on duration, usage (digital, broadcast, IVR), term, edits, and studio. A script of about 140 words per minute is a common planning figure (3P).

## 8. Contract points (the user's counsel reviews)
Scope of use, term, territory, media; buyout vs licence; AI clause (default: no AI training or cloning without a separate signed agreement and fee); revisions; credit; confidentiality; recording ownership; kill fee; payment; deliverables list. Keep a copy with the licence log.

## 9. Singing (extra risk)
- ElevenLabs Music vocals: official pages name English, Spanish, German, Japanese; Tamil is not documented (F). Test Tamil in script and in transliterated Latin; expect lyric and stress errors on ழ, ற and ள (U). Credits are heavy per track.
- PVC does not support singing (3P). Treat voice-conversion of singing as U.
- Reliable route (E): a human singer records the Tamil vocal, a music director arranges, AI is used only for the temp track or a backing bed. Playback singer voices only with the singer's consent.
- If AI singing is used for a short or temp, label it TEMP, keep lyrics short, and have a native speaker and a musician check scansion and pronunciation.
- No prompts naming artists or songs; run a similarity check (sound-music-voice.md section 6).

## 10. Decision shortcuts
- No budget for a performer: AI TTS with spoken script, take selection and post.
- A performer is available for 1 hour: STS.
- Face on screen, broadcast, or emotional drama: human artist.
- Many languages, one brand voice: a consented clone, native reviewers per language.
- Singing: human singer.
