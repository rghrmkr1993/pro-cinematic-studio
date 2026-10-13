# Edit Studio engine — project file (EDL) and module contracts

One JSON file is the whole project ("project = code"). `ed_edl.py` renders it frame-exactly. Every other module
either **produces** an EDL (genre planner, sequence planner, storyboard, remake drafter, voice tools) or is **called
by the renderer** (fx, text, sound, QA). Module docstrings describe what is installed; where they and this file
disagree, the docstring is right.

Frame numbers are output frames (inclusive ranges). Times in seconds are output time unless a field says
"segment-relative" (k = frame index inside a segment, 0-based) or "source" (seconds of a source file). Canvas units
are pixels of the full canvas (1080×1920 for 9:16); previews scale them (`scale` = 0.5).

## 1. Top level

```json
{
 "canvas": {"w": 1080, "h": 1920, "fps": 30},
 "n_frames": 521,
 "frame_interp": "flow",                        // nearest | blend | flow (source fps -> output fps)
 "sharpen": "auto",                             // auto | false | amount (gentle, halo-free; only crops enlarged > 1.1x)
 "sources": {"<name>": {"path": "...", "box": [x0, y0, x1, y1], "logo": [x0, y0, x1, y1], "mask": "...", "fps": 30}},
 "audio": {...},                                // §4
 "segments": [...],                             // §2
 "ops": [...],                                  // §3
 "texts": [...],                                // static text items (ed_edl docstring)
 "layers": [...],                               // §5 (ed_text)
 "qa": {...},                                   // §6
 "meta": {...}                                  // §7
}
```
`sources.<name>`: `box` = the live picture in source px (without letterbox bars, or the video window of a screen
recording: `ed_video.content_box`); crops are fractions of it. `logo` = the user's own logo (inpainted near crop
windows). `mask` = an external subject matte (path or `{"path", "invert", "channel": "luma"|"alpha", "offset", "fps"}`)
decoded and warped like the picture (region fx, `mask_flash`, layers). `overlays` = declared static graphics
boxes that QA keeps out of talk crops (detected ones are added). HDR sources are tone-mapped to SDR BT.709 at
decode; untagged HD is read as BT.709.

## 2. Segments (one shot on screen)

```json
{"id": "C01", "f0": 94, "f1": 129, "src": "film", "t": 303.5, "part": "hype", "note": "...",
 "speed": 1.0,                                   // or "speed_curve": [[k, rate], ...] (linear between)
 "times": [303.5, 303.53, ...],                  // optional: exact source second per frame (freeze, stutter, velocity)
 "interp": "nearest",                            // per-segment override of frame_interp
 "crop": {"cx": .5, "cy": .5, "z": 1.0, "rot": 0, "to": {...}, "ease": "inout", "path": [[k, cx, cy, z], ...]},
 "border": "reflect" | "black", "shutter": 0.5, "time_blur": true, "sharpen": "auto",
 "grade": {"preset": "bw_hi", ...}, "grades": [{"k0": 0, "k1": 11, "grade": {...}}],
 "fx": [{"type": "<fx>", "frames": [k, ...] | "t": [t0, t1] | "times": [t, ...], "amt": 1.0, "move": "<id>", ...}],
 "transition_in": {"kind": "<transition>", "frames": 6, "align": "center" | "end", "params": {...}},
 "ghosts": [...], "alts": [...]}
```
- `crop`: `cx, cy` = window centre as fractions of the box, `z = 1` = the window spans the full box height; `to`
  animates cx / cy / z / rot to the segment's end; `path` keys are segment frames.
- Motion blur: `shutter` (fraction of the frame interval) blurs crop / camera motion; on frames played ≥ 1.3× also
  source time, along optical flow (a smear, no double contours); `time_blur: false` turns that part off.
- `fx` in order. Camera fx (fold into the crop warp): `zoom.punch`, `zoom.crash`, `zoom.in_out`, `shake.beat`,
  `roll`, `drift`, `handheld`. Image fx: `bleach, bloom, blur, chroma, clarity, contour_glow, datamosh, defocus,
  dirblur, duotone, exposure, film_overlay, flash, glitch, glitch_blocks, glow, grain, invert, lens_warp, letterbox,
  light_leak, pixel_art, pixel_sort, pixelate, posterize, rgb_split, saturation, shake, smear, tape, vignette,
  zoomblur`. Every image fx takes `region` (`background` | `subject` | `all`), `behind`, `feather`, `expand`,
  `auto_mask` (weighted by `sources.mask`, else a person mask). Registry: `ed_fx.py registry fx`.
- **Looks** (`ed_fx.LOOK_PRESETS`: `film_print, home_tape, clean_luxe, dreamy_bloom, gritty_contrast, mono_noir,
  neon_night, golden_hour, silver_bleach, teal_orange, vivid_pop, pastel_fade, cold_concrete`; `ed_fx.look(name,
  intensity)` → `{"name", "grade", "fx"}`): the look's grade becomes the segment's `grade` (own overrides on top) and
  its fx are appended to `fx`, each carrying `"look": name`. The planner's looks replace the genre's own vignette,
  texture, glow and clarity and are fitted to the footage (`ed_plan` `fit_grades`: ≤ 7 % of pixels crushed, mean
  luma ≥ 60 on normal-key footage unless `dark`, faces unclipped).
- `transition_in` kinds: `datamosh, dip, dissolve, fade, flash, glitch, lens, light_leak, liquid, luma, pixel_sort,
  push, slide, spin, whip, wipe, zoom`. `align: center` = the window is centred on f0 (both sides continue frames/2
  in their sources); `end` = the window ends at f0 + frames.

## 3. Frame ops (absolute frames)

`{"f": [frames] | "a:b", "op": "...", "stage": "pre" | "post", ...}`: `invert`, `white` / `black` (`a`), `mask_flash`
(fills the subject matte), `rect_flash`, `hud_tc`, `flash` `{color, curve: [1, .55, .25, .1], blend: "screen" |
"normal" | "add"}`.

## 4. Audio (ed_sfx mixes it; full spec in the ed_sfx docstring)

```json
"audio": {
 "copy": false,                                             // true: mux "path" (reference audio) untouched
 "music": {"path", "in": 0, "at": 0, "dur": null, "gain_db": 0, "fade_in": 0, "fade_out": 0.5, "speed": 1.0},
 "voice": [{"path", "at", "in", "dur", "gain_db": 0, "lufs": null, "norm": "source" | "clip"}],
 "sfx_level": "normal", "sfx_style": null, "sfx_dir": null, "genre": null,
 "sfx": [{"kind", "variant", "at" | "t": [t0, t1], "align": "attack" | "peak" | "start" | "end", "offset_ms": 0,
          "dur", "level": "light" | "normal" | "strong" | dB, "lu": null, "rel_lu": null, "gain_db": 0,
          "pan": 0 | [p0, p1], "width": 1, "seed", "style": null, "duck": null | true | false | {...},
          "file": null, "pitch": 0, "rate": 1, "stretch": 1, "reverse": false, "trim_db": -50, "synth": false,
          "params": {}}],
 "music_fx": [{"op": "gain" | "level" | "swell" | "fade_out" | "fade_in" | "filter" | "crush" | "stutter" |
               "tape_stop" | "scratch" | "mute" | "gate", ...}],
 "duck": [{"under": "voice", "depth_db": 8, "mode": "smooth", ...}, {"under": "sfx" | "sfx:<kind>", ...},
          {"t": [t0, t1], "to": -60}],
 "key": null, "grid": {"bpm", "beats", "downbeats"}, "loudness": {"lufs": -14, "tp": -1, "max_gr_db": 8},
 "base_dir": null, "debug": {"stems": "<dir>"}
}
```
- **Event kinds** (`ed_sfx.KINDS`): `whoosh, reverse_whoosh, riser, swell, impact, sub_drop, glitch, click, scratch,
  tape_stop, stutter` with variants (`ed_sfx.py list`); `tape_stop`, `scratch`, `stutter`, `glitch:crush`,
  `riser:filter` process the music itself. Sound style `cinematic` | `trap` | `clean` (event `style`, else
  `audio.sfx_style`, else the genre).
- **Time**: `at` + `offset_ms` is where the anchor lands (`attack` = the first sample above −20 dB of the peak;
  `peak` = the designed peak — a riser's or reversed sound's end). `t: [t0, t1]` without `at` = a range the event
  fills (`dur` = t1 − t0 by default): attack / start aligned events (hits, glitches, clicks, the music kinds,
  `"align": "start"`) start on t0; peak / end aligned ones (whooshes, risers, reverse sounds, swells, `"align":
  "end"`) build across the range and land on t1 (a synth is lengthened so its build starts on t0; a sample keeps
  its length). `ed_sfx.event_anchor(event)` = the landing time; the planners and QA use it.
- **Level**: `level` = a preset around the sound's target loudness against the program (music + voice): `light`
  −5 dB, `normal` 0, `strong` +4 (aliases: soft / subtle / quiet → light, heavy / loud / hard → strong; a number =
  dB); `audio.sfx_level` = the default; `lu` = absolute (no preset); `rel_lu` = legacy card scale; `gain_db` = trim.
- **Files**: `file` = the user's sound (any kind or none; trimmed, anchored like a synth); `audio.sfx_dir` = a folder
  whose best-named file is used for events without one (else synthesized).
- **Audibility** (shared with ed_qa): events within 150 ms form a group; its loudest 400 ms on the SFX bus vs the
  program's 3 s short-term loudness; need = `QA_MIN_LU` (impact 3, whoosh 0, riser 0 LU) + the level preset +
  `gain_db`; the mixer raises / dips until each group meets it. Every placed event records `st_lu`, `need_lu` and
  `floor_db` (the dB the audibility floor added above the level rules).
- `ed_sfx.mix(audio, total_s, out_wav)` → `{lufs, tp, sfx_count, events, audibility, limiter, warnings, ...}`;
  `ed_sfx.encode_audio(wav, out, codec='aac', bitrate='320k', tp_max=-1.0, lufs=None, lufs_tol=0.5)` → the delivery
  AAC, re-limited until the **encoded** file meets the true peak; `ed_sfx.validate_audio(audio, total_s)` →
  `(errors, warnings)` for the validators.

## 5. Layers (ed_text)

`{"kind", "f0", "f1" | "t0"/"t1" | "dur", "blend", "opacity", "safe_zone", "style", "anim_in", "anim_out", "pos",
"occlude"}`; kinds `static, kinetic, beat_text, subtitle, karaoke, title_card, intertitle, lower_third, callout,
counter, route_map, margin_note, repeat, behind_subject` (`ed_text.py registry layers`).
**Caption layers** (`subtitle`, `karaoke`): `words` / `chunks` / `lines`; `style` = a caption preset (`podcast_bold`,
`podcast_caps`, `clean`, `boxed`, `karaoke_highlight`, `karaoke_box`; aliases) or `{"preset", ...overrides}`;
`max_lines` (presets: 3, karaoke 2); `fit`: `reflow` (default — never shrink: lines measured with the real font,
wrap up to `max_lines`, then split the chunk in time at a phrase point, both parts ≥ 0.7 s, inside the layer's
f0..f1) | `shrink`; keyword highlight (`highlight.keyword`, `keywords`); `avoid: "face"` moves a chunk off the face
and keeps its ink and the pop-in's peak inside the safe zone. `ed_text.split_caption_layer(layer, ow, oh, fps)`
returns the chunks as displayed (QA counts these); `fit_caption_layers(layers, …)` splits explicitly;
`text_fits(text, style, canvas, max_lines)` → `{fits, lines, width_px, max_px, size_px, n_lines}` checks a line as
the renderer wraps it; `caption_hints(name, ow, oh, text=None)` → `{max_chars, max_lines, max_px, …}` for producers.
Fonts: OFL files in `engine/assets/fonts`; CJK faces (OFL; `engine/models/LICENSES.md`) are fetched on first use
into `~/.cache/edit-studio/fonts`.
`ed_text.render_layer(layer, f, fps, ow, oh, scale, ctx=None) -> (rgba premultiplied, blend) | None`.

## 6. QA (ed_qa)

`ed_qa.run(edl_path, video_path, out_dir) -> dict` (also `qa.json`, `qa.md`, sheets). Checks (`qa.json` `checks`):
`format, cuts, rhythm, loudness, frames, flashes, safe_zone, faces, image, speech, parts, sfx`; storyboards add the
`GAPS` verdict. Among them: `cuts` accepts a boundary made visible by a planned punch / shake / crop-scale jump
(`accent`); `frames` warns on slow motion below 0.4× from ≤ 30 fps sources unless `qa.interp`; `image` leaves
letterbox bars out and warns on brightness jumps over 20 % at hard cuts inside music parts; `speech` measures lip
sync on the render (`ed_sequence.estimate_av_offset`, warn over 2 frames); `parts` judges static overlays only inside
their `spans`; `sfx` places events with `ed_sfx.event_anchor`. Thresholds (`qa` block, all optional): `genre, kind
(music | speech; planners declare it), words, on_beat_share, on_word_share, grid_tol_frames, source_cuts, lufs,
lufs_tol, tp_max, planned_black, planned_white, planned_freeze, freeze_min_s, black_luma, white_luma, frame_ratio,
flash_limit_hz, red_flash_limit_hz, flash_area, flash_delta, safe_zone, color, first_word_max, max_pause,
allowed_pauses, planned_pauses, max_cps, min_sub_s, max_sub_lines, max_static_s, click_db, voice_over_music_db,
interp, drop_tol_frames, drop_f, drop_at, sfx_min_lu, parts`. Details: the ed_qa docstring.

## 7. Meta and producers

`meta`: `genre`, `scenario` (`genre` — speech plans add `kind: "speech"` — | `storyboard` | `sequence` | `remake`),
`version`, `notes`,
`history` (point edits), `options` (what the planner was given), `parts`, `slots`, `gaps`, `grid`, plus:
- **Genre plans**: `meta.parts` = `{"hook" | "build" | "drop" | "outro": {"t": [t0, t1], "f": [f0, f1], "bars"}}`.
- **Style and versions**: `meta.style` (preset name), `meta.variant` (int), `meta.choices` = what this version picked
  (`style, variant, seed, match, dark, transitions, transitions_at, looks, look, look_pick {i, name, intensity,
  rotation}, grade, nuance, caption_style, sfx_style, sfx_level, accent_swaps, shots, ramps` — one row per ramped
  slot: pattern, brake beat, rates, braking / speed-up frames, exit) — the next version's `avoid` reads it.
- **Gaps**: `meta.gaps` = `[{"slot", "id", "part", "role", "kind": "missing" | "stretched" | "reused" | "weak" |
  "storyboard", "reason", "fill", "t", "f", "dur", "need_s", "brief"}]`; `brief` (edit-gen) = `{shot_size, subject,
  action, camera, duration {slot_s, source_s, handles_s, generate_s}, speed, continuity, look, aspect, fps, prompt}`.
  Storyboards add `meta.storyboard` (`brief`, `character`, `slots` timing / speed mapping / zooms / grade, `filled`).

Producers:
- `ed_plan.plan_genre(track, footage, genre, canvas, fps, dur=None, **opts)`; opts: `style`, `variant`, `avoid`,
  `n_shots`, `order`, `require_moves`, `forbid_moves`, `music_in`, `drop_at`, `drop_t`, `bpm`, `bars`, `cut_rate`,
  `sfx_level`, `in_sequence`, `interp` (deep slow motion from < 50 fps sources accepted: floor 0.25× instead of
  0.4×), `dark` (relaxed picture limits), `check_dark`, `fit_grades`, `check_cuts`, `check_flash` (default on),
  speech: `words`, `lang`, `src_in` / `src_out`, `from` / `to`, `subtitles`, `music_db`, `voice`.
  `ed_plan.resolve_style(text, genre=None)` → `{name, score, genre, matched, why}` (English words; `matched: false`
  = the default style); `STYLE_PRESETS` (18); `look_rotation(preset)`; `explain(edl)` → the slot table (composites:
  one table per part).
- `ed_plan.plan_storyboard(track, genre=None, style=None, dur=None, brief=None, canvas, fps, n_shots=None,
  character=None)` → every slot a slate + a gap with a brief; `ed_plan.fill_gaps(edl, {slot: path | {"path", "t"}})`.
- `ed_plan.apply_command(edl, cmd)` (point edits; composites: `part` = id, `id.section`, or a section);
  `ed_plan.validate_edl(edl)` → `(errors, warnings)` (uses `ed_sfx.validate_audio`).
- `ed_sequence.plan_sequence(spec, cache_dir=None, log=print)`, `variant(edl, variant, style)`, `resolve(spec)` (§8).
- `ed_remake.draft(reference, footage, out_dir, canvas, fps, music=None, music_in=None)`, `repick`,
  `measure_effect(clip, fps=None, sheet=None)` → `{events, candidates: [{move, score, params, why, apply}]}`.
- `ed_voice.transcribe`, `find_phrase(words, text, after=None, before=None, min_score=0.7)`, `find_phrase_all`,
  `reaction_end(media, t, words=None, max_s=4.0)`, `setup_starts(words, end_t, min_s=6, max_s=25, env=None)`,
  `clip_candidates`, `speech_segments`, `remap_words`, `subtitle_chunks(words, …, kind=None, fps=30, style=None,
  canvas=None, breaks=None, soft_breaks=None)` (phrase-aware; `breaks` never crossed, `soft_breaks` preferred).
- `ed_video.content_box(path, t0, t1)`, `static_overlays(path, box, t0, t1)` → `[{box, kind: logo | text | ui |
  popup, coverage, spans}]`, `shot_cuts`; `ed_reframe.speaker_crop(path, t0, t1, box=None, avoid=None, canvas, fps,
  words=None)` → `[{t0, t1, crop {cx, cy, z, path?}, shot, speaker, face, subject}]`.
- `ed_sequence.estimate_av_offset(video, t0, t1)` → `{offset, measured, lag, r, confident, why}` (lip sync of a source
  or a render), `clean_starts(words)`; `ed_sfx.event_anchor(event)`; `ed_text.text_fits`, `caption_hints`.

## 8. Sequence spec (ed_sequence)

`edit.py sequence SPEC --project P` (or `ed_sequence.py plan SPEC --out EDL`, `resolve SPEC`, `variant EDL`,
`example`). The full key list is in the ed_sequence docstring and in edit-director's
`references/scenario-composite.md`; in short:
```json
{"canvas": {"w": 1080, "h": 1920, "fps": 30},
 "style": "gritty street", "variant": 0,
 "parts": [
   {"type": "talk", "id": "talk", "source": "interview.mp4",
    "from": {"phrase": "the real question is"}, "to": {"phrase": "three million a year", "end": "after_reaction"},
    "remove": [{"phrase": "Let me check my notes."}], "crop": "speaker", "subtitles": "podcast_bold", "music_db": -18},
   {"type": "edit", "id": "hype", "footage": ["g1.mp4", "g2.mp4"], "order": "given", "genre": "epic",
    "bars": 5, "shots": 5, "moves": ["time.speed_ramp"], "sfx": "heavy"}],
 "music": {"path": "track.wav", "drop_at": {"part": "hype", "at": "start"}},
 "transitions": [{"from": "talk", "to": "hype", "kind": "flash", "sfx": "impact"}]}
```
Spec keys added since the first version: top-level `sfx_dir` (the user's sounds → `audio.sfx_dir`); talk `from`:
`{"auto": true, "max_s": 25}` or missing (the first clean sentence; a source over 90 s: the best setup sentence ≤
`max_s` before the end); talk `av_offset` (default: measured and corrected when confident and ≥ 2 output frames;
`0` = as recorded).
Output: segment ids `T01…` / `E01…` / `K01…` (each with `part`); `audio.voice` per kept range; `layers` = captions
(chunked with the preset and the canvas; jump cuts and part ends hard breaks, camera cuts soft); `qa` in speech mode
+ `qa.parts`, `qa.planned_freeze` (slivers held at a range edge), `qa.source_cuts`;
`meta.parts` = **a list** `[{"id", "type", "f0", "f1", "t0", "t1", "segments", …}]` — talk / clip: `source`, `keep`,
`av_offset`, `lip_sync` (what was measured and done) (+ `tighten_pauses` when set); edit: `genre`, `bars`, `shots`,
`engine`, `sfx`, `drop_frame`, `style`, `variant`, `sections` `{"hook" | "build" | "drop" | "outro": [f0, f1]}`
(absolute frames). `meta.style`, `meta.variant`, `meta.choices`; `meta.sequence` = the music decision (a track with
no clear drop: the biggest energy jump, with a note), transitions, per-part decisions and the input `spec`;
`meta.validation` = `{errors, warnings}`; `meta.notes`.

## 9. Rendering (ed_edl)

`python3 -I ed_edl.py EDL OUT.mp4 [--preview] [--labels] [--frames a:b] [--interp nearest|blend|flow] [--workers N]
[--fast] [--no-sidecar]`; `--stills SHEET.jpg --at first | a:b:step | f1,f2`; `--validate`. Through `edit.py
render`: the draft (540×960, blend, labels — the default), `--full` (optical flow), `--final` (full size, no
labels, the best interpolation; x264 CRF 17 preset slow; previews CRF 20 veryfast), `--background` + `edit.py
status`; `edit.py frame EDL T --out x.png` = one frame at full size, rendered like the final. RGB → YUV 4:2:0 with
the BT.709 matrix and tags. Progress on stderr every `ED_PROGRESS_S` s (frames, %, fps, ETA). Each segment is
decoded only over the region and at the size its crops need; a crop enlarged more than 1.1× gets adaptive
sharpening (from the scale and the source's noise / texture floor, held inside the local range: no halos).
Labels: a big `#N` and the output timecode; small: segment id, frame, source time, active moves.
Sidecars: `OUT.mp4.render.json` (per-frame segment ids, transitions, ops / fx / moves applied, text and layer boxes,
`label_box`, timing, module status, `audio` {mix lufs / tp, `encode` {lufs, tp, …}, `events` [{i, kind, at, start,
end, level, need_lu, st_lu, floor_db, …}], `audibility`}, `edl_md5`) and `OUT.boxes.json` (OUT without extension:
`{"canvas": [W, H], "frames": {"<f>": [[x0, y0, x1, y1, id, kind, flags…]]}}` — layer ink boxes and op boxes).
`ed_edl.shift(edl, from_f, delta)` inserts (delta > 0) or removes frames before `from_f`: everything after it moves,
the music and its grid stay, a cut segment's keys are rebased and trimmed.

## 10. Validation

`edit.py validate EDL` runs both `ed_plan.validate_edl` (the contract of this file, including the audio block via
`ed_sfx.validate_audio`) and `ed_edl.validate` (files, frame ranges, overlaps, unknown fx / transition / layer kinds,
keys outside their segment). Planners validate their own output; `sequence` and `variant` stop with exit code 2 on
errors (the timeline is kept, not rendered; `edit.py render` renders it anyway), and `edit.py cmd` refuses an edit
that would break the timeline (`"force": true` writes it anyway; a JSON list of commands is one new version).
