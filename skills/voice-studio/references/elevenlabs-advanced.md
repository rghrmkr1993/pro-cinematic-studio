# ElevenLabs advanced (v3, v4, settings, tags, cloning, STS)

Labels: F documented by ElevenLabs (see sources.md), 3P third party, E estimate to tune by ear, U unverified. Tool names and the credit gate live in `${CLAUDE_PLUGIN_ROOT}/skills/film-studio/references/elevenlabs.md`. Docs and models change fast; re-check the live docs before a big job.

## 1. Model facts (F unless noted)
- Eleven v4 (`eleven_v4`, released 2026-09-28, 3P for the date) is recommended over v3 for most users. 90+ languages, 10,000 characters per request. Tamil is not named on the v4 page, so test it (U).
- Eleven v3: 70+ languages, 5,000 characters per request.
- v4 and v3 do NOT support SSML `<break>` tags. Phoneme tags work only on `eleven_flash_v2`. Pauses come from tags, ellipses and punctuation.
- v4 settings: Stability and Similarity only. Docs: "Style and Speed sliders are not available in Eleven v4". v3: Similarity not available; Speed not available for v3 or v4 (the same docs page contradicts itself in one FAQ line, so test the UI).
- Speed 0.7 to 1.2 exists on older models (v2, Flash); extreme values reduce quality.
- PVCs are supported again in v4; IVCs and PVCs made before v4 must be retrained for v4. Every clone needs verified consent.
- Stability presets on v3 (3P, widely repeated): Creative (most expressive, tags land, can hallucinate), Natural (balanced, closest to the voice), Robust (very stable, tags barely respond). Not in the official docs page I could fetch (U).

## 2. Settings to try (E starting points; change one thing at a time)
| Goal | Model | Stability | Similarity | Notes |
|---|---|---|---|---|
| Warm narration, long form | v4 | 50 | 75 | Docs default zone: stability about 50, similarity about 75, style 0 |
| Emotional or conversational line | v4 | 35 to 45 | 70 | Lower stability widens emotion but can get erratic; take 4 or more |
| Ad read, punchy | v4 | 40 | 75 | Short lines, one tag max |
| Consistent brand voice across 50 lines | v4 | 55 to 65 | 80 | Safer, a little less lively; add life in script and post |
| Emotional dialogue on v3 | v3 | Creative or Natural | n/a | Robust ignores tags; do not use for acted lines |
| Poor source clone | any | 50 | 60 to 70 | High similarity copies the source noise (F, docs) |
Speaker Boost: subtle gain in likeness, more latency (F); leave off for Tamil tests unless a clone sounds off. Style exaggeration: keep 0 where it exists (F recommended 0).
Randomness note: output is non-deterministic, sliders set a range not a result (F). Fix a seed where the API exposes `seed` for repeatable comparison (E: seed gives near, not exact, repeat). To vary a line, change the seed, not the text.

## 3. Audio tags (v3 and v4)
Tags are free text in square brackets, not a closed list (3P). Official examples: `[laughs] [whispers] [sighs] [exhales] [sarcastic] [curious] [excited] [crying] [warm] [long pause]`, sound effects such as `[applause] [door slams]`, experimental `[strong X accent] [sings]`.
Rules:
1. One tag per phrase where the feeling changes; zero in neutral lines. Over-tagging sounds acted and brittle (E).
2. Tags can be read aloud or ignored, especially in non-English; test in Tamil before trusting `[softly]` style tags (U). Describe voice quality instead: `[low, calm voice]`, `[speaking gently]`.
3. A tag must fit the voice. A calm narrator will not shout on `[shouts]` (F).
4. Tags work best in text over about 250 characters (3P).
5. Put the emotion in the words too. Tag plus matching line beats tag alone.
6. If a tag is spoken aloud, delete it and rely on punctuation, or re-take.
Examples (English tags around Tamil text; translation in brackets for the reader):
- `[warm] இந்த சோப்பு... எங்க பாட்டி செஞ்ச மாதிரியே இருக்கும்.` (This soap is like the one my grandmother made.)
- `[sighs] நாளெல்லாம் வேலை... [softly] ஆனா இந்த நேரம் எனக்கு மட்டும்.` (All day work, but this moment is only mine.)
- `[excited] இன்னைக்கு ஒரு புது விஷயம் சொல்லப் போறேன்!` (Today I will share something new.)
Tamil examples are my own drafts: native review required.

## 4. Punctuation and delivery (F for v4, E for Tamil)
- Ellipsis `...` adds a pause or hesitation; a dash is a lighter pause (less consistent). CAPITALS add emphasis (Latin words only; Tamil has no caps, so rely on word order and tags).
- Break one long sentence into 2 to 3 lines. Each line is one breath.
- Avoid many breaks or tags in one generation: instability, speed changes, noise (F).
- Context stitching and previous_text or next_text parameters (API) keep pacing across consecutive lines (v4 feature, F). Use them when generating line by line so the voice does not reset tone.

## 5. Text normalization and numbers
Normalization is on by default (F). Still, write numbers in words in Tamil (script-for-voice.md section 5), and spell out currency, dates, phone numbers, units, URLs. Smaller or faster models misread numbers more (F).

## 6. Pronunciation
- v4: IPA between forward slashes inside the text, with stress marks, e.g. `/ˈbaɪoʊ/`; test with the chosen voice, generate several takes (F).
- Alias rule: map a written form to a spoken one (`UN` to `United Nations`). Pronunciation dictionary: TXT or `.PLS`, alias or phoneme rules only, case sensitive, first match wins, upload in Studio or Dubbing Studio (F). Phoneme rules apply to older models only; on v3 and v4 use alias rules and respelling in Tamil script (E).
- Brand and ingredient words: try the Tamil-script spelling (வைட்டமின் ஈ), a phonetic spelling, and the Latin spelling; keep the one that scores best; store it in the dictionary.

## 7. Voice choice and Voice Design
- Pick a native Tamil voice from the library first (owner-checked: 20+ professional Tamil voices, filter by language and use case; see elevenlabs.md). Library voices Srivi and Bhavatharini are the current defaults; audition at least 5 more before locking one.
- Voice Design (F, experimental): structure `Native Tamil. Female, 30s. Good quality. Persona: warm storyteller. Emotion: gentle, reassuring. Two sentences on timbre and pace.` State language and region first; use "thick" rather than "strong" for accent; avoid FX words (reverb, phone); guidance scale about 20 to 40 percent; use a full-sentence preview that matches the mood. Docs say PVC is higher quality than Voice Design.
- Do not use "accent" when you mean intonation. Do not ask for a celebrity-like voice.

## 8. Cloning (F; consent in voice-ethics.md)
| | Instant (IVC) | Professional (PVC) |
|---|---|---|
| Audio | about 1 to 2 minutes clean (page says about a minute; upload screen says 10 s minimum, inconsistent) | 30 minutes to 3 hours clean and consistent |
| Verification | Consent checkbox | Voice verification: record samples compared with the long recording |
| Quality | Convincing likeness, weaker on breath and emotion range | Captures breath, pacing, emotional range; closest to the original |
| Time and plan | Seconds; from the entry paid tier | Hours to days (3P: 3 to 6 hours up to 72 h); Creator tier and up (3P) |
Tips: record dry, 48 kHz, no music, no reverb, varied emotion for PVC; 3 minutes beyond the first minute gives little gain for IVC (3P). PVC does not support singing (3P).

## 9. Speech-to-Speech (voice changer), the usually most natural route
- Record a human performance (guide), choose a target voice (library, clone or designed), convert. Keeps whispers, laughs, accent and subtle emotion (F). Timing is not documented as preserved but in practice follows the input (E, test).
- Models: `eleven_multilingual_sts_v2` (29 languages; Tamil U, test) and an English one. Start with the multilingual model even for English (F).
- Max 5 minutes per segment; set `remove_background_noise=true` for noisy rooms (F). Cost is 1,000 characters per minute of audio (F).
- Best input: dry, close mic (10 to 15 cm), 48 kHz, no clipping, performed with full emotion and the exact words. Do not whisper-guide; perform at target energy.
- Failure fixes: output has the guide's accent leaking (pick a Tamil voice or a different target); pitch wobble (lower the guide's vibrato, record steadier); artifacts on plosives (pop filter, retake).

## 10. Dubbing Studio (F)
90+ languages claimed, audio only, no lipsync. Auto speaker detection, per-speaker voice, timeline editor to fix translation, reassign speakers, regenerate clips (editing depends on plan; API transcript editing is Enterprise-only, 3P). Third-party lists name Tamil among supported dubbing languages (3P). Review every Tamil translation by a native adapter; machine Tamil is often formal and long. Match to the dubbing flow in sound-music-voice.md section 9.

## 11. Failure fixes
| Symptom | Likely cause | Fix |
|---|---|---|
| News-reader tone | Written Tamil script | Rewrite spoken (script-for-voice.md) |
| Same cadence every line | One take, high stability | Lower stability to 40, 4 takes, splice |
| Tag spoken aloud | Tag not understood | Use descriptive wording, or remove and rely on punctuation |
| Speeds up or garbles mid-line | Too many breaks or tags, long input | Split lines, under 300 characters per line |
| Wrong word stress | Ambiguous spelling | Respell, alias dictionary, re-take |
| English words sound foreign | Latin text in a Tamil sentence | Try Tamil-script transliteration |
| Hiss, metallic ring | Source clone noise or heavy similarity | Lower similarity; clean source; post de-ess |
| Voice drifts across lines | Per-line independent generation | Context stitching, fixed seed, same settings |
| Hallucinated extra words | Creative mode on v3 | Natural mode, shorter lines |
| Singing in Tamil wrong | Music v2.5 language gap (F) | Human singer, see hybrid-and-human-artists.md |
