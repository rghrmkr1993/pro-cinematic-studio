# Timeline (EDL): edit recipes

The contract is `$ED/engine/TIMELINE.md`; this page shows how to make typical edits by hand. Frames are **output**
frames, ranges inclusive; `k` = frame index inside a segment (from 0); seconds are output time unless a field is
"source" time. Canvas units are pixels of the full canvas (1080×1920); previews scale them.

Prefer commands: `edit.py cmd EDL '<JSON>'` applies structured edits, ripple edits and low-level `set` / `append` /
`delete` on any path, writes the next version (a JSON list of commands = one new version) and refuses edits that
would break the timeline (`references/point-edits.md`). Hand-edited copies: run `edit.py validate EDL` (both
validators: the planner's contract and the renderer's own check — missing files, bad ranges, overlaps, unknown kinds,
keys outside their segment).
Parameter names live in the registries: `python3 -I $ED/engine/ed_fx.py registry fx|transitions|looks`,
`python3 -I $ED/engine/ed_text.py registry layers|caption_styles`, `python3 -I $ED/engine/ed_sfx.py list`.

## Skeleton

```json
{"canvas": {"w": 1080, "h": 1920, "fps": 30}, "n_frames": 900, "frame_interp": "flow",
 "sources": {"a": {"path": "media/clip1.mp4"}},
 "audio": {"music": {"path": "media/track.wav", "in": 42.0, "fade_out": 0.5}, "loudness": {"lufs": -14, "tp": -1}},
 "segments": [{"id": "C01", "f0": 0, "f1": 59, "src": "a", "t": 12.4, "speed": 1.0, "crop": {"cx": 0.5, "cy": 0.5, "z": 1.0}}],
 "ops": [], "texts": [], "layers": [],
 "qa": {"genre": "epic", "on_beat_share": 0.9, "lufs": -14, "lufs_tol": 1, "tp_max": -1, "safe_zone": "tiktok", "flash_limit_hz": 3},
 "meta": {"genre": "epic", "scenario": "genre", "version": 1, "notes": ""}}
```
Segments are contiguous (next `f0` = previous `f1` + 1; last `f1` = `n_frames − 1`). `sources.<name>`: `path`,
`box` (the live picture: no letterbox bars, or the video window of a screen recording), `logo` (the user's own logo,
inpainted), `mask` (an external subject matte: path or `{"path", "invert", "channel": "luma"|"alpha", "offset",
"fps"}`), `fps` (override).

## Segment: source, crop, speed, picture

| task | edit |
|---|---|
| another moment | `"src": "b", "t": 81.2` — check `t + (f1 − f0 + 1) / fps × speed` ≤ the source length |
| 9:16 crop on a face | `"crop": {"cx": 0.43, "cy": 0.38, "z": 1.2}` — fractions of the box; `z = 1` = the full box height |
| slow push-in | `"crop": {"cx": .5, "cy": .45, "z": 1.0, "to": {"z": 1.15}, "ease": "inout"}` |
| follow a subject | `"crop": {"path": [[0, .62, .55, 1.4], [15, .60, .50, 1.4], [29, .58, .45, 1.45]]}` (`[k, cx, cy, z]`) |
| roll / dutch | `"crop": {"rot": 12}` |
| slow motion | `"speed": 0.5` with `frame_interp: "flow"` |
| speed ramp | `"speed_curve": [[0, 2.4], [8, 2.4], [14, 0.35], [40, 0.35]]` (`[k, rate]`, linear between) |
| exact per-frame timing (freeze, stutter, velocity) | `"times": [t_k, …]` source seconds per frame; a freeze repeats a value (+ `qa.planned_freeze`) |
| motion blur | `"shutter": 0.5` (fraction of a frame: crop / camera motion; on frames played ≥ 1.3× also source time, a motion-compensated smear); `"time_blur": false` turns the source-time part off |
| sharpening | `"sharpen": "auto"` (default: none up to 1.1× enlargement; above it, gentle and adaptive — set from the scale and the source's own noise / texture, held inside the source's local range, so no halos or ringing; motion-blurred frames stay soft) \| `false` \| amount; top level or per segment |
| colour | `"grade": {"preset": "teal", "contrast": 1.15}`; presets `natural, color, warm, cool, teal, desat, bw, bw_hi, bw_dark, bw_soft`; params `auto, exposure, sat, temp, tint, gamma, contrast, black, gain, lift, fade, split, duo` |
| colour by sub-range | `"grades": [{"k0": 0, "k1": 11, "grade": {…}}, {"k0": 12, "k1": 29, "grade": {…}}]` |

HDR sources are tone-mapped to SDR BT.709 at decode; nothing to do by hand.

## Looks

A look = a grade + image fx: `ed_fx.look(name, intensity)` → `{"name", "grade", "fx"}`. By hand: copy its grade into
the segment's `grade` (own overrides on top) and append its fx to the segment's `fx` (each fx carries `"look"`).
Names: `film_print, home_tape, clean_luxe, dreamy_bloom, gritty_contrast, mono_noir, neon_night, golden_hour,
silver_bleach, teal_orange, vivid_pop, pastel_fade, cold_concrete` (aliases: film, vhs, luxury, dreamy, gritty, noir,
bw, neon, golden, bleach, blockbuster, pop, pastel, cold…; `references/style-dna.md` §3). The planner's looks
replace the genre's own vignette, texture, glow and clarity, and are fitted to the footage (at most 7 % of the
picture crushed to black, mean brightness ≥ 60 on normal-key footage unless the user asked for a very dark picture,
faces never clipped); a look added by hand is not fitted — check it with a still sheet or `edit.py frame`.
`clarity` never clips.

## Segment effects: `fx`

Applied in order; gate with `frames: [k, …]`, `t: [t0, t1]` or `times: [t, …]` (output seconds); strength `amt`
(animate with `amt_to` / `amt_keys` + `ease`); `move` keeps the card id for point edits.
```json
"fx": [{"type": "zoom.punch", "frames": [0], "scale": 1.2},
       {"type": "shake.beat", "t": [16.0, 16.3], "amt": 1.0},
       {"type": "defocus", "region": "background", "amt": 0.8}]
```
- **Camera fx** (change the crop warp itself): `zoom.punch`, `zoom.crash`, `zoom.in_out`, `shake.beat`, `roll`,
  `drift`, `handheld`.
- **Image fx**: `bleach, bloom, blur, chroma, clarity, contour_glow, datamosh, defocus, dirblur, duotone, exposure,
  film_overlay, flash, glitch, glitch_blocks, glow, grain, invert, lens_warp, letterbox, light_leak, pixel_art,
  pixel_sort, pixelate, posterize, rgb_split, saturation, shake, smear, tape, vignette, zoomblur`.
- **Subject regions**: any image fx takes `"region": "background" | "subject" | "all"` (or `"behind": true`),
  weighted by the subject matte — `sources.<name>.mask` if given, else a person mask computed on the frame
  (`"auto_mask": false` to skip); `feather`, `expand` move the edge. Colour pop = `{"type": "saturation", "sat": 0,
  "region": "background"}`; lens blur behind the subject = `defocus` with `region: "background"`; a rim light =
  `contour_glow`.

## Transition: `transition_in`

Blends the previous segment into this one. `align: center` — the window is centred on the cut (both sides need
`frames/2` of handle in their sources), `end` — the window ends at `f0 + frames`.
```json
"transition_in": {"kind": "whip", "frames": 6, "align": "center", "params": {"direction": "left", "blur": 0.35}}
```
Kinds: `datamosh, dip, dissolve, fade, flash, glitch, lens, light_leak, liquid, luma, pixel_sort, push, slide, spin,
whip, wipe, zoom`.

## Frame operations: `ops`

`{"f": [frames] | "a:b", "op": "…", "stage": "pre" | "post"}`: `invert`; `white` / `black` (`a` = strength);
`mask_flash` (fills the subject matte); `rect_flash`; `hud_tc`; `flash` `{"color", "curve": [1, .55, .25, .1],
"blend": "screen"}`. Planned black and white frames go into `qa.planned_black` / `qa.planned_white`.

## Text and captions

- `texts` — static blocks `{"f0", "f1", "items": [{"text", "font", "size", "x", "y", "color", "anchor"}]}`.
- `layers` (ed_text): `{"kind", "f0", "f1" | "t0"/"t1" | "dur", "style", "anim_in", "anim_out", "pos", "safe_zone",
  "occlude"}`; kinds: `static, kinetic, beat_text, subtitle, karaoke, title_card, intertitle, lower_third, callout,
  counter, route_map, margin_note, repeat, behind_subject`. Sizes ≤ 1 are fractions (of the height for sizes),
  larger are canvas px. `occlude: true` puts the text behind the person.
- **Caption layers** (`subtitle`, `karaoke`): `"style": "podcast_bold"` (a preset: `podcast_bold, podcast_caps,
  clean, boxed, karaoke_highlight, karaoke_box`; or `{"preset": …, overrides}`); `max_lines` (subtitle presets 3,
  karaoke 2); `fit`: `"reflow"` (default: captions never shrink — lines are measured with the real font, a chunk
  wraps up to `max_lines`, then splits in time at a phrase point, each part ≥ 0.7 s and inside the layer's frames) or
  `"shrink"`; keywords in colour via `highlight.keyword` or `"keywords": ["4 million"]`. Build them from words with
  edit-voice (`ed_voice.subtitle_chunks(…, style=…, canvas=…, breaks=[jump cuts], soft_breaks=[camera cuts])`, or
  `edit.py voice subs … --style --canvas --breaks`); `ed_text.text_fits(text, style, canvas)` checks one line. QA
  judges them as displayed. A line that still runs too wide: a smaller `max_chars` on the layer's `chunk` (or
  `subtitles.max_chars` in a sequence spec).

## Sound: `audio`

```json
"audio": {"music": {"path": "media/track.wav", "in": 42.0, "at": 0, "gain_db": 0, "fade_in": 0, "fade_out": 0.5},
          "voice": [{"path": "media/talk.mp4", "at": 0.0, "in": 24.05, "dur": 8.75}],
          "sfx_level": "normal", "sfx_style": null, "sfx_dir": null,
          "sfx": [{"kind": "whoosh", "at": 7.13, "align": "peak"},
                  {"kind": "impact", "variant": "boom", "at": 7.53, "align": "attack", "level": "strong"},
                  {"kind": "riser", "t": [5.6, 7.5]},
                  {"file": "media/my_hit.wav", "at": 12.0, "level": "normal"}],
          "music_fx": [{"op": "gain", "t": [0, 19.2], "db": -18}, {"op": "swell", "at": 19.2, "dur": 1.5}],
          "duck": [{"under": "voice", "depth_db": 18}],
          "loudness": {"lufs": -14, "tp": -1}}
```
- **Kinds and variants**: `whoosh` (air, swish, heavy, orbit), `reverse_whoosh`, `riser` (noise, short, tonal,
  reverse_cymbal, endless, filter), `swell`, `impact` (punch, boom, soft, metal, stretched, chord, stop), `sub_drop`
  (classic, short, long, reverse), `glitch` (burst, static, transition, trill, blips, censor, hiss, crush), `click`
  (tick, shutter, pop), `scratch`, `tape_stop` (stop, start), `stutter` (repeat, build). Sound style: `cinematic`,
  `trap`, `clean` (from `audio.sfx_style`, else the genre).
- **When**: `"at"` + `"align"` (`attack` = the first loud sample, `peak` = the designed peak — a riser's or a
  reversed sound's end — `start`, `end`) + `offset_ms`; `"dur"` sets the length. `"t": [t0, t1]` (no `at`) = a range
  the event fills, `dur` = t1 − t0 by default: hits, glitches, clicks and `"align": "start"` start on t0; whooshes,
  risers, reverse sounds, swells and `"align": "end"` build across the range and land their peak / end on t1 (a
  synth is lengthened so its build starts on t0; a sample keeps its length). A riser into a drop at 7.5 s:
  `{"kind": "riser", "t": [5.6, 7.5]}` (= `"at": 7.5, "dur": 1.9`). `ed_sfx.event_anchor(event)` returns where an
  event lands; the planners and QA use it.
- **How loud**: `"level": "light" | "normal" | "strong"` (−5 / 0 / +4 dB around the sound's own target against the
  music; aliases subtle → light, heavy → strong; a number = dB) — the normal way. `"lu"` = an absolute level against
  the program (no preset); `gain_db` = an extra trim. `audio.sfx_level` sets the default preset of every event.
  Impacts and sub drops dip the music by themselves (`"duck": false` disables).
- **The user's sounds**: `"file"` on an event (any kind; `pitch` in semitones, `rate`, `stretch`, `reverse`,
  `trim_db`), or `audio.sfx_dir` = a folder (`--sfx-dir` on `edit.py plan`, `"sfx_dir"` in a sequence spec): events
  without a file take the best-named file for their kind (impact / hit / boom…, whoosh / swoosh…, riser /
  uplifter…, sub / 808…); nothing fits → synthesized.
- **Music level**: `music_fx` `gain` (a hold over `t`), `level` (`points`), `swell` (a rise into `at`), `fade_out`,
  `fade_in`; `filter`, `crush`, `stutter`, `tape_stop`, `scratch`, `mute`, `gate`. `duck` under the voice is smooth
  (no pumping between words).
- Every render mixes to WAV, encodes AAC 320 kb/s and re-measures loudness and true peak on the encoded audio; the
  sidecar keeps the per-event placement (`audio.events`: level, need, measured LU, floor) for QA's `sfx` check.

## Insert, delete, move (ripple edits)

```bash
edit.py cmd EDL '{"op": "insert", "at": "0:07", "dur": 0.5, "segment": {"src": "a", "t": 12.0}}'   # or "path": "b-roll.mp4"
edit.py cmd EDL '{"op": "delete_clip", "clip": "#5"}'
edit.py cmd EDL '{"op": "delete_range", "from": "0:07", "to": "0:07.5"}'
```
Through `ed_edl.shift(edl, from_f, delta)`: everything after the point moves (fx times, ops, texts, layers, voice,
SFX, qa marks); the music and its beat grid stay. A clip cut by a delete keeps what its remaining frames showed
(in-point, speed-curve and crop-path keys, grades, fx frames rebased and trimmed) — a jump cut. An inserted clip
takes the look of the clip it joins unless `"grade"` is given.

## Cutaway over speech (the voice continues)

A ripple insert would move the voice too. For B-roll over running speech, split the talk segment at the phrase's
output frames (`ed_voice.find_phrase` → source time → output frame through the piece's `at` / `in`) into before /
insert / after; point the middle piece at the B-roll (`src`, `t`, `crop`, `grade`); leave `audio.voice` alone.
Validate, render the window, check a still sheet.

## Library move → timeline field

| move | in the timeline |
|---|---|
| `zoom.slow`, `zoom.in`, `zoom.out` | `crop` → `to.z` with ease |
| `zoom.punch`, `zoom.crash`, `zoom.in_out`, `shake.beat` | the camera fx of the same name |
| `angle.dutch` · `handheld.shaky` | `crop.rot` · fx `handheld` / `drift` |
| `time.slow_motion` · `time.speed_ramp` · `time.velocity`, `time.freeze` | `speed` · `speed_curve` · `times` |
| `trans.*` | `transition_in.kind` |
| `light.flash` | op `flash` / `white` |
| `fx.*`, `glitch.*`, `look.*` | image fx / a look (card's `engine` field) |
| `type.*`, `gfx.*` | `layers` |
| `sfx.*` | `audio.sfx[].kind` |
| `cut.flash`, `cut.quick`, `cut.jump`, `cut.stutter` | structure: series of short segments |

## Versions, renders, sidecars

Every edit is a new version (`edit.py cmd` does it; by hand: copy to `edl_v(N+1).json`, `meta.version` = N+1, a note
in `meta.notes`, then `edit.py validate`). Partial render: `edit.py render EDL --frames a:b` (no sound); still sheet:
`edit.py render EDL --stills SHEET.jpg --at a:b:4`. Every render writes `OUT.mp4.render.json` (per-frame segments,
transitions, fx and moves, text boxes, timing, module status, the mix and encode numbers, `audio.events`) and
`OUT.boxes.json` (text and op boxes for QA).
