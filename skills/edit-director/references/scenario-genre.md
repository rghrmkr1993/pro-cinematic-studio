# Music edits: footage + track + genre or style (`edit.py plan`)

The main scenario. Input: the user's footage (video and photos), a track, and a genre or a style in plain words
("clean and expensive", "gritty street"). Output: a timeline cut to the music, a plan sheet, a draft preview with
numbered clips, QA; later versions and the final. `E="python3 -I $ED/engine"`.

Contents: 1. Plan lines · 2. Track and footage · 3. Genre or style · 4. Plan · 5. Speech genres · 6. Versions ·
7. Gaps · 8. Storyboard (a whole video to generate) · 9. Checkpoints and final · 10. Rules easy to forget

## 1. Plan lines

At most 5 lines (`references/briefing.md`): the footage and its order, the track window ("from the drop", "0:42"),
length, format, the genre or the style preset the words picked — with the reason in one line. Style words are
matched in English: translate the user's words first.
```bash
$E/ed_plan.py styles "clean and expensive, a bit retro"     # {"name", "score", "genre", "matched", "why"}
```
`matched: false` (score 0) = nothing matched: the genre's default style is used; say so and offer 2–3 presets
(`references/style-dna.md`). A request with parts in order is a composite (`references/scenario-composite.md`).

## 2. Track and footage

- `$E/edit.py track TRACK $PROJ/track.json --plot $PROJ/track.png` — tempo, beats, sections, drops
  (`references/music.md`). The planner analyses the track itself; this is for you to explain the plan.
- `$E/ed_analyze.py source SRC $PROJ/src/<name> --fps 8` — a shot sheet of a source, when you need to see the
  material. The planner does its own analysis per clip (cached in `$PROJ/.ed_cache`).
- Phone HDR (PQ / HLG) is tone-mapped to SDR BT.709 by the engine; rotation and variable fps are handled at decode.
  Photos work as sources (slow zoom, parallax).

## 3. Genre or style

- **Genre** (`genres/<slug>.md`, 15): structure, rhythm, shot selection, move limits and bans
  (`references/genres.md`; summary `python3 -I $ED/scripts/find_move.py --genre <slug>`).
- **Style** (`ed_plan.STYLE_PRESETS`, 18 house styles, `references/style-dna.md`): a recipe on top of a genre — the
  genre itself when none is given, a rotation of 2–3 `ed_fx` looks (grade + texture; the look's fx replace the
  genre's own vignette, texture, glow and clarity), a transition palette, preferred and avoided moves, a caption
  preset, an SFX style and level, pacing. The genre card's rules and colour targets still hold. `--style` takes a
  preset name or the user's words (in English).

## 4. Plan

```bash
$E/edit.py plan --track T.wav --footage a.mp4 b.mp4 c.mp4 --style "gritty street" --project $PROJ
$E/edit.py plan --track T.wav --footage *.mp4 --genre epic --dur 30 --project $PROJ
$E/ed_plan.py explain $PROJ/edl_v1.json          # parts by seconds + per slot: what was placed and why
```
Writes `edl_vN.json`, `plan_vN.jpg`, a draft preview and QA (`--no-render` = timeline only, `--full` = HQ preview).
The first run analyses every clip (cached in `$PROJ/.ed_cache`): add `--background` and poll `edit.py status $PROJ`
when that plus the preview may take more than a couple of minutes. Other flags: `--canvas 1080x1920`, `--fps 30`,
`--seed`, `--title`, `--word`, `--outro-text`, `--no-reframe`, `--sample-fps`.

The user's wishes are planner options (`edit.py plan` flag / `ed_plan.plan_genre` option):

| the user says | flag | what it does |
|---|---|---|
| "5 shots" | `--n-shots 5` | exactly 5 shots; a cut always lands on the drop beat; even lengths on the beat grid |
| "in this order" | `--order given` | shot i from footage file i (the window inside the clip is still chosen); default `auto` |
| "with speed ramps", "slow-mo", "a freeze" | `--require time.speed_ramp` | the move appears even where the card does not list it (a ramp on every shot of an `--n-shots` plan, else on the drop shots) |
| "no shake", "no glitch" | `--forbid shake.beat fx.glitch` | never placed, sounds included (ids or families) |
| "start the track at 0:42" | `--music-in 42` | the track second at output 0 (snapped to a beat) |
| "the drop at 0:08" | `--drop-at 8` | the output second where the strongest drop lands |
| "the drop is at 1:05 of the track" | `--drop-t 65` | overrides the drop detector |
| "it's 140 BPM" · "8 bars" · "20 seconds" | `--bpm 140` · `--bars 8` · `--dur 20` | tempo hint · length |
| "faster cutting" | `--cut-rate 1.5` | × the card's cutting rate (shots split at strong beats; < 1 merges) |
| "no / subtle / lots of sound effects" | `--sfx-level none` / `light` / `heavy` | `light` = the switch only; `genre` (default: the genre's or the style's) = the card's program + a thump on every ramp brake + a whoosh or riser into the switch; `heavy` = also whooshes on speed-ups, risers into every section, hits on the drop's downbeat cuts, a sub drop under the drop hit |
| "use my sound effects" | `--sfx-dir DIR` | events take the best file of the folder for their kind (filename and folder keywords); none fits → synthesized |
| a style / another version | `--style …` · `--variant N` · `--avoid EDL …` | §6 |

What the planner does: a track window of whole bars (the drop where the genre expects it, or where you fixed it),
hook / build / drop / outro on bars, a cut grid from the card's rhythm snapped to downbeats and hits, shot selection
by the card's profile (the best readable shot on the drop, action peaks on accents, one use per shot; a window with
a camera cut the analysis missed is re-picked), 9:16 crops that never cut a face at the edge, moves from the genre's
parts within the limits (no camera accent in the two frames just outside a hard transition), SFX per the level, QA
thresholds (`qa.kind = "music"`), and the reasoning per slot in `meta` (read it with `explain`).
- **Speed ramps**: four ramp curves (brake beat, slow depth, entry and exit) rotate, so neighbouring shots never
  share one; the slow floor is 0.4× from footage under 50 fps (deeper shows synthesized frames) and 0.25× from 50 fps
  and up. A shot without real motion plays at normal speed.
- **Colour**: every shot's grade is fitted to the card's targets on decoded frames — faces never clip; at most 7 % of
  the picture crushed to black and a mean brightness of at least 60 on normal-key footage (style words such as "very
  dark", "low key" or "pitch black" relax this); a look's push is eased along the footage's own colour cast and keeps
  near-neutral highlights neutral; auto exposure adds at most +0.6 EV to well-exposed footage; in epic, calm, travel,
  drama, fashion, teaser, product and motivation, neighbouring shots at a plain cut stay within 15 % brightness.
- **Flashes**: velocity, ramp and stutter shots are counted with the QA's flash metric on their graded frames; one
  near the limit is re-picked or plays at normal speed.

## 5. Speech genres (clips, ugc, explainer) and voice-overs

The same command cuts on words when the genre's kind is speech (the track is optional):
```bash
$E/edit.py plan --footage talk.mp4 broll.mp4 --genre clips --from "the first words" --to "the last" --project $PROJ
```
`--words JSON` (an existing transcript), `--lang`, `--src-in S --src-out S` (a range instead of phrases),
`--subtitles karaoke|subtitle|none`; motivation: `--voice FILE` (a voice-over over a music edit). Jump cuts at
pauses and fillers, crops kept off overlays, captions with the style's preset. Exact in/out by quoted words with a
reaction kept, or a talk part followed by a music edit → `references/scenario-composite.md`.

## 6. Versions

"Another version", "not like the last one":
```bash
$E/edit.py variant $PROJ/edl_v2.json --variant 2                   # same inputs, avoids v2's choices
$E/edit.py variant $PROJ/edl_v2.json --variant 1 --style "dreamy retro"   # the same inputs in another style
```
A variant re-plans from the same track, footage, genre, options and length: other shots per slot, cut-grid
tie-breaks, another transition order and places, other accent picks, the ramp rotation started further on, a grade
nuance, the next look of the style's rotation (version v takes look v mod n: 2–3 looks per style; the talk styles
`podcast_punch`, `calm_explain` and `native_ugc` stay natural on v0 and take a subtle look later) and, on odd
variants, the sibling caption preset. `--avoid EDL …` steers away from more earlier versions. What each version
picked is in `meta.choices` (style, variant, transitions, looks, look, look_pick, grade, nuance, caption_style,
sfx_style, sfx_level, shots, ramps, accent_swaps). Composites: `edit.py variant` re-plans the stored spec; remakes
have no variants (`edit.py remake --pick`). Point edits on any version still go through `edit.py cmd`. A variant is
a full re-plan with a preview: `--background` when it may take more than a couple of minutes.

## 7. Gaps

Slots the footage cannot serve are listed in `meta.gaps` (`kind`: `missing`, `stretched`, `reused`, `weak`) with a
reason and an edit-gen brief, and show as NO SHOT tiles on the plan sheet. Options, cheapest first: code (a zoom
from a wider shot, a crop, photo parallax), another moment of the footage (`edit.py cmd` with `"op": "swap"`),
generation (the edit-gen skill: brief, price, explicit "yes"), then `edit.py fill EDL MAP` (§8). On autopilot only
the free options; list the paid ones with prices.

## 8. Storyboard: a whole video to generate, cut to the user's track

```bash
$E/edit.py storyboard --track T.wav --style "gritty street" --brief "a boxer before a fight" \
    --character "a tall boxer in a red hoodie" --n-shots 8 --project $PROJ --background   # also --genre, --dur, --variant
```
The track is planned like a genre edit over stand-in shots; every slot becomes a gap with an edit-gen brief in
`meta.gaps[].brief`: `shot_size`, `subject`, `action`, `camera`, `duration` (`slot_s`, `source_s`, `handles_s`,
`generate_s`), `speed`, `continuity` (the character kept identical), `look`, `aspect`, `fps` and a ready `prompt`.
The preview is an animatic of slates; QA lists the slots still to fill. Then:
1. the **edit-gen** skill turns each brief into a shot (one Element for the character), prices every shot and the
   total, and waits for an explicit "yes";
2. generate, download into `$PROJ/gen/`;
3. `$PROJ/gen/map.json` = `{"C01": "gen/c01.mp4", "#2": "gen/c02.mp4", …}` (segment id, `#N` or the slot source
   `slot03`; `{"path", "t"}` picks the in-point);
4. `$E/edit.py fill $PROJ/edl_v1.json $PROJ/gen/map.json` — per slot the best window, a slow-down when a clip is too
   short (reported as `stretched`), a subject crop with the planned zooms, the planned grade fitted to the clip; the
   next version, sheet, preview, QA.
Music comes from the user's file; Higgsfield audio generation is a separate paid option with its own "yes".

## 9. Checkpoints and final

The plan sheet + 5–10 lines from `explain` (track window, parts by seconds, the style and why, gaps and how to fill
them) → the draft preview + QA (`references/qa.md`) → point edits (`references/point-edits.md`) → final:
`$E/edit.py render $PROJ/edl_vN.json --final --background`, then `$E/edit.py status $PROJ`
(`references/modes.md`). File for the user: `/mnt/user-data/outputs/<project>_v<N>.mp4`.

## 10. Rules easy to forget

- Cuts on beats ±1 frame; the share on the grid ≥ the genre's `on_beat_share`.
- Motion peaks (a hit, a landing) on beats; ramps and flashes tied to them.
- Effects and SFX on musical events, within the card's limits; one move repeated back to back looks cheap.
- Text inside the 9:16 safe zone (top 12 %, bottom 20 %, right 12 %), never over faces.
- Flashes ≤ 3 per second (photosensitivity); loudness −14 LUFS, true peak ≤ −1 dBTP.
