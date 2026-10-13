# Self-check: reading QA and acting on it

You do not see the video or hear the sound. After every render the engine **measures** the file it wrote (the MP4
itself, after encoding) and writes frame sheets — judge by those, and tell the user what was checked: "cuts on the
beat 27 of 29 (±1 frame); −14.1 LUFS, −1.2 dBTP; every sound effect audible; no unplanned black frames; faces whole".
Never "watched it, all good".

```bash
python3 -I $ED/engine/edit.py qa $PROJ/edl_vN.json $PROJ/preview_vN.mp4      # [--out DIR] [--json]; runs after renders anyway
```
Thresholds come from the timeline's `qa` block (the planner fills it from the genre card), then the genre card,
then defaults. Outputs in `qa_vN/`: `qa.json` (`status`, `verdict` lines, `parts`, `gaps`, `checks`), `qa.md`,
`qa_issues.jpg`, `qa_cuts_N.jpg`, `qa_rhythm.png`, `qa_loudness.png`.

## Reading order

1. `qa.md` / the verdict lines (`WARN cuts: …`, `FAIL parts: …`); `edit.py qa` prints every one.
2. `qa_issues.jpg` — frames with the problem marked (text zone, faces, black, frozen, flashes, talk framing: the
   render next to what the crop should show). Start here on any `fail`.
3. `qa_cuts_N.jpg` — f−1 | f | f+1 around every boundary (green exact, blue hidden or transition, grey invisible by
   design or a slate, red off-frame, orange missing / flash frame / soft transition rendered hard, magenta
   unexpected).
4. `qa_rhythm.png` (cuts on the beat grid for music parts, on word spans for talk parts) and `qa_loudness.png`.
5. The look across segments: `edit.py render EDL --stills $PROJ/qa_vN/stills.jpg --at first`; one frame at full size
   (sharpness, colour, captions at 1:1): `edit.py frame EDL 0:07.5 --out $PROJ/qa_vN/f.png`.
6. Sound: the numbers, then the user's ears at named spots ("the impact at 0:19, the laugh at 0:12").

## Checks and what to do

| check | measures | on warn / fail |
|---|---|---|
| `format` | frame count, duration, fps, size vs the timeline | a cut-off render → render again; an audio of another length → check `audio.music` / `voice` |
| `cuts` | every boundary shows its cut on its own frame: `exact`, `masked` (under a flash), `soft` (invisible by design), `transition`, `accent` (no clear step, but a planned punch, shake or crop-scale jump ≥ ×1.08 on the cut frame makes it visible), `gap` (next to a storyboard slate); bad: `offset` (1–4 frames off, fail), `missing` (adjacent pieces of one shot), `flash_frame` (a one-frame shot), `hard` (a soft transition rendered as a cut), unexpected cuts (a shot change inside a segment's source range, with the fix) | unexpected cut → move `t` or shorten the segment; `missing` → another moment or a transition; `flash_frame` at a source camera cut → shift the boundary to the source cut; `offset` → report it (renderer timing) |
| `rhythm` | music parts: share of cuts within ±1 frame of the beat / half-beat grid vs `on_beat_share`; talk parts: share of cuts outside words (default: all) | all cuts shifted alike → the music `in` / drop is off, not the plan (`references/music.md`); single cuts off → `edit.py cmd` timing; a cut inside a word → move it to the pause |
| `loudness` | integrated LUFS and true peak of the encoded MP4 vs `lufs ± lufs_tol`, `tp_max`; the renderer's own numbers next to it | the levels in `audio` (music `gain_db`, voice, SFX `level`), the target in `audio.loudness`; a big gap between MP4 and renderer numbers = audio replaced after the render |
| `frames` | black / white / frozen frames beyond the planned ones (a static source shot is reported as such; held slivers at a talk part's camera cuts are planned); slow motion below 0.4× from a source of ≤ 30 fps (synthesized frames show) | a gap between segments, a source that ends before its slot (`t` + length × speed), a too-dark grade; planned ones go to `qa.planned_*`; too-deep slow motion → a slow rate of 0.4 or more on that segment, or 50 fps footage (`qa.interp: true` only when the user accepts interpolated frames) |
| `flashes` | WCAG-style flashes in every 1 s window vs `flash_limit_hz` (3), red flashes separately | remove or soften `flash` / `white` ops or flash transitions there; ramps and velocity shots that flicker → normal speed |
| `safe_zone` | ink boxes of all text vs the zone (`tiktok`: x 0.06–0.88, y 0.12–0.80) | titles and other text layers: the layer's `pos` / size. Captions are fitted by their rendered width and should not overflow; if one does, shorter lines: `"subtitles": {"style": …, "max_chars": 20}` in the spec (or `max_chars` on the layer), or another preset |
| `faces` | faces cut by the frame edge, text over faces, the main face lost by the crop | `crop.cx/cy`, a smaller `z`, a `path`; captions `avoid: "face"` / another position; AI reframe (edit-gen, paid) |
| `image` | per segment (picture area only: letterbox bars are left out): luma p1 / p50 / p99, crushed / clipped %, saturation vs `qa.color` (with a tolerance); **brightness jumps** — at a hard cut inside a music part the mean brightness changing by more than 20 % (and ≥ 6 levels) | the segment's grade or look intensity; a jump → match that shot's exposure / grade to its neighbour, or put a transition there; in hard-contrast styles a jump can be intended — say so instead |
| `speech` | talk parts: first word ≤ 0.3 s after the part starts; pauses > `max_pause` (inside shots only beyond the planned ones when pauses were tightened); captions **as displayed** (reflowed up to the layer's `max_lines`, chunks split in time judged one by one): ≤ 20 characters/s, ≥ 0.7 s on screen, lines ≤ `max_lines`; the longest stretch without a visual change; clicks at audio seams; **lip sync** of every talk part measured on the render (warn when the audio lags the picture by more than 2 frames with a confident estimate) | a late first word → the part's `from` / `snap`; long pauses → `tighten_pauses`; fast captions → another preset, `max_words`, fewer removals; a static stretch → `punch_ins: true` / `push`; a click → move the cut into a quieter pause; lip sync → the part's `av_offset` (the lag QA measured) and rebuild — judge it on a `--full` or final render, the estimate is weaker at preview size |
| `parts` | composites: parts tile the timeline, every part boundary is a cut; the strongest drop lands on the edit part's start (or its `drop_frame`) ±1 frame (a track with no clear drop: the nearest downbeat); talk framing: the render matches the crop of the source, the speaker's face whole and found where the crop puts it; static overlays (logo, lower third, UI, pop-ups) outside the crop windows — judged only while each is on screen, i.e. inside its `spans` (≥ 25 % visible = fail) | drop off → `music.drop` / `in`; render mismatch → re-render, then report; face lost → that segment's crop; an overlay visible → its box into the part's `avoid` |
| `sfx` | audibility of every sound effect on the rendered soundtrack, by the mixer's own rule: each event placed where the mixer anchors it (`ed_sfx.event_anchor`: a range `t` lands on t1 for risers and whooshes, on t0 for hits), a group of events within 150 ms vs the program (music + voice) around it; need = impact +3 LU, whoosh / riser 0 at the normal level (light −5, strong +4); weak = more than 1 LU under the need; each group also shows `floor_db`, how far the mixer's audibility floor already lifted it | `"level": "strong"` on the event, `"sfx": "heavy"` for the part, a deeper music dip, or the user's own sample (`references/edl-cookbook.md`, Sound); weak although `floor_db` is already high → the mixer ran out of headroom: a deeper music dip there or a denser sound (another variant, the user's sample), not more gain; `unverified` = measured on a render from another mixer version — re-render |

Storyboards (animatics) are QA'd differently: the verdict starts with `GAPS` (the slots still to fill, with their
briefs); slates are not judged as pictures.

## Self-correction

- Fix measurable `fail` and clear `warn` yourself and re-render — at most two rounds in a row; then show the user and
  explain what does not add up.
- Matters of taste (which shot, how many effects) go to the user as an option, not a silent change.
- After a point edit: a partial render of the window (`--frames a:b`) and a still sheet around it; full QA on the
  next full preview.

## Final

QA runs again on the final (loudness and true peak on the encoded file). Give the user 3–6 lines: what was measured,
what is within norms, what is left for their ears. TikTok requirements: `references/publish.md`.
