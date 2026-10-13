# Engine primitives (draft vocabulary for the `engine` field)

The edit-director engine assembles a timeline JSON and renders it with ffmpeg/numpy/opencv. Move cards refer to the primitives below. Time is in timeline seconds; `t=[t0, t1]`; `ease` — `linear | inQuad | outQuad | inOutQuad | inCubic | outCubic | inOutCubic | inExpo | outExpo | inOutExpo | hold`. `center`/`target` — `[x, y]` in fractions of the frame or `track(face|person|object:<name>)` (mediapipe/opencv tracking).

If a move needs a primitive that is not on the list, name it in the same style (`snake_case(param=...)`) and describe its parameters; the shared vocabulary is consolidated after the review.

## Geometry and camera
- `transform(scale=[s0, s1], center, rotate=[r0, r1], shift=[[x0,y0],[x1,y1]], t, ease, motion_blur=False|<shutter fraction>)` — keyframed 2D animation of the frame: digital zoom, punch-in, pan across the crop, roll.
- `shake(amp, freq, t, decay, axes='xy'|'rot', seed)` — shake; `beat_shake(...)` — locked to the beats.
- `stabilize(strength)` / `destabilize(profile='handheld')`.
- `reframe(aspect, target)` — crop to an aspect ratio by tracking; if it cuts off something important → Higgsfield `reframe`.
- `outpaint(...)` — extending the frame (Higgsfield) when code runs out of edges.

## Time
- `speed(rate | curve=[[t, rate], ...], interp='blend'|'flow'|'drop')` — speed ramps, slow motion, speed-up (`flow` = optical-flow frames). The planner brakes ramps to 0.4× at most from sources under 50 fps (0.25× from 50 fps and up).
- `freeze(at, dur)`, `reverse()`, `loop(mode='pingpong'|'cycle')`, `step_print(hold=n)`, `echo(trails, decay)`.

## Cuts and transitions
- `cut(at)`, `jump_cut(...)`, `match(on='shape'|'motion'|'color'|'vanishing_point')`.
- `transition(kind, dur, params)` — kind: `dissolve | dip(color) | whip | zoom | spin | wipe(shape) | luma | glitch | flash | morph | nest(quad)`.
- `chain_zoom(clips, per_link, rate, seam, center)` — a chain of zoom-ins.

## Image and color
- `blur(kind='gaussian'|'radial'|'directional'|'zoom', amount, center, t)` — `zoom_blur` = radial motion blur driven by speed.
- `flash(color='white', t, dur, curve)`, `fade(to='black', t, dur)`.
- `color(lut | params)`, `grain(amount, size)`, `vignette(amount)`, `letterbox(ratio, t)`, `glow(threshold, radius)`, `rgb_split(px, angle)`, `chroma_ab(amount)`, `posterize(levels)`, `pixelate(size)`, `datamosh(...)`, `kaleidoscope(segments)`, `mirror(axis)`.

## Masks and compositing
- `mask(method='mediapipe_person'|'face'|'selfie'|'hf_remove_background', feather)`; `composite(layers, blend)`; `split_screen(layout)`.

## Graphics and text
- `text(content, style, anim, t, safe_zone='tiktok')`, `kinetic_text(words, sync='beats'|'words')`, `subtitle(style, karaoke=bool)`, `counter(...)`, `callout(...)`, `shape(...)`.

## Sound
- `sfx(kind, at, gain, align='attack'|'peak', level='light'|'normal'|'strong')` — kind: `whoosh | riser | impact | sub_drop | glitch | click | swell | reverse_whoosh | scratch | tape_stop`; or `sfx(file=<the user's sample>, at, level)`; `sfx(kind, t=[t0, t1])` — a range the sound fills: hits start on t0, builds (whoosh, riser, swell, reverse sounds) land on t1; `duck(music, under=voice)`; `beat_sync(event, grid='1/4')`.
- In the timeline these become `audio.sfx` events and `audio.duck` rules (`engine/TIMELINE.md` §4).
