# Model dialects: how to prompt each model (researched 2026-10-13)
Labels: (V) vendor-official, (3P) third-party, (H) house rule from earlier company research. For Seedance depth, load `seedance-20`. Universal: English for predictability (Seedance and Kling sometimes respond better to Chinese for nuanced motion, V); describe what you want, name only a few key exclusions (V); no contradictions between prompt and image; one change per iteration.

## Seedance 2.0 and 2.5
Formula: Subject, Action, Environment, Camera, Style, Constraints; 60-100 words; open with an aesthetic foundation (H). Image-to-video at 720p first, short prompt (V). References: @character, @style, @motion, @audio. 2.5 modes: text-to-video, omni-reference, video edit, video extension (3P); explicit roles ("@Image1 is the face, @Video1 is camera motion only"). Multi-shot: number the beats with timestamps (0-3s, 3-6s), close "Total: Ns, N shots, aspect" (H). Bracket syntax for audio, dialogue, subtitles (3P). UGC clip block order: Style and Mood, Narrative Summary, Dynamic Description (cuts with "Hard cut to."), Static Description, Audio, Quality tail (H). Failure: camera ignored (use exact terms), drift (anchors or Element), jerky cuts (first and last frame), "fast" degrades (make one element fast).

## Kling 3.0 family
Connected narrative beats per scene (action, setting, camera move, mood), Start and End Frames anchor motion, Elements lock characters, audio on or off (V). Genres and speed ramps shared with Cinema Studio. Use 16:9, 9:16, 1:1 only (2.35:1 is style vocabulary, not output, 3P). Motion Control: character image with arms and hands visible, clean reference video without cuts. Draft on Turbo, finish on full (V).

## Veo 3.1
Cinematic paragraph: subject, action, setting, camera, lighting, atmosphere, then audio line: dialogue in quotes with who speaks, ambient sounds, "no music". Describe weather, global illumination, depth. Avoid brand names, real people, alcohol-adjacent imagery (over-blocks, 3P). 4-8s clips; plan multi-shot via separate clips chained by last frame. Close-up faces softer (3P): use medium shots.

## Cinema Studio
Narrative and action only; rig in UI; see cinema-studio.md.

## Wan 2.6/2.7
Best with a first and last frame or a style reference video; weaker text-only (3P). Short action prompt plus references. Good for product realism and restyle.

## MiniMax Hailuo
Minimal prompts work; strong on facial emotion and text sharpness; use for fast UGC tests (3P).

## DoP
Pick preset, then describe scene; Enhance toggle expands the prompt; sharp composed source image; 3 or 5s (V).

## Soul 2.0 (images)
Layers: subject, details, environment, style, camera; base character neutral studio shot first, then "keep the exact same person, same face and pose, change only wardrobe" (V). Combine preset or Moodboard + Soul ID + HEX; attaching a reference image disables the prompt field (V). Moodboard: 20+ cohesive images, no faces. Anti-slop module in characters-and-consistency.md.

## Soul Cinema
Scene, subject, mood; name the light source (blue hour, twilight, backlight), shallow depth, grain, palette; no cinematography jargon stacking; use result as first frame for Kling or Seedance (V).

## Nano Banana (Pro, 2, 2.1, Lite)
Be explicit on counts and layout; exact on-image text in quotes with font style, size, placement; up to 14 refs, name each reference's role; draft on Lite, final on 2 or Pro; if blurry at high res, generate lower and upscale (V). Product hero: "exactly one [product], front label facing camera, placed on [surface], [light], no other text".

## GPT Image
Typography and color accuracy; give hex values and exact copy; good for storyboards and boards (H).

## Seedream 4.5 / 5.0
Instruction edits and de-slop: "KEEP EXACTLY composition, subjects and product; CHANGE ONLY micro-realism"; list what to avoid (H).

## FLUX 2 / 3, Kontext
Direct, literal prompts; Kontext for context-aware edits and style transfer; FLUX 3 video edit and upscale (V).

## Popcorn
Subject, Setting, Style, Action, Atmosphere per frame; refer to references by number; style keywords first; match input ratio to output (V).

## Recraft / Ideogram
Vector and logos: shapes, colors, flat style; Ideogram for text replacement and transparent backgrounds (V changelog).

## Audio models
Eleven v4: write dialogue with punctuation and emotion cues, language tag; MiniMax Speech: clean TTS; Seed Audio: scene sound with dialogue, music, effects. Specify accent and pace; avoid music with lyrics in ads (H).

## Official prompt rules [official, 2026-10-13]
Help center and blog: specificity is the main lever; layers subject, details, environment, style, camera and mood (video); video prompts read like a shot list (style, camera, light, beat-by-beat action, audio and dialogue timing, shots with durations). Four causes of ignored prompts: choices left open, reference covers appearance only, one dense paragraph, extra people and beats. Fixes: exact age/build/outfit plus a distinguishing detail, block who stands where, camera as physical setup, name every contact point of hands, tie emotion to a visible action, one light source and direction, say what is heard and what must not appear. Multi-person or multi-beat scenes: storyboard in Popcorn first. Seedance camera terms read directly: dolly in, truck left, arc, push in, pull back wide, handheld follow, crane up, orbital. Prompt and image must agree (calm text vs motion-blurred frame conflicts). Academy shot-prompt header and VFX skeleton: academy-lessons.md.

## Universal prompt skeleton (copy and fill)
"[Aesthetic: photoreal, 35mm, natural grade]. [Subject with 2-3 identity anchors]. [Action: start pose to end pose, one hand job each]. [Environment with 3 anchors, one named light source]. [Camera: one move, one direction, speed value]. [Audio line]. [Constraints: exactly one product, no text, no extra hands, no morphing]."

## Prompt length limits [verified 2026-10-14]
Cinema Studio 2.5 and 3.0: 512 characters (3P claim only; 2.5 @ chips cost 80-100 hidden characters). Cinema Studio 4.0: no cap published, official blog prompt about 3,400 characters (V). Seedance 2.0 and 2.5: no official hard cap found, guidance 60-100 words for 2.0, Higgsfield 2.5 guide prompts run 4,900-7,000 characters (V). Kling 3.0: 3,072 hard, 2,500 recommended, 512 per multi-shot beat (V API reference via search). Veo 3.1: 1,024 text tokens, about 4,000 characters (V Gemini API). Nano Banana Pro: 65,536 input tokens, 14 reference images (V). Runway Gen-4.5: none published on readable pages. Method and examples: `${CLAUDE_PLUGIN_ROOT}/skills/cinematography/references/prompt-compression.md`; fps per model: `frame-rates-deep.md`.
