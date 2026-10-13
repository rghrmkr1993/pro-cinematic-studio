# Plugging generated shots into the timeline

A generated clip differs from its slot in length, fps, framing, light and texture. `edit.py fill` conforms it for
free and writes the next version; hand edits are for special cases.

## 1. Inspect the files

`ffprobe` each (fps, size, duration) and a quick sheet to see the usable span and artefacts (warped hands, faces,
text):
```bash
ffmpeg -v error -i $PROJ/gen/c03.mp4 -vf "fps=4,scale=270:-1,tile=6x4" -frames:v 1 $PROJ/gen/c03_sheet.jpg
```
A broken shot is not plugged in: say what is wrong and offer a prompt fix with a new price.

## 2. Map and fill

`$PROJ/gen/map.json` — one entry per slot; the slot is a segment id (`"C03"`), the `#N` from the plan sheet, or the
slot source (`"slot03"`); the value is a path, or `{"path": …, "t": 1.2}` to force the in-point:
```json
{"C01": "gen/c01.mp4", "#2": "gen/c02.mp4", "C03": {"path": "gen/c03.mp4", "t": 1.2}}
```
```bash
python3 -I $ED/engine/edit.py fill $PROJ/edl_v1.json $PROJ/gen/map.json      # or inline JSON; --out, --no-render, --full
```
Per slot `fill`: analyses the clip, picks the best window for the slot's role and speed mapping (the action peak on
the planned accent), slows a too-short clip to fit (reported in `meta.gaps` as `stretched`), crops on the subject
with the planned zooms and tilt, gives the planned grade the clip's exposure and the genre's colour fit, and moves
punch / crash centres onto the subject. Generated clips are usually well exposed already: auto exposure adds at most
+0.6 EV to them, the look's colour push follows the clip's own cast, and an enlarged crop gets only gentle,
halo-free sharpening (none up to 1.1×). Then the next version, the plan sheet, a draft preview and QA. The user's
own clips can fill slots the same way.

## 3. Check

The plan sheet (no NO SHOT / slate tiles left where clips were given), QA (`GAPS` gone from the verdict for filled
slots; `image` — including brightness jumps over 20 % at hard cuts —, `faces`, `cuts` as usual), a "neighbour | shot
| neighbour" still sheet for colour and motion direction, and one full-size frame for texture and sharpness
(`edit.py frame EDL T --out f.png`). Fix single slots with point edits (`edit.py cmd`: a swap, a crop, a grade) — or
regenerate after a new "yes".

## 4. By hand (special cases)

Insert a clip as a source and segment (`references/edl-cookbook.md` in edit-director): fps differences are
interpolated (`frame_interp`), `t` sets the in-point, `speed` 0.8–1.0 stretches a short clip, `crop` frames 9:16 (a
window under ~1080 source px looks soft — upscale is paid, `references/ai-tools.md`), `grade` matches the neighbours
(brightness within ~15 %), the same `grain` / look as the neighbours, a transition at the join if the genre allows.

## 5. Provenance

`$PROJ/gen/provenance.json`: one record per shot (`slot`, `job_id`, model, prompt, Elements, price, date, file, the
span used) — for an honest "made with AI" label when publishing and for repeats. Generated files need not go into the
project archive beyond what `edit.py pack` stores; they can be downloaded again by `job_id`.
