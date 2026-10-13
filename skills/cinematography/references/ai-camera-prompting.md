---
name: cinematography
description: "Model-by-model camera control for AI video: Higgsfield Cinema Studio camera bodies, lenses and moves, Seedance, Kling, Veo and Runway, with phrasing that works, how to avoid camera-move failures, and a test protocol. Part of the cinematography skill."
---

# AI camera prompting by model
Labels: (V) vendor-official page, (3P) third-party guide or community test, There is no open unverified label any more: every claim carries a verified tag or a no-source marker. Researched 2026-10-13, resolved 2026-10-14. Model versions change quickly; confirm names on the generate screen. Platform panels and prices live in `higgsfield-master`; this file is the camera-language layer.

## Universal formula
`[Shot size, angle, lens] + [Camera move, speed, start and end framing] + [Subject and one action] + [Environment anchors] + [Light] + [Look]`
Google (Veo) states Cinematography + Subject + Action + Context + Style as its official order (V). Runway: Camera Movement + Scene + Action + Details (V). Kling third-party: Camera + Scene + Subject action + Light + Audio (3P). All lead with the camera.

## Universal laws
1. Lead with the shot and the move. (V Runway, Google)
2. One primary move per shot. (V Runway; 3P Kling and Veo)
3. Name speed and endpoints. (V Higgsfield blog)
4. State start and end framing: "starting on a wide, ending on a close-up". (V)
5. Image-to-video: the image sets composition, light and style; the text should be almost all motion. (V Runway)
6. Keep prompts short for single clips (about 3 to 5 sentences). Long prompts dilute camera control. (3P)
7. Replace negatives with positives on Runway and Veo: "locked camera", "steady", not "no shake". (V)
8. If motion drifts, simplify the prompt and let start and end frames carry the direction. (V Higgsfield Kling note)
9. Test one variable at a time (Kling's own guide advises speed, then move type, then style). (V)

## Higgsfield Cinema Studio (see `higgsfield-master/references/cinema-studio.md` for versions)
- Keep hardware in the panel: camera body, lens, aperture, genre; prompt text is for story and action. (V and 3P)
- 4.0 panel (V): Camera types Auto, Modern, 35mm Film, 8mm Film, DV Camcorder; lenses Auto, Clean Sharp, Anamorphic, Vintage Anamorphic, Warm Vintage, Halation Vintage; aperture f/1.4, f/4, f/11; 30+ movement presets; Genre, Era, Tempo; lighting presets; speed ramps; Forward and Backward Extend; Edit Video.
- Presets set register; the prompt still names the move and endpoints. (V blog 2026-10-09)
- Stack up to three simultaneous moves in presets (3P); keep to one unless you are experienced.
- Map goals to settings:
| Goal | Body | Lens | Aperture | Move |
|---|---|---|---|---|
| Premium product | Modern | Clean Sharp | f/4 | Slow dolly in or orbit |
| Nostalgic memory | 35mm or 8mm | Halation Vintage | f/1.4 | Slow push-in |
| Epic landscape | 35mm | Anamorphic | f/11 | Helicopter, crane |
| Handheld chaos | DV Camcorder | Warm Vintage | f/4 | Handheld, Tempo Chaotic |
| Clinical clarity | Modern | Clean Sharp | f/11 | Static |
- Failure: version-name mixups; always read what the selected version shows. (V)

## Seedance 2.x (3P guides; Higgsfield-hosted)
- Reads: push in, pull back, dolly in, truck left, arc, orbit, handheld follow, crane up, tilt, locked-off. (3P and V Higgsfield notes)
- Five cues per shot: framing, angle, camera move with speed, depth of field, lens hint such as "35mm anamorphic". (3P)
- Allows 2 to 3 combined moves with "while" in some guides; others say one. Default to one. (3P conflicting)
- Match move to size: static or micro push-in for ECU, handheld or gimbal for MS, slow push, static or crane for wide; avoid handheld on wide. (3P)
- Start with a push-in: rarely misfires. (3P)
- Example: "Slow push-in from medium to close-up, 50mm, f/2, subject lifts the cup and looks left, soft window light, locked horizon, no cuts."
- Specialist packs: `seedance-20`, `01-cinematic`, `05-fight-scenes`, `07-ecommerce-ad`.

## Kling (3.0 and later; 3P plus Kling's blog)
- Open with the capture method; use cinematic verbs (dolly push, whip pan, crash zoom). Generic "moves" gives little. (3P)
- Clause-separate: "Slow dolly in only." then subject action in a separate sentence. (3P)
- Orbit: keep to 30 to 90 degrees per 5 s clip and slow; image-to-video holds identity better with partial orbit. (3P)
- Multi-shot prompts: "Shot 1 (0-3 s) ... Shot 2 (3-6 s) ..." with a different move per shot. (3P)
- Start and end frame attach on Higgsfield Kling: start defines opening, end defines resolution, both lock trajectory. (V Higgsfield)
- Official page lists static, pan, tilt, zoom, dolly, orbital, crane, roll, master-shot presets, Motion Control (locks character motion while the camera is directed). Standard mode for drafts, Professional mode for finals. (V Kling blog; partly promotional)
- Speed descriptors with durations are helpful: ultra-slow, slow and deliberate, moderate, quick snap. (V)

## Veo (3.1)
- Official: Cinematography + Subject + Action + Context + Style. (V)
- Vocab: dolly, tracking, crane, aerial, slow pan, POV; wide, close-up, extreme close-up, low angle, two-shot; shallow depth of field, wide-angle, soft focus, macro, deep focus. (V)
- Example from Google: crane shot starting low on a lone hiker and rising to reveal a mist-filled canyon at sunrise. (V)
- First and last frame: provide start and end images and a transition description; the model fills in motion and audio. Use for match cuts and morphs. (V)
- Ingredients to video: reference images for character, object, scene or style, kept consistent across shots. (V)
- Audio: dialogue in quotes; "SFX:" for sounds; "Ambient noise:" for atmosphere. (V)
- Limits: 4, 6 or 8 s clips; 720p or 1080p; 16:9 or 9:16. (V)
- If no camera is stated, Veo tends toward a static or gently floating frame. (3P)
- Negatives: describe what is present ("a desolate landscape, empty roads") instead of "no buildings". (V)

## Runway (Gen-4 and 4.5)
- Plain English over jargon; current models understand everyday description better than technical terms. (V)
- Formula: [Camera Movement] + [Scene] + [Action] + [Details]; one action per prompt; 5 to 10 s. (V)
- No "then" sequencing; each prompt stands alone. (V)
- Positive phrasing only; negatives can backfire (V). Use "the camera remains completely still".
- Vocabulary: static, handheld, dolly, tracking, crane, pan, tilt, whip pan, orbit, dolly zoom, drone ascending. (V)
- Image-to-video: spend text on motion only. (V)
- Community tests: orbits above low speed drift at edges; heavy handheld jitters fine detail. (3P)

## Image models (stills)
- Shot size, angle, lens and aperture words work well; motion words do nothing. (K)
- Use camera body and film words for look: "35mm film, Portra 400, f/2". (3P)
- Build look-dev frames first (Soul Cinema, GPT Image, Nano Banana Pro on Higgsfield, V), then animate. (V)

## How to avoid camera-move failures
| Failure | Cause | Fix |
|---|---|---|
| Move ignored | No camera words or lost behind long text | Lead with the camera; shorten |
| Move reversed or different each run | Speed, path, end undefined | Add speed, path, end framing (V) |
| Zoom instead of dolly | Ambiguous "move in" | "Camera physically dollies forward, focal length constant" |
| Subject morphs mid-move | Big angular change or long clip | Partial orbit, shorter clip, start frame reference |
| Hands, label or face warps | Fast move plus close subject | Slow down, lock the move, add still beats |
| Floating or "swimmy" background | Handheld on wide | Gimbal or lock-off |
| Fake gimbal "AI float" | Default model drift | State "locked tripod, rigid" when you want stillness |
| Rack focus fails | Whole frame stays soft | Choose a single focus plane or cut between two shots |
| Dolly zoom not working | Hard for models | Generate several; or fake in edit with scale plus dolly |
| Camera appears in shot or reflects | Mirror or glass | Reduce reflection; use angle off-axis |

## Test protocol (H)
1. Draft: 3 variants at lowest cost, same prompt, to learn how the model reads the move.
2. Change one variable (speed, then end framing, then lens).
3. Choose the best path, lock the wording, reuse it verbatim across shots (V Higgsfield).
4. Finals at full resolution; run a defects checklist (hands, text, eyelines, reflections).
5. Log working prompts in `shot-list-templates.md` format for reuse.

## Model-pick quick table (3P; test before committing)
| Need | Try first |
|---|---|
| Directed multi-shot with native audio | Cinema Studio (Seedance 2.5 default in 4.0, V) or Kling 3.0 multi-shot |
| Realistic dialogue with sound and clean aerial reveals | Veo 3.1 |
| Fast iteration, image-to-video stylization | Runway Gen-4 family |
| Precise orbit or product turn | Seedance or Kling with image-to-video |
| Frame-pair transitions | Veo first and last frame, Kling start and end |
