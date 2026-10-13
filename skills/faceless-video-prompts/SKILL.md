---
name: faceless-video-prompts
description: "Prompt-writing system for faceless YouTube videos on Seedance 2.5 (and similar video models): documentary, educational and explainer content. Turns a script beat or a 10-second block into a production-ready video prompt, dynamic multi-shot cuts, retention-first pacing, photoreal 'live' footage, sepia 'archive' beats and practical light VFX, with every key detail written in automatically so the output avoids generic AI slop. Trigger whenever the user asks for a faceless video prompt, a documentary/explainer shot, 'prompt for my faceless channel', a 10-second block, or hands over a script and says 'make the prompts'."
---
Part of the cinematic pipeline: entry point creative-studio

# Faceless Video Prompts (Seedance 2.5)

You write ONE standalone, render-ready video prompt per request. The reader runs a faceless channel:
no host, no talking head — the retention lives entirely in the picture, the cuts and the pacing.
Every rule below exists to kill the two things that murder faceless channels: **generic AI slop**
and **static, boring shots**.

## Core principle — write the visible

Describe only what the lens records: physical verbs, materials, geometry, light. Numbers instead
of adjectives — camera speed in km/h, atmosphere as a percentage ("humid air at 30% haze"), scale
against a known object, field of view in degrees, white balance in Kelvin. No mood words without a
physical carrier, no "cinematic / epic / stunning", no camera-equipment names — the look is written
as light, texture and grain, never as "shot on ARRI".

- ❌ "an epic mysterious shot of the pyramid" → ✅ "84° wide from ground level, the pyramid's edge
  cutting the frame on the right third, heat shimmer rising off the stone at 20% haze, hard flat
  midday light, pale grey-dust sky"

## Positive-only prompting

The model treats every noun as a request — "no people" plants people. Say what IS in the frame,
then pin it in a **POSITIVE LOCKS** paragraph at the end of the prompt: what stays true in every
frame (light, palette, staging, tilt, subject position, cut count). Hard prohibitions are rewritten
as affirmative states: "the site is unmanned in every frame; only architecture, equipment and light".

## Prompt architecture (block order)

Build every prompt in this order, dropping blocks that don't apply. Style lives distributed in its
home blocks — never as a "style:" prefix.

```
SCENE CONTEXT      one-paragraph summary of the whole clip
LOCATION MAP       what stands where — the spatial anchor that stops teleporting
FIRST FRAME        already mid-action; no empty establishing frames
FORMAT MODE        single take, or timed multishot with the exact cut count and timestamps
OPTICS             FOV in degrees + camera distance
CAMERA             the physical move, motivated
ACTION TIMING      per-shot time ranges: what happens from second to second
PHYSICS            weight, inertia, real material behavior
LIGHTING           practical sources, WB locked
AUDIO              the standing line: NO MUSIC. SFX ONLY (see below)
STYLE              texture, grain, palette percentages
POSITIVE LOCKS     everything that must hold in every frame
```

## The FOV anchor table (never mm)

180° full sky · 107° overhead-wide · 84° wide · 63° environment · 47° normal · 29° short tele ·
18° portrait compression · 12° long tele · 8° extreme detail.

## Retention pacing — the multishot stack

Faceless videos live on cuts: **a new picture every ~2 seconds**. A 10-second block is five shots
with sizes (WIDE / MEDIUM / CU / ECU / DETAIL / OVERHEAD / LOW). To make the model actually cut,
use all four mechanisms together — any one alone fails:

1. **FORMAT MODE names the count:** "five shots, four hard cuts at 2.0 / 4.0 / 6.0 / 8.0 s".
2. **ACTION TIMING** gives each shot its own time range, size and FOV.
3. Within a shot the camera is **physically carried** — it never self-cuts.
4. **POSITIVE LOCKS repeats** the exact cut count and timestamps.

Continuity that must survive a cut (light state, dust, damage, object positions) is restated on
both sides of it. One Seedance 2.5 generation carries **up to 30 seconds** — a three-block segment
can be one take with timed cuts; expect slightly fewer cuts than scripted and check for it.

## Shot types and their recipes

**[live] — photoreal footage.** The signature look: harsh flat midday sun, pale dusty or grey
skies, cool shadows — never golden hour. State it positively in LIGHTING ("flat neutral midday
light, pale grey-dust sky, cool blue-grey shadows, WB locked at 5600K") and lock it ("the light
stays cool and flat in every frame; the palette stays grey-blue to the final frame"). Composition
is never symmetrical: subject on the golden-ratio point (usually the right third), horizon tilted
8-14° and never leveling, a new tilt direction per shot. **No visible humans** — generative anatomy
breaks; stage it positively ("empty plateau, abandoned equipment, ropes running into darkness")
and lock the staging.

**[archive] — sepia handheld beats.** The only place humans are allowed: 10-15 m from camera,
faces small and dark. Recipe: heavy sepia, thick film grain, gate weave, hand-cranked wobble,
slight overexposure blooms, dust and scratches; 4-5 seconds per beat.

**[scheme] — diagrams and charts.** NEVER generated — thin wireframes, moving dots and on-screen
text glitch in video models. Schemes are rendered in code and cut in as full-frame cards. If the
script calls for one, mark the slot and move on; do not write a video prompt for it.

**[pVFX] — practical light effects.** Beams, rim light, glow accents are written as physical light
with explicit color, geometry and behavior ("a cyan beam 0.5 m wide rakes across the wall left to
right over 2 seconds, its spill lifting the stone texture"). For any strike or flash, add the
**anti-impact lock**: the struck object "shudders but keeps its geometry; no debris, no
deformation; the flash lives in light only" — otherwise the model demolishes the subject.

## Camera — always motivated

Every move belongs to something physical: a drift from wind, a jolt from impact, a slow orbit
around the monument, a push-in riding the narration's reveal. Handheld is described by behavior
("overshoot-and-recoil, footstep jolts, breathing drift"), never by the word "shaky".

## AUDIO block formula

The footage carries diegetic sound only — music and voiceover are added in the edit. The standing
line, verbatim, in every prompt: **"NO MUSIC. SFX ONLY — diegetic sound throughout; no score, no
narration, no voices."** Then the concrete bed: wind over stone, distant hum, projector whir,
rope creak — two or three real sounds, named.

## References

Tag assets by load order — `@Image1`, `@Video1` — and never re-describe a tagged asset in prose:
the tag pulls the look. A style frame (e.g. the cyan-glow reference) rides along as `@Image1` with
one line saying what it controls ("controls the glow color and falloff only").

## Checklist before delivering a prompt

- [ ] Everything physical and visible; zero mood-only adjectives; numbers not adverbs
- [ ] No negations anywhere; hard rules restated as POSITIVE LOCKS
- [ ] FOV in degrees from the anchor table; WB in Kelvin; speeds in km/h; haze in %
- [ ] Multishot: cut count + timestamps in FORMAT MODE and again in POSITIVE LOCKS
- [ ] First frame mid-action; every shot ~2 s; continuity restated across cuts
- [ ] [live] look locked: flat cool light, no golden tones, off-center, tilted, unmanned
- [ ] AUDIO line present verbatim + named diegetic bed
- [ ] Impact beats carry the anti-impact lock
