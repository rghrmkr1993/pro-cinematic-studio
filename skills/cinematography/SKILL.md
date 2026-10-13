---
name: cinematography
description: "Director-of-photography craft translated into AI video and image prompts: shot sizes and angles, camera movement, lenses and optics, composition and blocking, lighting, color and film looks, coverage and sequences, director-style techniques, per-model camera prompting (Higgsfield Cinema Studio, Seedance, Kling, Veo, Runway) and shot-list templates. Use for any request about camera, shots, framing, lens, lighting, composition, color grade, film look, storyboard, shot list or coverage for AI-generated video or stills."
---
Part of the cinematic pipeline: entry point creative-studio


# Cinematography for AI video and images

A DP decides what the audience sees, how close, from where, in what light and color, and how the frame moves. This skill turns those decisions into prompt words that image and video models obey. Evidence labels used in the files: (V) vendor-official, (3P) third-party guide or practitioner, (K) established film craft, (H) house rule. All items once labelled unverified were resolved on 2026-10-14: each claim carries a [verified source, date] tag or a [no public source ...; checked: ...] marker.

## Router: open only what the job needs
**MANDATORY first step for any scene the user describes: `references/scene-to-shot-reasoning.md` (13-step thinking protocol, 10-question check, 6 worked examples). Do it before the workflow below.**

| Need | Open |
|---|---|
| Frame size or camera angle, emotional effect | `references/shot-sizes-and-angles.md` |
| Any camera move (push, orbit, handheld, whip, dolly zoom...) | `references/camera-movement.md` |
| Focal length, anamorphic, depth of field, frame rate, special lenses | `references/lenses-and-optics.md` |
| Framing rules, blocking, 180 and 30 degree rules, depth staging | `references/composition-and-blocking.md` |
| Light setups, Kelvin, contrast ratio, skin-tone lighting | `references/lighting-for-film.md` |
| Palette, film stock, grain, halation, genre and regional looks | `references/color-and-look.md` |
| Coverage, dialogue or chase grammar, montage, transitions, AI shot planning | `references/coverage-and-sequences.md` |
| "In the manner of" styles, Indian cinema traditions | `references/director-styles.md` |
| Model-specific syntax and failure fixes | `references/ai-camera-prompting.md` |
| Shot list or storyboard format, worked scenes | `references/shot-list-templates.md` |
| Camera bodies, sensors, film formats, do AI models read camera names | `references/camera-systems.md` |
| Exposure triangle, shutter, ISO, ND, log, dynamic range, aspect ratios | `references/exposure-and-settings.md` |
| Frame rate by content type, slow motion, 50 Hz flicker, AI model fps, interpolation, timeline rule | `references/frame-rates-deep.md` |
| Prompt length limits per model, fitting a scene into 512 characters, the 512 check | `references/prompt-compression.md` |
| Lens families, crop factor, filters, flare, what to prompt per look | `references/lens-deep.md` |
| Still photography, product and cosmetics lighting, retouch rules | `references/photography-craft.md` |
| Where claims came from | `references/sources.md` |

## Sibling skills (link by name, do not duplicate)
- `higgsfield-master` (platform UI, Cinema Studio panels, signature shots, visual-language): use for settings and credits. This skill supplies the why and the wording.
- `creative-studio` (routes visual jobs), `film-studio` (long-form film production pipeline, built in parallel): hand sequencing and production steps there.
- `graphics-rendering` (3D and real-time lighting math), `motion-animation` (UI and 3D camera grammar), `photoreal-humans`, `asian-human-reference` (people realism), `seedance-20` and `01-cinematic` (model packs).

## Shot-design workflow (run in order, one pass per shot)
1. Story beat: what changes in this shot? One sentence. No change, no shot.
2. Emotional intent: what should the viewer feel (safe, uneasy, awe, desire, trust)?
3. Shot size: how close the viewer must be to feel it (`shot-sizes-and-angles.md`).
4. Angle: power and vulnerability, tilt, height.
5. Lens: focal length and depth of field set intimacy and isolation (`lenses-and-optics.md`).
6. Move: only if it carries meaning; otherwise lock off. One move per shot.
7. Light: name one motivated source, direction, quality, color temperature.
8. Color: three-color palette, contrast, grain, look reference.
9. Composition: where the eye lands, headroom, lead room, depth layers, screen direction.
10. Prompt: assemble in the order below, add constraints, pick the model, generate 2 to 4 variants.

## Prompt assembly order (works across models)
`[Shot size + angle + lens] + [Subject and action, start pose to end pose] + [Environment, 3 anchors] + [Camera move with speed, start framing, end framing] + [Light: source, direction, quality, Kelvin] + [Look: palette, stock, grain] + [Constraints]`
Example: "Medium close-up, eye level, 50mm shallow focus. A baker lifts a loaf from the oven and turns to the window. Brick kitchen, flour dust, steel racks. Slow push-in over 5 seconds from medium close-up to close-up, then hold. Warm window light from camera left, 4000K, soft, faint haze. Natural color, fine grain. One continuous shot, no cuts, no zoom."

## Golden rules
1. Every choice answers a story or emotion question (K). If a choice stands out without reason, remove it. (3P, Deakins interview paraphrase)
2. One move per shot, one subject action per shot, one named key light per shot (H, 3P).
3. Write what the camera does, with speed and endpoints. Vague "cinematic" gives random results (V, Higgsfield camera blog).
4. Physical terms beat adjectives: "50mm, f/2, soft window light 4000K" beats "beautiful dreamy".
5. Cuts need contrast: change size, angle or action between shots, and move at least 30 degrees or change size by two steps to avoid jump cuts (K).
6. Keep screen direction and the 180-degree line unless crossing is deliberate (K).
7. Lock identity first (reference image, Element, first frame), then spend prompt words on camera and light (H).
8. Light faces with care for the actual skin tone: exposure, reflectance and highlight roll-off, never a one-formula fix (3P, ASC-profile interviews).
9. Short generations obey better than long: 4 to 8 seconds per move, chain shots by last frame (3P).
10. Negative phrasing is unreliable on some models (Runway, Veo advise positive wording): write "locked camera" not "no camera movement" (V).
11. Test cheap, finish dear: draft on a fast model or low resolution, lock the camera language, then render finals (H).
12. Check hands, product labels, text, eye lines and reflections in every output before use (H).

## Common failure signals and first fix
| Symptom | First fix |
|---|---|
| Random or jittery move | State one move, speed, start and end framing; remove other motion words (V) |
| Face or product morphs during move | Shorter move, partial orbit, hold the first frame, drop the second subject action (3P) |
| Flat look | Name the source and direction, add a rim or practical, add haze (K) |
| Looks "AI shiny" | Add grain, lower contrast, real stock reference, remove "8k, ultra detailed" (3P) |
| Wrong lens feel | Name mm and aperture, not just "wide" (V) |
| Scene cuts do not match | Re-state environment anchors and light in every shot (H) |

## Output standard
Return: the shot list row(s) from `shot-list-templates.md`, the final prompt per shot, the model choice with reason, the settings to apply in the tool UI, and the checks to run on the result. Mark any claim about a model feature you could not verify with a [no public source as of <date>; checked: ...] marker. Client-neutral: never reuse one client's brand, names or product as example content for another.

## Safety and compliance
No real-person likeness without documented consent. Product beauty and skincare shots must not imply results the product cannot support; copy and claims belong to the compliance owner. Do not imitate a living artist's protected work: use technique descriptions only (`director-styles.md`).
