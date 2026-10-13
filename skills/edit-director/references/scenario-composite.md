# Composite videos: parts in order (`edit.py sequence`)

A composite is any video built from **two or more parts in a given order** on one canvas with one soundtrack: a talk
moment followed by a hype edit, intro → edit → outro, a talk clip with an inserted shot, several talk moments
joined. One JSON spec describes the parts; `ed_sequence.plan_sequence` plans each part with the right engine (talk
and clip parts by words and camera shots, edit parts by the genre planner on the beat grid), joins them and returns
an ordinary EDL. `E="python3 -I $ED/engine"`.

Signals: "first … then …", "up to his reaction", "then the edit", "intro", "outro", "after she says …". Never squash
these into one genre plan, and never use the talk source as footage for a music edit.

Contents: 1. Pipeline · 2. Spec reference · 3. What the planner does · 4. Output · 5. Worked example ·
6. Versions and point edits · 7. Troubleshooting

## 1. Pipeline

1. **Plan lines** (`references/briefing.md`) → the spec `$PROJ/spec_vN.json`. Start from
   `$E/edit.py sequence --example > $PROJ/spec_v1.json`; `//` and `#` comments are allowed; relative paths resolve
   against the spec's folder.
2. **Cheap facts**: `ffprobe` every file; `$E/edit.py track TRACK $PROJ/track.json`; a transcript per talk source
   (`$E/edit.py transcribe SRC $PROJ/voice/words.json`, cached; a long source: `edit.py voice transcribe SRC --out
   $PROJ/voice/words.json --background`; the planner transcribes by itself when `transcript` is not given).
3. **Resolve** — where the phrases land and which drop is used, no video work:
   `$E/ed_sequence.py resolve $PROJ/spec_v1.json`. Check each talk range (first / last words, removed spans, the
   reaction end, length) and the music drop. A phrase in the wrong place → `occurrence`; not found → show the user
   the nearest transcript lines with timecodes. A talk part without `from` shows its automatic start here: name it
   to the user (quote + timecode).
4. **Plan checkpoint**: `$E/edit.py sequence $PROJ/spec_v1.json --project $PROJ --no-render --background` (the
   first run analyses every source; a foreground command that outlives the tool's time limit is killed), poll
   `$E/edit.py status $PROJ` (stage, the last log line, the result or the error), then
   `$E/ed_plan.py explain $PROJ/edl_vN.json` — a table per part (time, length, shot, moves, why) and the notes. Show
   the plan sheet `plan_vN.jpg`, the parts, and the notes that matter (lip sync corrected, no clear drop, a start
   skipped because the picture was hidden, a held sliver). A spec or validation error stops it with exit code 2 and
   the reason; a timeline with validation errors is kept but not rendered.
5. **Preview**: `$E/edit.py render $PROJ/edl_vN.json --background` (the draft, then QA; `--full` = a high-quality
   preview). On autopilot steps 4–5 are one call: `edit.py sequence SPEC --project $PROJ --background`.
6. **Preview checkpoint**: QA (`references/qa.md`: `parts`, `speech`, `sfx` matter most here) + what to listen to
   (the join, the reaction, the drop).
7. **Changes**: cut points, lengths, order, style → edit the spec and rebuild (the analysis is cached: seconds to a
   minute); one spot → `edit.py cmd` (§6).
8. **Final**: `$E/edit.py render EDL --final --background`, then `$E/edit.py status $PROJ`.

## 2. Spec reference

Seconds are **source seconds** of a part's file unless a key says otherwise. `ed_sequence.py example` prints what
the installed engine supports.

**Top level**

| key | value |
|---|---|
| `canvas` | `{"w": 1080, "h": 1920, "fps": 30}` |
| `parts` | ordered list; each part has `type` (`talk`, `edit`, `clip`) and `id` (default: type + index) |
| `music` | `path`; `drop_at`: `{"part": ID, "at": "start" \| "end" \| seconds into the part}` or just the part id; `drop`: track second of the drop (default: the strongest downbeat that leaves enough track for the parts after it; a track with no clear drop: the biggest bass / loudness rise on a downbeat, with a note that suggests another section or track); `in`: track second at output 0 (overrides the alignment); `gain_db` (0); `fade_in` (0.6); `fade_out`. Without `drop_at` the drop lands on the first frame of the first edit part |
| `transitions` | `[{"from": ID, "to": ID, "kind": KIND, "frames": 4, "sfx": "auto" \| "none" \| kind \| [kinds]}]`; KIND = `cut`, `flash` or a transition kind (`dissolve`, `dip`, `fade`, `whip`, `zoom`, `spin`, `wipe`, `luma`, `lens`, `glitch`, `pixel_sort`, `light_leak`, `liquid`, `push`, `slide`). Default talk/clip → edit: flash + auto SFX; otherwise a cut |
| `sfx` | the default SFX amount of every part: `none`, `light`, `genre` (default), `heavy` (`references/briefing.md` §3) |
| `sfx_dir` | a folder of the user's sound effects (relative to the spec): every event takes the best-named file for its kind, else it is synthesized |
| `loudness` | `{"lufs": -14, "tp": -1}` |
| `subtitles` | default caption settings for talk parts (same forms as the part key) |
| `end` | `{"fade": s}` — fade to black at the very end (default 0.27 s when the last part is an edit) |
| `qa` | extra keys for the EDL's `qa` block |
| `style` | a house style for every part: preset name or plain words (`references/style-dna.md`) — the edit parts' planner style (genre defaults to the style's), the talk parts' caption preset, the default join from the style's palette |
| `variant` | version number (int, default 0): re-seeds choices inside the rules; cut points and the drop stay |
| `avoid` | earlier versions (EDL paths or dicts) whose `meta.choices` the new one steers away from |

`style`, `variant` and `avoid` may also sit on one part (the part's key wins) — except that a talk or clip part's own
`avoid` means its overlay boxes; earlier versions go there as `avoid_versions`.

**`talk` part** — speech cut on words

| key | value |
|---|---|
| `source` | the video with the speech; `transcript` (a words JSON, optional); `lang`; `vocab` (names the recogniser splits, joined for matching and captions) |
| `from` | seconds, `"0:24.05"`, `{"phrase": "…", "occurrence": 1, "snap": "pause" \| "word" \| "sentence", "pad": 0.0}`, `{"auto": true, "max_s": 25}` (the best setup sentence at most `max_s` before the end), or missing: the first clean sentence (not a fragment cut off by the recording, not one whose picture is hidden by a pop-up or shows no face); a source over 90 s without `from` gets the setup start |
| `to` | seconds or `{"phrase": "…", "end": "phrase" \| "after_reaction" \| "sentence", "max_s": 4, "pad"}` |
| `remove` | `[{"phrase": "…"} \| "phrase" \| {"from": …, "to": …} \| [t0, t1], …]` |
| `tighten_pauses` | `null` (natural) or seconds: longer pauses are shortened to this; the reaction is kept |
| `crop` | `"speaker"` \| `"center"` \| `{"cx", "cy", "z"}`; `box` (live picture inside a screen recording; detected by default); `avoid` (overlay boxes; detected logos, lower thirds, watermarks, UI by default, and a pop-up while it is on screen); `max_zoom` (1.45) |
| `push` | `true`: a slow push-in on the punchline and the reaction |
| `punch_ins` | `true` or seconds: motivated zoom cuts (≤ ×1.12 on the face) inside camera shots longer than 4 s — numbers, sentence starts, the punchline |
| `av_offset` | seconds the source's audio lags its picture (the picture is taken that much earlier). Default: measured (`estimate_av_offset`, mouth motion vs the speech envelope) and corrected when the estimate is confident and ≥ 2 output frames; `0` keeps the recording as is |
| `subtitles` | `"subtitle"`, `"karaoke"`, a caption preset (`podcast_bold`, `podcast_caps`, `clean`, `boxed`, `karaoke_highlight`, `karaoke_box`), `null`, or `{"kind", "style", "pos", "max_chars", "max_lines", "max_words", "pace": true}`. Default: the house style's preset, else `podcast_bold` |
| `audio` | `"voice"` (default) \| `"mute"` |
| `music_db` | the bed under this part (−18); `swell`: `{"s": 0.6, "to_db": …}` \| `false` (the bed rises into a following edit part and is at full level on its first frame) |
| `grade` | a grade for the part |

**`edit` part** — a music edit on the beat grid

| key | value |
|---|---|
| `footage` | videos or globs |
| `order` | `"given"` (shot i = file i) \| `"auto"` (scored) |
| `genre` | a genre slug (default: the style's genre) |
| `bars`, `shots` | length in bars; number of shots (5 in 5 bars = one bar each) |
| `moves`, `forbid` | required / forbidden move ids or families |
| `sfx` | `none`, `light`, `genre`, `heavy` |
| `engine` | `auto` (the genre planner when its result honours frames, shot count, order, music in-point and the required moves; else the recipe), `planner`, `recipe` |
| `ramp` | `{"fast": 2.5, "slow": 0.4}` (recipe speed ramps; from sources of 45 fps and up the slow rate goes to 0.3); `grade`; `seed` |

**`clip` part** — a piece of another video between parts (B-roll, an establishing shot): `source`, `from`, `to`
(seconds or phrases), `crop` (`"auto"` = as `speaker` \| `"center"` \| `{…}`), `audio` (`"voice"` \| `"mute"`),
`speed` (1.0), `subtitles` (null), `music_db`, `punch_ins` (false).

## 3. What the planner does

- **Start**: without `from`, the first clean sentence; a long source (over 90 s) or `{"auto": true}`: the best setup
  sentence at most `max_s` (25) before the end — sentence starts after a pause, questions and topic openers first,
  leading "and / but" and pronouns pointing back penalised. A start whose picture is hidden by a pop-up or shows no
  face is skipped (note: `start at … s skipped: …`).
- **Cut points** sit in the quiet part of the pause next to the word, never past the next word's onset; a phrase
  starting or ending inside connected speech moves the point to the nearest pause (≤ 1.5 s). Removals cut on the
  word boundary and keep the joined pause short. `after_reaction` keeps the sigh, face-palm or one-word "wow" and
  ends just before the next sentence.
- **Lip sync**: each talk source's audio lag is measured; when the estimate is confident and ≥ 2 output frames the
  picture is shifted to match (note: `lip sync: the source audio lags the picture by 0.12 s - corrected`). Scans are
  keyed by the source window, so a new `av_offset` re-plans in seconds.
- **Framing**: camera cuts inside the kept ranges become segment boundaries on the exact source frame; every camera
  shot gets its own 9:16 crop (`ed_reframe.speaker_crop`: the active speaker, the face whole, logos, lower thirds and
  UI out, a pop-up out while it is on screen). No piece under 0.5 s at a range edge: the in / out point moves onto the
  camera cut when no word is spoken there, else the sliver holds the neighbouring shot's frame (`qa.planned_freeze`).
- **Captions**: `ed_voice.subtitle_chunks` gets the preset and the canvas; jump cuts (removed text) and the part's
  ends are hard breaks no chunk crosses, camera cuts soft ones (preferred boundaries, dropped when a chunk would get
  too short or too fast). Lines are fitted by their real rendered width, so they never overflow. The part's
  `tighten_pauses` is recorded so QA judges the pauses that are left.
- **Music**: the track is placed so its drop lands on the edit part (`drop_at`); the bed under talk parts follows
  `music_db` and swells into the edit part. No clear drop: the switch lands on the biggest energy jump, with a note.
- **Edit parts**: the genre planner (style, variant, required moves, SFX amount; ramps rotate four curves so
  neighbouring shots differ) or the recipe — one shot per bar on the downbeats, speed ramps anchored on each clip's
  action peak, a hold punch-in at every brake, motion blur on fast frames, a heavy shake on the drop.
- **Join**: the default talk → edit join is a flash; with a style, or on later versions, a punchy kind rotated per
  version (the style's flash / cut / zoom / whip / glitch / light leak; without a style flash, zoom, cut). `auto` SFX
  = an impact at `light`, riser + impact + sub drop at `genre` / `heavy` (a whoosh for whip / zoom joins). A part that
  starts on the drop always gets its level's drop package minus what the part already places on its first frame.

## 4. Output

An ordinary EDL: segment ids `T01…` (talk), `E01…` (edit), `K01…` (clip); every segment carries `part` and a `note`
(speaker pick, punch-in word, push-in); talk segments use exact source frames. `audio.voice` = one entry per kept
range; `audio.music_fx` = the bed level and the swell; `audio.sfx` from transitions and edit parts (with `level`);
`layers` = captions; `qa` in speech mode for talk parts with `qa.parts`.
`meta.parts` = `[{"id", "type", "f0", "f1", "t0", "t1", "segments", …}]`: talk/clip parts add `source`, `keep`,
`av_offset` and `lip_sync` (what was measured and done), and `tighten_pauses` when set; edit parts add `genre`,
`bars`, `shots`, `engine`, `sfx`, `drop_frame`, `style`, `variant` and `sections` `{"hook" | "build" | "drop" |
"outro": [f0, f1]}` (absolute frames). `meta.style`, `meta.variant`, `meta.choices` (the edit part's picks + the
transitions and punch-ins, for the next version); `meta.sequence` = the music decision (drop, in, why, candidates),
transitions, per-part decisions (ranges, removals, reaction, box, overlays, crops) and the input `spec`;
`meta.validation` = `{"errors", "warnings"}`; `meta.notes` = the notes printed after the build. Held slivers go to
`qa.planned_freeze`, the source's own camera cuts to `qa.source_cuts`.

## 5. Worked example (invented content)

**Request**: "From chef.mp4 (a screen recording of a cooking stream): start where she says 'nobody salts the water
enough', end after the audience laughs at 'two whole spoons'; cut 'hang on, the timer'. Vertical, only her. Then a
fast edit of my 6 plating shots in order, two beats each, speed ramps, the drop when it starts. Bold captions."

**Plan lines**:
```text
1) Talk from chef.mp4: "nobody salts the water enough" → the laugh after "two whole spoons"; "hang on, the timer" cut;
   vertical speaker crop (stream UI and channel logo kept out).
2) Edit: your 6 plating shots in order, speed ramps, the drop on its first frame, flash + impact on the switch.
~20 s · 9:16 · captions podcast_caps on the talk only. Starting now.
```
**Spec** (`$PROJ/spec_v1.json`):
```json
{"canvas": {"w": 1080, "h": 1920, "fps": 30},
 "parts": [
  {"type": "talk", "id": "talk", "source": "media/chef.mp4", "lang": "en",
   "from": {"phrase": "nobody salts the water enough"},
   "to": {"phrase": "two whole spoons", "end": "after_reaction"},
   "remove": [{"phrase": "hang on, the timer"}],
   "crop": "speaker", "subtitles": "podcast_caps", "music_db": -18},
  {"type": "edit", "id": "plates", "footage": ["media/p1.mp4", "media/p2.mp4", "media/p3.mp4",
                                               "media/p4.mp4", "media/p5.mp4", "media/p6.mp4"],
   "order": "given", "genre": "product", "shots": 6, "bars": 3, "moves": ["time.speed_ramp"], "sfx": "heavy"}],
 "music": {"path": "media/track.wav", "drop_at": {"part": "plates", "at": "start"}},
 "transitions": [{"from": "talk", "to": "plates", "kind": "flash", "sfx": "impact"}]}
```
**Resolve** → read the talk range, the reaction end and the drop; **build** (`--background`, poll `status`) → read
`meta.parts` (talk 0:00–0:13, plates 0:13–0:20), `explain`, the plan sheet and QA; tell the user what to listen to:
the laugh and the switch. Had the request named only the end ("the bit that ends with the laugh at 'two whole
spoons'"), the spec would have no `from`, `resolve` would print the chosen start (`start: first clean sentence -
"Here's my one rule..." at 2.41 s`), and the plan lines would quote it so she can move it.

## 6. Versions and point edits

- **Another version**: `$E/edit.py variant $PROJ/edl_v2.json --variant 2 [--style "dreamy retro"] --background`
  re-plans the stored spec with the next unused variant, avoiding the given version: the cut points by words and the
  drop stay; looks (the style's rotation), moves, shot windows, ramp curves, punch-ins, the join and the caption
  sibling preset change. `--avoid` is ignored for composites (put earlier versions in the spec's `avoid`).
- **Point edits**: `edit.py cmd` works on composites — `"part"` is a part id (`"plates"`), `"plates.drop"`, or a
  section (`hook` / `build` / `drop` / `outro`) of the edit part at `"at"` / `"clip"`; the edit part's genre rules
  apply. Changing a cut point, length, order or the style → edit the spec and rebuild (a rebuild drops point edits
  made on the old EDL: re-apply them from `meta.history` or say what was reset).

## 7. Troubleshooting

| symptom | cause → fix |
|---|---|
| the talk starts or ends in the wrong place | the phrase matched another occurrence → `"occurrence": 2`, or quote more words; check with `resolve` |
| the automatic start is not the one the user wants | give `from` as a phrase, or `{"auto": true, "max_s": 15}` for a shorter lead-in |
| the lips are out of sync | QA `speech` warns over 2 frames (judge it on a `--full` or final render; the estimate is weaker at preview size) → set the part's `av_offset` to the measured lag and rebuild; `0` keeps the recording |
| the reaction is cut off | `to` without `"end": "after_reaction"`; a long reaction → `"max_s": 6` |
| a half sentence remains after `remove` | remove the whole sentence (quote it fully) or use `[t0, t1]` |
| the logo / lower third / UI shows in the vertical crop | QA `parts` names the overlay → add its box to the part's `avoid`, or set `box`; report it |
| the face is cut or the wrong person is framed | QA `parts` / `faces` → `"crop": {"cx", "cy", "z"}` on that part, or `edit.py cmd` on that segment's crop |
| the picture is soft in the talk part | the crop zoom over a small source picture → lower `max_zoom`, or AI upscale (edit-gen, paid) |
| the drop misses the switch | `music.drop` (the track second the user hears) or `music.in`; QA `parts` checks the drop on the boundary |
| note "no clear drop in this track" | the switch sits on the biggest energy jump; tell the user, offer another section (`music.in` / `drop`) or another track |
| the sound on the switch is weak | QA `sfx` → `"sfx": "heavy"` on the edit part, or louder events (`references/edl-cookbook.md`, Sound) |
| captions too fast or too long | QA `speech` (characters per second, lines) → another preset, `"max_words"`, `"max_lines"`, `tighten_pauses: null` |
| a caption line runs past the safe zone | should not happen (lines are fitted by their rendered width); if it does: `"subtitles": {"style": …, "max_chars": 20}` |
| a brightness jump between two shots of the edit part | QA `image` → that shot's grade / exposure, a look at lower intensity, or a transition there; in hard-contrast genres it can be intended — say so |
| `edit.py sequence` stops with exit code 2 | a spec or validation error, printed in one line → fix the named key |
| the build was killed or nothing came back | it ran in the foreground past the tool's limit → run it with `--background` and poll `edit.py status $PROJ` |
