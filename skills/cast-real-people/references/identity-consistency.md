# Identity consistency across a film (cast-real-people)
Builds on higgsfield-master characters-and-consistency.md; do not repeat the general stack here. Labels: (V) vendor-official, (3P) third-party, (U) unverified.

## 1. Choosing the lock path
| Situation | Path | Why |
|---|---|---|
| 20+ good photos, hero or recurring role | Soul ID, then Elements for video | strongest face lock; reusable across Soul-family models |
| 8 to 19 photos, short film or one ad | reference set: front, 3/4 L, 3/4 R, profile (from Nano Banana Pro character sheet or the photos) | no training; cheaper |
| Background actor or one-shot cameo | 2 to 4 reference images in the video model | not worth training |
| Multi-person scene | one Soul ID per person, Elements for the scene (V: one Soul ID holds one person) | prevents blended faces |
| Existing live footage of the person | performance-direction reference capture, motion transfer onto the lock | keeps the real performance |
Best default for a real-face film (assumption, to be proven on the first test grid): Soul ID for stills and key frames, then use the passing stills as image-to-video starts and Elements/@character references in Seedance, with Kling Elements as the second option for close-ups and Veo 3.1 (3 refs) for dialogue shots with native audio.

## 2. Lock sheet (refs/<person>/lock/)
1. Six anchors: front, 3/4 L, 3/4 R, profile, smile, serious, all neutral light, plain grey background, 2K.
2. One full-body panel with the face blurred or erased (Academy rule: lock only one face per sheet), and a separate sheet per wardrobe or state (dry, sweaty, injured, aged).
3. Identity text line (a short factual description, for example age range, skin undertone, hair, eye colour, marks) used only as support; the images carry identity (V: text is reinterpreted each time).
4. Version and date, Soul ID or Element name `<project>_<person>_v1`, QA score, approval by the person.

## 3. Test grid (6 to 9 neutral shots)
Front, 3/4 L, 3/4 R, profile, slight up tilt, slight down tilt, soft smile, serious, one medium-wide. Same lens language (85mm look), same light, same background; change one variable per cell. Generate cheap (draft), keep seed and prompt in the log. Score with the SKILL.md scorecard; show the person.
Failure patterns and fixes:
- Face is "similar but prettier": add imperfection anchors from real photos (marks, asymmetry); lower style strength; remove beauty words; retrain with less retouched photos.
- Skin lighter or smoother than the real person: put undertone and Fitzpatrick/Monk range in the identity line, use neutral daylight, check on a vectorscope skin line (color-grading); reject, do not grade it back.
- Age drift: add age range and "mature bone structure, no baby face"; use the correct-age reference.
- Eyes or mouth shape wrong: add a close-up reference crop of that feature; use inpaint on that region.

## 4. Across the film
- Wardrobe and hair bible per scene state; describe wardrobe verbatim in every shot; attach the wardrobe reference.
- Lighting continuity: one lighting card per scene (key direction, colour temperature, softness); same direction across the coverage; change only when the story changes.
- Camera: closer shots hold identity better; wide shots show a tiny face. Plan hero lines in medium close-ups, use wide shots with the person from behind or small in frame, or run the face repair pass (below).
- One variable per shot; chain last frame to first frame; keep clips under about 30 s (V characters-and-consistency.md).
- Anchor refresh: after each sequence, save the strongest frame as an extra anchor; compare the next batch to the lock sheet, not to the previous shot (prevents compounding drift).
- Hardest shot first: run the toughest angle, motion and expression before the rest.
- Seedance roles: @character for identity, separate @motion for performance; keep identity in the reference, action in the prompt.

## 5. Drift repair: the face-reference edit pass
1. Detect: side-by-side with the lock sheet at 100 percent; check eye spacing, nose bridge, jaw, hairline, marks, skin tone.
2. Minimal fix first: re-roll with the same lock and seed variation (cheapest), then
3. Edit pass: use an image or video edit tool (Edit Image/Inpaint for stills; Seedance 2.5 Edit with Draw to Edit or Kling Omni Edit for video; V tools-a-z.md) with the lock images as references and a prompt that says "keep composition, pose, light; restore the identity of the reference face; keep skin tone and marks". Mark only the face region.
4. Face swap: only as the last repair, only to place the same consented person's face onto their own digital double, never another real person's body, never with a face that has no release.
5. Re-run QA (face match, skin tone, features, age). Check skin pores and sharpness after the edit (V: after every edit pass re-check skin detail).
6. Upscale last, on the selected final; upscaler Creative modes may change faces (V), so use the Precise mode and re-run QA.
7. Log the repair: shot ID, tool, lock version, before and after, who approved.

## 6. Lipsync and speaking shots (voice consent first)
Front-facing or three-quarter frame, mouth uncovered, one to two sentences per clip (about 35 words per 15 s) (V blog 2026-10-08). Models offered by Higgsfield Lipsync Studio include Veo 3.1, Kling 2.6 Lipsync, Wan 2.5 Speak, Kling Avatars 2.0 (V tools-a-z.md). Check eyes, jaw, hair and signature marks while speaking and the teeth shape of the real person. Indic scripts: indic-languages for phoneme timing and review. Use the person's approved script and voice file only.

## 7. Approved tools for face data
Studio-held paid accounts on Higgsfield (web, MCP), Google Gemini/Veo API accounts on the studio's own cloud, Kling via Higgsfield or the studio account. Not allowed: free online face-swap sites, browser extensions, mobile "AI photo" apps, unknown Telegram or Discord bots, any tool whose terms let it keep and resell faces. If a tool is not on this list, the Manager approves it in writing after reading its terms.

## 8. Generation log fields
date, shot ID, person, lock version, tool and model, prompt file, seed, input references, output file, credits, approved by, consent file checked (yes), label decision.

## 9. Handoff to prompt-engineer
Hand over: lock sheet path, Soul ID/Element names, identity line, wardrobe bible, lighting cards, QA score, permitted uses (media, territory, term, voice yes or no), forbidden uses, and the line "real faces only from casting-director identity locks".
