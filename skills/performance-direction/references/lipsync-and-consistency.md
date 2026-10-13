# Lipsync acting and performance consistency
Labels: (V) vendor-official, (3P) third-party, (H) house rule, (E) estimate, (U) unverified. Mouth shapes, syllable rate, script adaptation, tool comparison and ffmpeg alignment for Indian languages live in `indic-languages` references/lipsync-and-dubbing.md (read it, do not copy it). Tool list: higgsfield-master tools-a-z.md (Lipsync Studio / Speak).

## 1. Acting while speaking
Speech is a performance, not just mouth movement. Lipsync tools animate the mouth; the director supplies the face around it.
- Prepare the pre-line beat: a breath, glance or shift of weight before the first word.
- Show the thought, not just the sound: brows, eyes and head move with emphasis words; a talking head that only opens its mouth reads as dead.
- Landing: after the last word, hold on the face for 1 to 2 s (the reaction is part of the line).
- Pauses: the pause in the delivery is acting. Keep pauses in the audio; do not trim them to fill the clip (E).
- Emotion in the voice must match the face: a sad voice over a neutral face breaks belief. Brief the voice-director and performance together (voice-studio).
- Audio-first: record or generate the voice first, then build the performance to its rhythm (H). The face follows the voice.

## 2. Prompt and setup for talking characters (V, characters-and-consistency.md official additions)
- Front-facing or three-quarter image, mouth uncovered; avoid extreme angles, fast head movement, hands near the mouth.
- 1 to 2 sentences per clip, about 35 words in 15 s; longer speech is split across shots (cut on breath).
- Check eyes, jaw, hair and signature details while the character speaks; fix drift before moving on.
- Native audio (Seedance, Kling 3.0, Veo, Wan 2.5) is simplest when the clip is fresh; Lipsync Studio when the audio is already made (V: image or video input, scene templates General, Selfie, Podcast, Car Talking; models include Kling Lipsync, Sync Lipsync 3, Wan 2.5 Speak, Higgsfield Speak 2.0).
- Do not write the spoken line inside the visual prompt in a way that makes the model render subtitle text; give speech as dialogue instructions or audio.

## 3. Indian-language lipsync (link: indic-languages)
- Tamil, Telugu and Malayalam dubs run longer than English at the same content; adapt the script for timing before generating (indic-languages lipsync-and-dubbing.md section 2 and 3).
- Lip shapes: Indian phonemes include retroflex, aspirated and long vowels that standard viseme maps handle imperfectly; test each tool on a short sample per language before committing (U on Indic quality, tested by us only per language).
- Review at 25 fps frame by frame on the mouth region (section 6 of that reference); log mismatches by frame.
- Pronunciation and script live with the voice-director and indic-languages; performance-direction only checks that the face matches the emotional intent and the timing of the pauses.
- Culture: expressions and gestures per region (asian-human-reference): a Tamil family dinner, a Hindi office scene and a Bengali conversation carry different gesture and distance norms (E, U on many points); the region lead reviews.
- Captions burn via ffmpeg libass for Indic scripts (editor).

## 4. Consistency of performance across shots
Faces stay consistent through locks; performance stays consistent through a bible.
Performance bible per character (one page, reused verbatim in every brief):
| Field | Example content |
|---|---|
| Baseline | Resting posture, gaze, face tension, breath pattern |
| Tempo | Slow and deliberate, or quick and light (words per second, movement speed) |
| Tics and habits | Rubs ring, tucks hair behind the left ear, taps two fingers |
| Emotional range | Rarely shouts, shows anger as stillness, smiles with the eyes first |
| Status | High or low (eye contact, space taken) |
| Voice link | Voice id, pace, accent; same across shots |
| Wardrobe contact | How they handle the saree end, watch, glasses |
| Cultural markers | Region, language register, greeting gesture (asian-human-reference) |
Rules:
1. Same words for the same behaviour in every prompt of a sequence (identity in the Element, behaviour in the prompt; characters-and-consistency.md).
2. Intensity ladder fixed per scene (e.g. level 1 until the turn, level 2 at the turn) and written in the beat map.
3. Chain clips: last frame to first frame inside a scene; keep clips under about 30 s (V consistency stack).
4. Match eyeline, screen direction and eye height across cuts; same blocking positions relative to anchors.
5. One performer, one capture session per character where transfer is used, so tempo and habits match; use the same performer for the same character across the film (consent covers the term).
6. Review each new take against the previous good take of the same character and against the first frame of the series (series drift check, V blog 2026-10-05 in characters-and-consistency.md).
7. Change one variable per retry (angle or light or action), not all at once.
8. Keep a prompt library of beats that worked, with model, settings and score (creative-studio learning loop).

## 5. Typical drift and fixes
| Drift | Likely cause | Fix |
|---|---|---|
| Emotion level jumps between shots | No fixed ladder | Write levels in the beat map, repeat the wording |
| Character becomes more expressive over a sequence | Model leakage, different seeds | Add "restrained, minimal facial movement" and reuse the same anchors |
| Gaze shifts to lens | No eyeline instruction | State the off-screen target and height in every shot |
| Tempo changes | Different model or clip length | Same model per scene; time reference clip or audio |
| Hands change habits | Prop and hand not locked | Prop sheet, hand law, simpler business |
| Face shape changes during speech | Lipsync model alters the mouth region | Lock the image, test model on a short sample; choose another lipsync model |
| Different accent or pace | Voice not locked | Lock voice id and speed (voice-studio) |

## 6. QA for lipsync and performance (per take)
- Mouth shapes close at B, M, P sounds; open on A; lips round on O and U (check the Indian phoneme list in the indic reference).
- Eyes alive: blinks every 2 to 6 s, gaze shifts at thought changes (E).
- Teeth and tongue natural; no melted lip contact.
- Head moves with the sentence; shoulders and breath visible on longer lines.
- Skin tone and identity match the lock; no brightening on close-ups.
- Audio sync within about 1 frame at start, middle and end (editing-and-assembly.md).
- The face reads the emotion at phone size.
