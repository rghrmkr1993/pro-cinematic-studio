# From the user's words to a plan

Most "it did not do what I asked" failures happen before the engine runs: a request with parts gets squashed into
one genre edit, "after his reaction" becomes "at the end of the sentence", "only the people" is lost. This page is
the in-skill version of the user guide: the request types users send, how each word becomes a spec field or a flag,
and the defaults.

Contents: 1. The five request types · 2. The plan lines · 3. Words → fields · 4. Defaults · 5. When to ask ·
6. Versions, point edits, named effects

## 1. The five request types

Users are told to send one message per request in one of these shapes (the user guide has the same templates).

| type | template the user fills | path |
|---|---|---|
| **A. Edit to music** | "Edit these clips to this track. Style: [words or genre]. [Length], [9:16]. Must: … Never: …" | `edit.py plan --style "…"` (`references/scenario-genre.md`) |
| **B. Talk → edit** | "From [file]: start at [quote / time], end [at quote / after the reaction to quote]; cut [quote]. Then [N] shots [in this order], [one bar each], [speed ramps], the drop when the edit starts. Captions [style] on the talk." | `edit.py sequence` (`references/scenario-composite.md`) |
| **C. Clip from a long talk** | "Find [3] moments of [30–45 s] in [file] that work alone. Vertical, [captions style]." / "Cut [quote] to [quote]." | `edit.py voice clips` → one talk part (`edit.py sequence`) or `edit.py plan --genre clips --from … --to …` |
| **D. Remake a reference** | "Remake [ref file] with my footage. [Same music / this track]. Replace its text with [words]." | `edit.py remake` (`references/scenario-remake.md`) |
| **E. Generate the whole video to my track** | "Make a [N]-shot video about [subject] to [track]. Character: [description]. Style: [words]." | `edit.py storyboard` → edit-gen (paid, explicit "yes") → `edit.py fill` |

Named effects ("a real VHS rewind like the original") and "another version" are add-ons to any type (§6).

## 2. The plan lines

Restate the request in at most 5 lines before heavy work: **parts in order · cut points · length · format · style**
(+ anything paid as a separate question). Plain words, the user's language, timecodes and quotes, no JSON.

```text
1) Talk from interview.mp4: "the real question is" → his reaction after "three million a year"; aside removed.
2) Hype: your 5 shots in order, one bar each, speed ramps; drop on its first frame; flash + impact on the switch.
~25 s · 9:16 · style "gritty street" → street_grit (matched "gritty", "street") · captions on the talk only.
```
For a style in plain words, translate the words into English first (the matcher is English-only), then name the
preset and why in one line: `python3 -I $ED/engine/ed_plan.py styles "their words"` prints `{"name", "score",
"genre", "matched", "why"}`. `matched: false` = nothing matched and the genre's default style is used — say so and
offer 2–3 presets. A talk part with only its end named gets an automatic start: say which sentence it is (quote +
timecode, from `ed_sequence.py resolve`) so the user can move it. Then run; corrections come back as spec or flag
changes.

## 3. Words → fields

**Talk parts** (spec of `edit.py sequence`; times are source seconds of that file):

| the user says | field |
|---|---|
| "from where she says 'X'" | `"from": {"phrase": "X"}` (or `"from": 24.05` / `"0:24.05"`) |
| only the end named ("the bit that ends with his reaction") | no `from`: the first clean sentence (sources up to ~90 s) or the best setup sentence ≤ 25 s before the end (longer sources); `"from": {"auto": true, "max_s": 25}` asks for the setup start on any source |
| "up to 'X'" | `"to": {"phrase": "X"}` — ends after X at the next quiet point |
| "until his reaction to 'X'" (sigh, laugh, "wow") | `"to": {"phrase": "X", "end": "after_reaction"}` |
| "to the end of that sentence" | `"to": {"phrase": "X", "end": "sentence"}` |
| "the second time he says X" | `{"phrase": "X", "occurrence": 2}` |
| "cut the part about X", "skip 'X'" | `"remove": [{"phrase": "X"}]` (or `"X"`, or `[t0, t1]`) |
| "tighter, no long pauses" / "natural pace" | `"tighten_pauses": 0.3` / `null` (default) |
| "only the people", "it's a screen recording", "no logo / UI" | `"crop": "speaker"` (content box and overlays are detected and kept out; `max_zoom` 1.45) |
| "push in on the punchline" / "zoom cuts on the key words" | `"push": true` / `"punch_ins": true` |
| caption look | `"subtitles": "podcast_bold"` · `"podcast_caps"` · `"clean"` · `"boxed"` · `"karaoke_highlight"` · `"karaoke_box"` · `null` (none) |
| "music quiet under the talk" | `"music_db": -18` (−18…−24; the bed swells into a following edit part unless `"swell": false`) |
| "the lips are out of sync" | nothing by default: the lag is measured and corrected when the estimate is confident (≥ 2 frames); `"av_offset": 0.12` forces a value, `0` keeps the recording as is |
| "shorter caption lines" | `"subtitles": {"style": "podcast_bold", "max_chars": 22}` (`max_lines`, `max_words` too) |

**Edit parts and plain music edits** (spec keys / `edit.py plan` flags):

| the user says | spec (edit part) | `edit.py plan` |
|---|---|---|
| "5 shots" · "one bar each" | `"shots": 5` · `"bars": 5` | `--n-shots 5` · `--bars 5` |
| "in this order" | `"order": "given"` | `--order given` |
| "with speed ramps", "slow-mo", "a crash zoom" | `"moves": ["time.speed_ramp"]` | `--require time.speed_ramp` |
| "no glitch", "no shake" | `"forbid": ["fx.glitch"]` (ids or families) | `--forbid fx.glitch` |
| "hard sound effects" / "subtle" / "no sound effects" | `"sfx": "heavy"` / `"light"` / `"none"` (default `"genre"`) | `--sfx-level heavy` … |
| "use my sounds" (a folder) | top-level `"sfx_dir": "sounds"` | `--sfx-dir DIR` |
| a style in words | `"style": "dreamy retro"` (top level or per part) | `--style "dreamy retro"` |
| a genre | `"genre": "phonk"` | `--genre phonk` |
| "faster cutting" | — | `--cut-rate 1.5` |
| "about 20 seconds" | `"bars"` (bars = s × BPM / 240) | `--dur 20` |

**Music** (spec `music` / plan flags):

| the user says | spec | `edit.py plan` |
|---|---|---|
| "the drop when the edit starts" | `"drop_at": {"part": "hype", "at": "start"}` (or `"drop_at": "hype"`) | — |
| "the drop 2 s into the edit" / "the drop at 0:16 of the video" | `"drop_at": {"part": "hype", "at": 2}` (seconds into the part) | `--drop-at 16` (output second) |
| "the drop is at 1:05 in the track" | `"drop": 65` | `--drop-t 65` |
| "start the track at 0:42" | `"in": 42` | `--music-in 42` |
| "a flash and a boom at the switch" | `"transitions": [{"from": "talk", "to": "hype", "kind": "flash", "sfx": "impact"}]` | — |
| (the track has no clear drop) | the engine lands the switch on the biggest energy jump and says so in a note: tell the user, offer another section (`"in"`, `"drop"`) or another track | same note |

SFX amounts (`sfx` / `--sfx-level`): `light` = the switch only (the hits on the drop); `genre` (default) = the card's
program + a low thump on every speed-ramp brake + a whoosh (or a short riser) into the switch; `heavy` = also a
whoosh on every ramp speed-up, a riser into every section, a hit on every downbeat cut of the drop and a sub drop
under the drop hit. How loud each event is, is a separate setting (`level`: light / normal / strong —
`references/edl-cookbook.md`, Sound).

Map the request into **the user's structure**: "a podcast fragment, then a hype edit" is two parts in that order —
not a genre edit of the podcast, not a hype edit with the podcast as footage.

## 4. Defaults (state them, do not ask)

| field | default |
|---|---|
| format | 9:16, 1080×1920, 30 fps |
| length | a composite: the sum of its parts; a music edit: the genre card's typical length (`--dur` to change) |
| style | none given: the genre's rules; words given: the matched preset (named in the plan lines) |
| talk part | natural pauses, `crop: "speaker"`, captions from the style, else `podcast_bold`; the bed at −18 dB; lip sync measured and corrected |
| talk start (only the end named) | the first clean sentence; sources over ~90 s: the best setup sentence ≤ 25 s before the end |
| join talk → edit | flash (with a style: a punchy kind from its palette, rotated per version) + a riser into the cut + impact and sub drop on it |
| SFX | `genre` amount; every sound at the `normal` level |
| shots | every given shot once; `order: "given"` for numbered or generated shots, else `auto` |
| preview | the fast draft (540×960); the final only on request or after the user's OK |
| mode | checkpoints; autopilot when asked (`references/modes.md`) |

## 5. When to ask (one round, at most)

Only what blocks the plan: no track for a music edit; a long source with no moment named (offer 3 candidates from
`edit.py voice clips` with timecodes and first lines); which file plays which role when it is unclear; anything
paid (a separate question with the price). Never ask about fps, caption look, SFX amount, transition kind or genre
when the words imply one. While waiting, run what does not depend on the answer (ffprobe, transcription, track
analysis).

## 6. Versions, point edits, named effects

- "Another version" / "not like the last one" → `edit.py variant EDL --variant N` (composites re-plan their spec;
  the cut points and the drop stay; shots, looks — each style rotates 2–3 — moves, ramps and transitions change).
  "Same, but in the dreamy style" → `--style "dreamy"`.
- Everything aimed at one spot ("#5", "at 0:07", "on the drop") → `edit.py cmd` (`references/point-edits.md`).
- "A [named effect] like the real one" without a file → web search for an example clip, the link and the user's OK,
  a direct GIF/MP4 into `$PROJ/refs/`, `edit.py measure-ref CLIP --sheet …`, then `cmd` or `--require`
  (`references/scenario-remake.md` §Named effects). No YouTube / TikTok downloads; a blocked fetch is reported, not
  worked around.
