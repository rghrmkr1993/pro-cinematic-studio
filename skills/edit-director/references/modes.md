# Working modes, progress, previews and the final render

## Checkpoints (default)

1. **Plan lines** (≤ 5 lines, `references/briefing.md`). Not a stop: without an open question, keep working.
2. **Plan**: `plan_vN.jpg` + a short table of parts / slots (what goes where and why, the style picked, gaps and how
   to fill them, free or paid with the price) + the engine's notes (lip sync corrected, no clear drop, the automatic
   talk start). Wait for "ok" or changes. A composite's plan without a preview: `edit.py sequence SPEC --project P
   --no-render --background`, poll `edit.py status P`, then `ed_plan.py explain P/edl_vN.json` — a table per part;
   after the "ok", `edit.py render P/edl_vN.json --background` makes the draft and its QA.
3. **Preview**: the draft `preview_vN.mp4` + 3–8 lines of QA + what to listen to. Point edits, as many rounds as
   needed.
4. **Final**: `final_vN.mp4` + QA of the final + one line on what could come next (translation, voice-over,
   publishing, saving the project).
Anything paid is always its own question with the price (edit-gen, edit-voice). "Looks good, go on" after the plan
= the preview; "ok, final" after the preview = the final render.

## Autopilot

On with "do it yourself", "no stops", "straight to the final"; off with "stop, show me the plan". Record `mode` in
`project.json`. The plan lines are still written (defaults stated, no questions); QA findings that can be measured
are fixed in up to two rounds; gaps are filled for free (another moment, code); paid options are listed with prices,
never run. Deliver the final **and** the labeled draft preview of the same version, plus what was measured, what did
not work out and which paid improvements exist.

## Speed and progress

The user cannot see the sandbox: before each heavy step one line (what, why, how long — `references/environment.md`),
then a status line at least every 2 minutes.

```text
Transcribing the interview (45 s of speech, ~1 min) and reading the track (a few seconds)…
Building v1 and its draft preview in the background (854 frames, ~3 min).
v1: planning done, preview 610 / 854 frames, 10 fps, ~30 s left.
Final v3 rendering in the background: 420 / 854 frames, 2.5 fps, ~3 min left.
```
- **Draft by default.** Every `plan`, `sequence`, `variant`, `remake`, `storyboard`, `fill` and `cmd --render`
  renders a draft preview: 540×960, blend interpolation, labels, then QA. `--full` = high-quality preview (optical
  flow), worth it only for judging slow motion and ramps. `edit.py render EDL` = the same draft; `--frames A:B` = a
  window without sound for your own checks; `edit.py frame EDL T --out x.png` = one frame at full size, like the final
  (sharpness, colour, captions at 1:1).
- **Long jobs in the background.** A foreground command that outlives the tool's time limit is killed (a composite
  build with preview and QA: 2–5 minutes). `--background` on `plan`, `variant`, `sequence`, `remake`, `storyboard`
  and `voice transcribe` detaches the job (log + `*.job.json` in the project folder, or next to `--out` for a
  transcript) and returns in under a second with the poll command; `edit.py status $PROJ` shows each job's stage, its
  last log line and, when done, the result or the error, plus the progress of renders.
- **Final in the background**: `edit.py render EDL --final --background`, then `edit.py status $PROJ` (frames, fps,
  ETA from `<out>.progress.json`). Foreground renders print progress every `ED_PROGRESS_S` seconds (default 5).
- **Over budget**: a step running past 2× its estimate → say so, offer a cheaper path (a shorter window, a partial
  render of the part in question, fewer shots).
- **Long sources**: transcription runs once per file (cached; `--background` for long files); the talk analysis
  (camera cuts, faces, overlays) covers only the kept range.

## The plan as an image

`plan_vN.jpg` is written by every planning command (`--no-sheet` skips it); for any version
`edit.py plan-sheet EDL [--at mid|first] [--cols N] [--width PX]`: one tile per segment with the frame that will be
used (crop and grade applied), a big `#N`, output time, part, source moment and moves; gaps and segments without a
usable source are NO SHOT tiles; a storyboard shows its slates. Add a short table from `ed_plan.py explain EDL`
(`#`, time, length, shot, moves, why; a composite gets one table per part, with its frames, source range, sections
and style, then the notes). Remake: `remake/slots.jpg`; composite with a screen recording: check the talk crops
(`references/scenario-composite.md`).

## Labeled preview

Every frame shows a big `#N` (the clip number = the segment's position in this version) and the output timecode;
small: segment id, frame, source time, active moves. The user can say "at #5" or "at 0:07".
- Numbering belongs to a version: keep `edl_vN.json` with `preview_vN.mp4`; resolve `#N` against the version the user
  watched. After inserting or deleting clips, say that the numbers shifted.
- The draft looks a little choppier in motion than the final; say so once.

## Final render

```bash
python3 -I $ED/engine/edit.py render $PROJ/edl_vN.json --final --background    # QA runs after it
python3 -I $ED/engine/edit.py status $PROJ
```
1080×1920 (the canvas), no labels, the best interpolation; H.264 (CRF 17, preset slow), BT.709; the sound mixed to
−14 LUFS / −1 dBTP and encoded as AAC 320 kb/s with loudness and true peak re-measured on the encoded audio. File for
the user: `/mnt/user-data/outputs/<project>_v<N>.mp4`.

## How to talk

- The user's language, briefly, with numbers; no JSON or internal ids in replies (except `#N` and timecodes).
- One round of questions at most; options as "A — …; B — …" with consequences.
- Honest about limits: what was measured, and what needs the user's eyes and ears.
