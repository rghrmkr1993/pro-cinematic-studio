# Remakes of a reference edit, and named effects from an example clip

Two uses of someone else's video: **remake** — "do this edit, but with my footage" (the reference's exact timing,
moves, flashes and text positions, filled with the user's shots) — and **named effects** — "a whip / VHS rewind /
crash zoom like the real one" (measure a short example clip and apply the matching move cards with their
parameters). We take timing and technique, never the reference's footage, text, logos or sound design into the
package or the user's output. `E="python3 -I $ED/engine"`.

## 1. Getting the reference

- The user sends the **file**, a **screen recording**, or a **direct link** to a file they have the rights to.
  YouTube / TikTok / social-platform downloading is not supported (terms and copyright): ask for one of the three.
- Reference media lives in the project folder (`$PROJ/refs/`, `$PROJ/remake/`): never in `/mnt/user-data/outputs/`,
  never in the skill. `edit.py pack` never stores a remake's reference video; sheets that show reference frames
  (`slots*.jpg`, `compare_vN.jpg`, measure-ref sheets) are not packed either.

## 2. Remake: draft

```bash
$E/edit.py remake --ref $PROJ/refs/ref.mp4 --footage a.mp4 b.mp4 --project $PROJ             # reference audio as is
$E/edit.py remake --ref $PROJ/refs/ref.mp4 --footage a.mp4 --music clean_track.wav --project $PROJ   # a clean track
```
Writes `edl_vN.json`, `$PROJ/remake/` (`slots.jpg` + `slots_pNN.jpg` = reference frame | top-5 candidates per slot,
`survey.jpg` + `survey_pNN.jpg` = every shot of the footage with its time, `candidates.json`, `decomposition.json`),
a draft preview, QA and `compare_vN.jpg` (reference | remake per slot). Options: `--canvas`, `--fps` (default: the
reference's), `--sample-fps` (footage analysis rate, default 3), `--music-in S` (skips the music alignment),
`--background` (detached; poll `edit.py status $PROJ` — the footage index of long files takes minutes the first time).
Several footage files are indexed separately and merged; sources are named after the files. `--music` aligns the
clean track to the reference audio automatically (no match → it starts at 0 with a warning; set `--music-in`).

What the draft does: a frame-exact breakdown of the reference (cuts, regrades, punches; white / black / inverted /
partial-flash frames; text without OCR → placeholders), per-slot descriptors (subject, scale, motion, light, colour /
B&W), the best candidate from the footage per slot (no overlaps, diversity), a 9:16 crop on the subject, the
reference's camera move mapped to the crop, a grade fitted to the slot, frame ops copied exactly.

## 3. Remake: review flow

The draft matches looks, not meaning: a remake with different footage is a translation of roles ("hands on a
keyboard" may become "hands over a fire").
1. Read `slots_pNN.jpg`: each row = the reference slot and its top 5 (green = chosen); the tag shows subject type /
   scale and B&W; `candidates.json` has the numbers behind every tile.
2. Read `survey_pNN.jpg` (or `survey.json`): every shot of the footage with its time. Pick moments that play the same
   role as the reference slot (subject, scale, motion direction, light), not the same object.
3. Swap: `$E/edit.py remake --project $PROJ --pick S05=12:34.5 "#7=b@0:41.2"` (SLOT = `S05` or `#5`; TIME = `12:34.5`
   or `SOURCE@1:02`; `--edl` / `--version` = the version to start from). Crop, grade and blur are recomputed for the
   new moment; hand-added fx and transitions stay. Then check `compare_vN.jpg` (red = the look differs a lot).
4. **Text**: the draft places `X…` placeholders where the reference had text (position, size, timing). The words come
   from the user; copy the reference's words only if the user decides so and they are not someone else's slogan,
   brand or quote.
5. **Sound**: the reference audio keeps every baked-in accent in place; with `--music` the reference's rhythm sits on
   the new track's grid (`references/music.md`).
6. QA (`references/qa.md`): every boundary a cut on its own frame (`cuts`), `offset` = timing error, unexpected cut =
   a shot change inside a slot's source range.
A remake has no variants (its timing is the reference); other versions = other picks. Point edits as usual
(`edit.py cmd`, `references/point-edits.md`).

## 4. Named effects: "like the real one"

When the user names an effect or transition and wants it like the original, and has no clip:
1. **Find an example**: search the web (any site) for a short clip or GIF that shows the effect cleanly. Show the user
   the link and what it shows; download only after their OK, and only a **direct GIF / MP4 file** (not a platform
   page): `curl -sSfL "<direct url>" -o $PROJ/refs/whip.mp4`. A blocked fetch → say so and ask for a file; do not
   work around it.
2. **Measure**:
   ```bash
   $E/edit.py measure-ref $PROJ/refs/whip.mp4 --sheet $PROJ/refs/whip_sheet.jpg      # --from 0:12.5 --to 0:15 on a long clip
   ```
   It prints the events (cut, flash / dip with opacity and decay, whip axis and direction, zoom scale / duration /
   easing, roll, shake amplitude / rotation / decay, speed ramps and freezes, RGB split) and the move cards that
   reproduce them, best first, each with params and an `apply` line. `--json` gives the whole measurement, `--top N`
   more candidates. Look at the sheet: frames with the events marked + the curves. A still clip gives no candidates.
3. **Apply**: fill the `apply` line's `"at"` (output time), `"between"` (two clips) or the clip id and run it:
   `$E/edit.py cmd $PROJ/edl_v3.json '{"op": "add", "move": "shake.beat", "at": "0:07", "params": {"profile": "heavy",
   "amp": 0.049, "rot": 1.77, "tau": 0.111}}' --render`. For a new plan, require the move instead
   (`edit.py plan … --require trans.whip`, spec `"moves"`), then set its params with `cmd`.
4. Tell the user what was measured and applied ("a whip to the right over 6 frames, as in the example") and that the
   example clip stays in the project only.

## 5. Gaps in a remake

A slot with no fitting shot: code (a zoom or crop from another shot), another moment (`--pick`), or generation
(edit-gen: the brief has the slot's duration, scale, motion and neighbours' light; paid, explicit "yes").
After the project: offer to save the reference's rhythm as a style DNA — numbers only (`references/style-dna.md`).
