# Performance brief template
One brief per shot, saved as `C:/Claude Code/company/creative/<client>/<project>/performance/<shot-id>-brief.md`. Client-neutral: fill with the project's own names. Keep each brief to one page; the prompt-engineer converts it to the model dialect.

## 1. Header
- Shot ID, scene, sequence, version, date, author (performance-director), reviewer (creative-director).
- Shot size, lens, camera move, light summary (from the cinematographer's shot list).
- Duration, aspect, fps, model and route (prompt only, transfer, native audio, lipsync pass, hybrid).
- Credit estimate, cap, and date of the user's yes (blank until given).

## 2. Character and bible link
- Character name, asset lock id (Soul ID, Element, character sheet), skin tone and undertone line from the lock (never changed).
- Performance bible fields in play: baseline, tempo, tics, emotional range, status, cultural markers.
- Wardrobe and props in hand (one per hand).

## 3. Beat
| Field | Entry |
|---|---|
| Beat number and length | |
| Want / obstacle / tactic | |
| Emotion and intensity (1 to 3) | |
| Subtext (said versus meant) | |
| Physical behaviour (3 to 5 small tells, with timing words) | |
| Landing (last second) | |
| What the viewer should feel | |

## 4. Blocking and eyeline
- Start position and end position (relative to anchors in the set), one move per beat.
- Screen direction (faces screen left or right).
- Eyeline: target (person, object, off-screen direction), eye height, angle from lens (0 for direct address only if intended).
- Eyeline match with the previous and next shot.
- Hands: which hand does what; business (prop actions).

## 5. Dialogue (if any)
- Line (exact text), language and script, speaking rate, pause markers.
- Voice id and the voice-director's take reference.
- Pre-line breath, post-line hold, emotion in the voice versus on the face.
- Lipsync route (native audio, Lipsync Studio model name) and 25 fps mouth QA noted.
- Length check: about 35 words per 15 s.

## 6. Transfer details (if route uses a reference video)
- Performer (name or ID), consent file reference (stored outside public folders), consent covers: likeness, motion, voice, term, territory.
- Reference video file, take number, fps (24 or 25), length, framing (waist up or full body), lighting note.
- Character image file (must match framing), model (Kling Motion Control, Act-Two, Genjutsu), mode (Match Video or Match Image), resolution tier.
- Test clip plan (3 to 5 s on the hardest beat).

## 7. Prompt skeleton (for the prompt-engineer)
Shot size and angle. Subject (from the lock) and attire. Action in one sentence with timing words. Face and eye behaviour. Gaze target. Hands. Setting anchors. Light. Realism cues (photoreal-humans). Region and culture cues (asian-human-reference). Negative notes (no sudden smile, no look at lens, no extra hands). Dialogue handling.

## 8. Do and do not
- Do: physical behaviour, timing words, one emotion arc, short line.
- Do not: name a real actor, ask for two emotions at once, use "emotional", describe subtitles or text, lighten skin.

## 9. Take review sheet
| Take | Beat match | Intensity | Eyeline | Hands, eyes, teeth, skin | Identity and tone | Landing | Decision |
|---|---|---|---|---|---|---|---|
| 01 | | | | | | | keep / refine one variable / reject |
Pass requires every column ok (all six questions in acting-direction.md section 9). One failing column means change one variable. After 3 drafts per shot, stop and rewrite the brief (creative-studio rule: no blind rerolls).

## 10. Performer consent checklist (tick before capture)
- [ ] Written release signed and dated, naming AI generation and performance capture.
- [ ] Scope: face, body motion, voice, edits and digital replicas, media, channels, term, territory.
- [ ] Right to withdraw and deletion terms; payment terms stated.
- [ ] Not a minor (or guardian consent verified and the Manager informed).
- [ ] Not a celebrity or public figure; reference video is original, not from a third party.
- [ ] Platform terms checked on the date: ____ (Kling, Runway, Higgsfield).
- [ ] Disclosure and AI label plan decided.
- [ ] Consent file stored outside public folders; reference recorded in log.md.
If any box is unticked, no capture and no generation.
