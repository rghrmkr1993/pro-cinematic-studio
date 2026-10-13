# Point edits: command grammar

A command = **WHERE** + **WHAT** (+ **HOW**). Word order is free; one message can hold several commands ("crash at
0:07, whip between #4 and #5, and any glitch on the drop"). Apply a message's commands as one JSON list: they run in
order and make **one** new version; show that version.

Contents: 1. WHERE · 2. WHAT · 3. Voice and synonyms · 4. A move from a family · 5. The shot is missing ·
6. How to apply · 7. Procedure · 8. How to reason

## 1. WHERE — addresses

| form | examples | how to resolve |
|---|---|---|
| moment | "at 0:07", "at 7.5 s" | **output** time (the preview's timecode); `"at": "0:07"`. A beat-tied move lands on the beat nearest to it; say where |
| clip | "#5", "the fifth shot" | the `#N` from the preview the user watched → `"clip": 5` / `"#5"`, or the segment id `"C05"` of that version (ids survive inserts, numbers shift) |
| within a clip | "on #5 at the hit", "at the end of #5" | a strong beat inside the segment, else the shot's motion peak; "at the end" = the last quarter |
| junction | "between #4 and #5", "on the cut before #5" | `"between": ["#4", "#5"]` (or ids), or `"at"` = the cut nearest that time |
| range | "from 0:05 to 0:09", "the last 2 bars" | frames f0..f1; the move goes on every segment in it, trimmed |
| part | "in the hook", "in the build", "on the drop", "in the outro" | `"part": "drop"` — the genre parts in `meta.parts` |
| part of a composite | "in the talk part", "in the hype part", "on the drop of the edit" | `"part": "hype"` (a part id), `"hype.drop"`, or a section (`hook` / `build` / `drop` / `outro`) of the edit part at `"at"` / `"clip"`; the edit part's genre rules apply |
| words | "where he says 'three million'", "after the laugh" | `edit.py voice phrase WORDS.json "three million"` → source time → output frame via the talk piece (`at` + t − `in`) |
| musical event | "on every beat of the drop", "on the downbeats", "before the drop" | `track.json` / `audio.grid`: beats, downbeats, the drop; "before the drop" = the last beat before it |
| by content | "where he jumps", "on all the close-ups" | the plan's slot tags / source features → a list of segments; more than three or doubtful → show the list and ask |
| everywhere | "on every transition" | all fitting spots within the genre's frequency limits; beyond them, warn once and do it |

## 2. WHAT — actions

| action | examples | how |
|---|---|---|
| add a move | "crash", "whip", "flash", "shake on the beat", "slow-mo", "freeze" | `{"op": "add", "move": ID, …}`, a transition: `{"op": "transition", …}` |
| any move of a family | "any glitch on the drop", "some transition" | `{"op": "family", …}` (§4) |
| remove | "remove the flash at 0:12", "no shake in the drop" | `{"op": "remove", "move": ID or family, scope}` (its sound goes too) |
| replace | "a dissolve instead of the whip on #5" | `{"op": "replace", "move": NEW, "replace": OLD, "clip": 5}` |
| another shot | "a different shot on #6", "the one where he jumps" | `{"op": "swap", "clip": 6, "with": "next" \| {"src": NAME, "t": 81.2} \| {"shot": "clip#3"}}`; remakes: `edit.py remake --pick` |
| parameter | "stronger", "softer", "faster" | `"params"` within the card's range: ±25 % amplitude, ∓30 % duration; exact numbers as said |
| insert / delete | "insert 0.5 s of the wide shot at 0:07", "remove #5", "cut 0:07–0:07.5" | ripple ops `insert`, `delete_clip`, `delete_range` (everything after moves, the music stays) |
| timing | "make #3 half a beat shorter", "move the cut before #5 a beat earlier" | low-level `set` on `f0` / `f1` / `t` of the neighbours, or a ripple op; keep cuts on the beat grid |
| sound | "louder impact on the switch", "no whooshes", "use my sounds" | `set` on `audio.sfx.<i>.level` (`light` / `normal` / `strong`), `delete` an event, `audio.sfx_dir` or an event `file` (`references/edl-cookbook.md`, Sound) |
| text, captions | "bigger captions", "move the title up", "captions with a box" | the layer's `style` / `pos`, the caption preset (`edl-cookbook.md`, Text) |
| colour, look | "warmer", "black and white on the drop", "film look" | the segments' `grade` / a look (`edl-cookbook.md`, Looks) |
| the whole version | "another version", "not like this one", "same in the dreamy style" | not a point edit: `edit.py variant EDL --variant N [--style …]` |
| a composite's structure | "start the talk a sentence earlier", "6 shots instead of 5" | not a point edit: the spec → rebuild (`references/scenario-composite.md`) |
| lip sync | "the voice is late", "the lips don't match" | not a point edit: the talk part's `av_offset` (QA's measured lag) → rebuild; the analysis is cached, so it takes seconds to a minute |
| back to a version | "put it back the way it was in v3" | a copy of v3 as the **new** version N+1; history is not rewritten |

## 3. Voice and synonyms

Users dictate: normalise numbers as words ("between the fourth and the fifth"), mishearings ("crash / crush", "whip /
wip / swish", "freeze / frieze") and word forms.

| said | move |
|---|---|
| crash, crash zoom, sudden zoom-in | `zoom.crash` (a crash cut to another world: `cut.crash`) |
| punch, zoom on the beat | `zoom.punch` |
| whip, swish | at a cut `trans.whip`; inside a shot `pan.whip` |
| flash, white flash | at a cut `trans.flash`; inside a shot `light.flash`; a stream of one-frame shots `cut.flash` |
| shake | `shake.beat` |
| slow-mo / ramp / velocity / freeze | `time.slow_motion` / `time.speed_ramp` / `time.velocity` / `time.freeze` |
| dissolve / fade to black | `trans.dissolve` / `trans.fade` |
| glitch, RGB, bars, film, glow | `fx.glitch`, `fx.rgb_split`, `fx.letterbox`, `fx.film_overlay` / `look.film`, `fx.glow` |
| boom, hit / swoosh / build-up / bass drop | `sfx.impact` / `sfx.whoosh` / `sfx.riser` / `sfx.sub_drop` |
| "harder", "can't hear it" (a sound) | that event's `level` one step up (`strong`); check QA `sfx` |
Not sure: `python3 -I $ED/scripts/find_move.py <word>` and choose by the move's position in the genre. A named effect
"like the real one" → measure an example (`references/scenario-remake.md` §4).

## 4. "Any move from the glitch family"

1. `find_move.py --family glitch --genre <slug> --part drop` (moves the genre forbids are hidden and named).
2. Prefer a move of this part of the genre, then an allowed one; no repeat of the same move within ±2 bars; mind the
   frequency limit.
3. Say what was chosen and why, plus 1–2 alternatives.
4. The genre forbids the family → do not substitute silently: "glitch is forbidden in epic; put it in anyway, or a
   flash with shake?" (`"force": true` only if the user insists).

## 5. The move needs a shot that does not exist

Status `footage` or `generation` (an orbit with no drone shot, 120 fps slow motion) → offer, free first: **code** (the
card's `fallback`: a digital orbit by cropping, slow motion by interpolation), **the footage** (another moment,
candidates as a sheet), **generation** (edit-gen: brief, price, explicit "yes").

## 6. How to apply

```bash
E="python3 -I $ED/engine"
$E/edit.py cmd $PROJ/edl_v4.json '<JSON command or list>' [--render]     # -> edl_v5.json (+ draft preview and QA)
```

| said | command |
|---|---|
| "crash zoom at 0:07" | `{"op": "add", "move": "zoom.crash", "at": "0:07"}` |
| "punch on #5, a bit stronger" | `{"op": "add", "move": "zoom.punch", "clip": 5, "params": {"scale": 1.25}}` |
| "whip between #4 and #5" | `{"op": "transition", "between": ["#4", "#5"], "move": "trans.whip"}` |
| "any glitch on the drop" | `{"op": "family", "family": "glitch", "part": "drop"}` (composite: `"part": "hype.drop"`) |
| "a flash instead of the whip on #5" | `{"op": "replace", "move": "trans.flash", "replace": "trans.whip", "clip": 5}` |
| "no shake in the drop" | `{"op": "remove", "move": "shake.beat", "part": "drop"}` (scope: `at` / `clip` / `part` / everything) |
| "a different shot on #6" | `{"op": "swap", "clip": 6, "with": "next"}` |
| "insert 0.5 s of clip a at 0:07" | `{"op": "insert", "at": "0:07", "dur": 0.5, "segment": {"src": "a", "t": 12.0}}` |
| "remove #5" / "cut 0:07–0:07.5" | `{"op": "delete_clip", "clip": "#5"}` / `{"op": "delete_range", "from": "0:07", "to": "0:07.5"}` |
| "zoom #3 in a bit more" | `{"op": "set", "path": "segments.C03.crop.z", "value": 1.3}` (also `append`, `delete`) |

- Apply to the **latest** version; translate `#N` from the version the user watched into an id first when numbers
  may have shifted.
- The engine refuses a move the genre forbids, and any edit that would break the timeline, with the reason; relay
  it. `"force": true` only when the user insists.
- A measured named effect (`edit.py measure-ref`) prints `apply` lines: fill `"at"`, `"between"` or the clip and run
  them as is.

## 7. Procedure

1. Resolve addresses (seconds → frames, `#N` → ids by the version the user saw, words → times).
2. Move details if needed: `find_move.py --show ID --fields params,when,avoid,sfx`.
3. Conflicts: genre bans, frequency limits, neighbouring moves, text and faces under the effect, enough source for a
   new length or speed.
4. `edit.py cmd …` (or a hand edit + `edit.py validate`).
5. Check the window: `edit.py render EDL --frames a:b` and a still sheet around it; for sharpness, colour or a
   caption at 1:1, one full-size frame: `edit.py frame EDL 0:07.5 --out $PROJ/check.png`.
6. A full draft preview when edits have piled up or the user wants to see it; then QA.
7. Report per command: what, where (`#N`, time), what did not work and why; "the former #7 is now #8" after inserts.
Ask only when the ambiguity changes the result noticeably or costs money; otherwise pick a sensible default and say it.

## 8. How to reason (30 fps)

**"crash zoom at 0:07".** t = 7.0 → f 210 → segment #6 (f 198–236). The card wants 0.3–0.7 s of static hold before a
~0.4 s snap landing on a beat. The nearest beat (7.02 s) is only 0.4 s into the clip — not enough hold; land on the
next beat at 7.52 s: "the crash lands on the beat at 0:07.5". Check `meta.history` and a still sheet.

**"whip between #4 and #5".** The transition sits at the start of #5; the blur direction follows the motion at the
end of #4 and the start of #5 (if they differ, take #5's and say so); a whoosh peaks on the cut.

**"any glitch on the drop"** (phonk): an allowed move of the family on the drop's first beat; in epic the family is
forbidden → a question with an alternative (§4).

**"make #3 half a beat shorter"** (120 BPM): half a beat = 0.25 s ≈ 8 frames — `#3.f1 −= 8`, `#4.f0 −= 8`, #4's
in-point 8 frames earlier (`t −= 8/30 × speed`) if the source has them; the cut stays on the half-beat grid.

**"put it back the way it was in v3"** (current v7): `edl_v8.json` = a copy of v3, `meta.notes`: "= v3 on request".
