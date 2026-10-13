# Cinema Studio (researched 2026-10-13)
Labels: (V) vendor-official, (3P) third-party; unverified items carry a [no public source ...] marker. Versions differ in vocabulary; use only the names shown in the selected version.

## Versions (V help center)
- 2.5: AI actors (Soul Cast, up to 3), built-in color grading, no video upload. 6 camera bodies, 10 lens characters, focal 8/14/35/50 mm (3P skill).
- 3.0 (2026-03-30): physics-aware motion, up to 9 refs, 7 genres, 8 speed ramps, native audio, no per-shot start/end frames needed. Video upload to 15s.
- 3.5: AI-assisted directing, Elements (characters, locations, props), team collaboration; Camera panel with body (Clean Digital, Fine Film, Raw 16mm), lens (Vintage Haze, Warm Halation, Anamorphic, Extreme Macro, Clinical Sharp), focal 8/14/35/50/75 mm, aperture; 9 MoveSet styles (Classic Static, Silent Machine, One Take, Epic Scale, Intimate Observer, Impossible Camera, Documentary Snap, Raw Chaos, Dreamy Flow) (3P).
- 4.0 (2026-08-12, default): up to 30s per generation, up to 50 refs, up to 1080p [official, 2026-10-13, blog settings table; the help article states no resolution, the 720p claim is withdrawn], runs on Seedance 2.5, other models usable inside.

## 4.0 Director's Panel (V blog, help center)
- Film Setup: Genre (General, Action, Epic, Drama, Comedy, Horror, Noir); Era (Auto, 60s, 80s, 90s, 2000s, 2020s); Tempo (Auto, Chaotic, Dynamic, Calm, Single Shot).
- Camera: type (Auto, Modern, 35mm Film, 8mm Film, DV Camcorder); lens (Auto, Clean Sharp, Anamorphic, Vintage Anamorphic, Warm Vintage, Halation Vintage); aperture (Auto, f/1.4, f/4, f/11); 30+ movement presets (POV, Robot Arm, Pan, Helicopter, tracking, pedestal down); can stack up to 3 simultaneous moves (3P).
- Character direction: Emotion Wheel per character via @-mention: Hope, Anger, Joy, Trust, Fear, Surprise, Sadness, Disgust [official, 2026-10-13: blog settings table lists these 8; the 6-emotion launch tweet claim is superseded].
- Color Palette: 50+ named templates [official, 2026-10-13: blog says 50+; Director's Panel lighting has 6 presets plus manual]. Lighting: Auto, Silhouette, Practicals, Window, Overhead Fall, Contre-jour, Soft Cross, plus manual color, brightness, diffuse, angle.
- Video modes: References (new clip), Forward/Backward Extend (continue or lead into an uploaded video up to 30s), Edit Video (change an object or face in a region without regenerating).
- Post: color grade (temperature, contrast, saturation, sharpness, grain, highlights, exposure). Team: live multi-user, Element sharing, Canvas, Project Brief, subfolders, Personal Assistant.
- Speed ramps (3.0): Linear, Auto, Flash In, Flash Out, Slow-mo, Bullet Time, Impact, Ramp Up.

## Method (pipeline, V Academy plus blog)
1. Project setup and brief. 2. Pick image model for look-dev (Soul Cinema, GPT Image, Nano Banana Pro). 3. Build LOCATIONS first. 4. Build characters (Soul Cast, AI Influencer, or consented Soul ID). 5. Save all as named Elements (naming system: CHAR_name, LOC_name, PROP_name). 6. Proof the hardest shot. 7. Shoot scene by scene, chaining last frame to first. 8. Spot the slop, fix by edit. 9. Grade the hero frame, match others to it. 10. Upscale finals.

## Prompting rules (3P skill, consistent with V guidance)
- Keep hardware (camera body, lens, aperture, genre) in UI controls, not prompt text.
- Prompt length (verified 2026-10-14): 512 characters is a third-party claim for Cinema Studio 2.5 and 3.0 (OSideMedia skill; no Higgsfield page states it); in 2.5 each @ chip uses about 80-100 hidden characters, max 2 tags. For 4.0 no cap is published and Higgsfield's own 4.0 blog prints a prompt of about 3,400 characters, so 4.0 accepts far more; keep 512 as the safe, cheap default and read the live counter. Method, per-model limits and six examples: `${CLAUDE_PLUGIN_ROOT}/skills/cinematography/references/prompt-compression.md`. Declare @ Elements once in scene 1.
- Identity lives in the Element; prompt describes action. One transformation per shot. Add a still beat at start and end (about 2s) to smooth cuts.
- Write Manual Style as laws (grade, lighting rule, texture, performance register), not "cinematic". Do not stack presets on Manual Style.
- Renderable action: standoffs, near misses, aftermath, walks, turns. Unreliable: precise strikes, kicks, prop combat, close grappling.
- Prompt for story and action, not rig (V blog). Mute native audio if scoring separately.
- Grid generation (introduced in Cinema Studio 2.0): up to 16 variations for the price of a single generation (V PR Newswire, 2026-02-26) [verified prnewswire.com, 2026-10-14]; it applies to the starting image stage, not video renders (3P); not re-confirmed for 4.0 [no public source for 4.0 behaviour as of 2026-10-14; checked: 4.0 blog, help center]. Read the cost on the Generate button.

## Camera and lens choices (practical)
8mm: scale, distortion, avoid on faces. 14-24mm: environments, tension. 35mm: documentary, natural. 50mm: flattering portraits. 75-85mm: compression, intimacy. f/1.4 isolates subject; f/4 balanced; f/11 deep focus for UGC and product clarity. Anamorphic: flares, oval bokeh, widescreen feel. Halation or Vintage: warm film softness. Clean Sharp: product and clinical looks.

## Failure modes
Version vocabulary mix-ups, "May contain protected content" block (remove real faces, IP), location drift, morphing in multi-beat shots, over-long prompts truncated, unreliable fight choreography, version-specific limits on uploads (2.5 none, 3.0 and 3.5 15s, 4.0 30s).

## Official additions [official, 2026-10-13]
- Official 3.5 help lists 10 Camera MoveSet styles, 8 colour palettes, 6 lighting presets (3P counts of 9 MoveSets are superseded). Elements are project-scoped but can be pulled into other projects; Soul Cast actors save via "Save to Elements".
- Why text-only camera prompts vary (blog 2026-10-09): speed, easing and end position are unspecified, so the model guesses. Fix: name speed and easing and an explicit start and end framing, reuse verbatim, rule out the competing move (dolly vs zoom), set aperture (f/1.4, f/4, f/11) and a lighting preset as parameters. Movement presets set register; the prompt still names the move. Genre sets physical logic first (7 genres). Tempo: Auto, Chaotic, Dynamic, Calm, Single Shot.
- Cost: not published; if Cinema Studio models are on your plan's Unlimited list, web generations deduct nothing.
- Academy lessons for film structure: see academy-lessons.md.

Named camera shots with prompts and Cinema Studio settings: see signature-shots.md.
