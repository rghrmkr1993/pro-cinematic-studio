# Move library

`moves/<family>.yaml` holds the cards of one family (several YAML documents separated by `---`), ~270 moves in all; read them with `find_move.py --show ID`. Cards are long (4–25 KB, median ~10 KB), and the index
`moves/index.md` is ~120 KB. **Never load the library or the index whole**: search with the script and read only the
fields you need from a card.

## Structure

- `id` = `<family>.<name>`: `zoom.crash`, `trans.whip`, `time.speed_ramp`, `fx.rgb_split`, `type.karaoke`, `sfx.riser`.
- Groups (our taxonomy): `camera` · `angle` · `editing` · `transition` · `time` · `effect` · `optics` · `aesthetics` · `graphics` · `sound`.
- Level: A — basic vocabulary, B — an effect with variations, C — a non-trivial technique.
- Status — what it takes to make the move:

| status | meaning | what to do |
|---|---|---|
| `code` | done in code on any video | use it |
| `hybrid` | needs a mask of an object or a person | a local mask (PP-HumanSeg; a precise one with U²-Net if the model is available) or Higgsfield `remove_background` — paid, via edit-gen |
| `footage` | needs a special shot (drone, 120 fps slow motion, an orbit…) | find it in the source footage; if there is none — the card's `fallback` (imitation in code), another move or generation |
| `generation` | no such shot exists and it cannot be made in code | only generation (edit-gen, price, "yes") or dropping the move |

## Search

```bash
F="python3 -I $ED/scripts/find_move.py"
$F crash zoom                         # by id, aliases, description
$F flash --genre phonk                # + the move's position in the genre: part, signature, allowed, FORBIDDEN
$F --family glitch --genre epic --part drop   # a family for a part of the genre; forbidden moves are hidden and named separately
$F --group transition --status code --genre travel --part build
$F --genre epic                       # genre summary: parts, signature, allowed, forbidden, SFX, looks
$F --show zoom.crash trans.whip --fields params,engine,when,avoid,sfx   # only the card fields you need
```
Result line: `id  status·level  genre-position  what it is | aliases`. A position "per move card" is the move card's
own view, shown when the genre card does not mention the move. A "hidden as forbidden" line is a reason to warn the
user, not to silently pick something else.

Without the script: one index line — `grep -n 'crash' $ED/moves/index.md`; the machine-readable index is
`moves/index.json` (`id, family, group, status, level, what, aliases, signature, allowed, banned, confidence, examples`).

## Which fields to read

| task | card fields |
|---|---|
| place a move | `params`, `engine`, `when`, `avoid`, `sfx` |
| understand what it looks like (to explain it to the user) | `what`, `frames`, `variants` |
| the needed shot is missing | `status`, `fallback` |
| spot the move in someone else's video (remake, DNA) | `detect` |
| a brief for generating a shot | `gen_hint` (an English starter: rewrite it for the slot, see edit-gen) |
| understand the user's command | `commands`, `aliases` |
| neighboring and easily confused moves | `related` |
| how far to trust the card | `evidence.confidence` (`low` — verify with a demo render) |

`engine` describes the move as a dictionary of primitives (`moves/_engine_api.md`: `transform`, `blur`, `speed`, `transition`,
`sfx`…). In the timeline they become EDL fields — the mapping table and recipes are in `references/edl-cookbook.md`.

## Rules of use

- **Genre first.** A move from the genre's part beats an allowed one; a forbidden one only if the user insists after a
  warning (and with an explanation of why the genre forbids it — in the "Moves by part" section).
- **Limits.** Take the frequency from the card's `when` and from the genre's limits (per 10 s, per bar, per video).
  Repeating the same move back to back and an effect on every beat are the main signs of a "cheap" edit.
- **Music.** The peak of a move lands on a beat or an accent (`beats`, `downbeats`, `drops` from `track.json`); cards
  with detailed `params` (for example `zoom.punch`) describe the peak timing in frames — follow it.
- **The move's sound.** The `sfx` field says which sound and at which point (`attack` — the start, `peak` — the peak);
  the engine synthesizes the SFX, the volume follows the genre card.
- **Text and faces.** No shake, glitch or heavy motion blur under text or on a close-up face while the person is
  speaking, unless the genre card says otherwise.

## Move demo

The user asks "what does a dolly zoom / pixel sort look like?" — the library has no GIFs. For `code` moves, render a
short demo on their own footage: 2–4 s around a suitable moment, preview size, no labels.
Minimal EDL: `canvas`, `n_frames`, `sources` (one source), one segment with the needed `fx`/`speed`/`crop`
and, if the move is a transition, two segments with `transition_in`. For `footage`/`generation` moves, explain in words
(`frames`) and show whether the source footage has a suitable shot.

## New and corrected moves

If the user has invented their own technique or wants to fix a card, the format and the field order are in
`moves/_conventions.md`. Write a new card as a separate `<id>.yaml` file in the user's data and check its fields
against neighboring cards of the same family. The skill folder may be read-only — keep your own cards in `/home/claude/projects/_user/moves/`.
IP rules for new cards: your own words, no titles of films or music videos, no brands, authors or people; examples are
generic ("a push-in on a face as the line is spoken").
