# Move library — conventions

One card = one move = one file `moves/<id>.yaml`. Values are written in English; the common editing terms for the move go in `aliases`.

## Card fields (the order is mandatory)

| field | contents |
|---|---|
| `id` | `<family>.<name>`, Latin letters, snake_case: `zoom.crash`, `cam.dolly_in`, `trans.whip` |
| `family` | our family (equals the id prefix) |
| `group` | one of the 10 groups (below) |
| `level` | A — basic vocabulary, B — an effect with variations (parameter calibration), C — a non-trivial technique (in-depth breakdown) |
| `aliases` | common English terms + colloquial names; no proprietary names from other catalogs |
| `what` | one line: what it is and what it is for (goes into the index) |
| `frames` | what the move looks like frame by frame, in our own words: setup → action → landing, with numbers |
| `variants` | (opt.) observed variants |
| `status` | `code` / `hybrid` / `footage` / `generation` |
| `fallback` | (opt.) what to do if the needed shot is missing: imitation in code, a search of the source footage, generation |
| `params` | working parameters for the engine: ranges + a typical value; time in seconds and in frames @25 fps |
| `when` | where the move works: part of the video, musical event, meaning; frequency limit |
| `avoid` | when the move does harm |
| `sfx` | sound support (type of sound and hit point) |
| `genres` | `{genre: signature / allowed / forbidden}` — only the genres where the move has a position |
| `detect` | how to recognize the move in someone else's video (for a remake): signs in the `ed_motion` output and visual signs |
| `engine` | which engine primitives, with which parameters (see `_engine_api.md`) |
| `gen_hint` | how to ask a generator for such a shot (an English prompt template) |
| `commands` | examples of user commands |
| `related` | (opt.) ids of related moves |
| `evidence` | `{examples, sources, measured, confidence}` — what the card is based on; `confidence`: `high` / `medium` / `low` |

## Groups (our taxonomy)

`camera` · `angle` · `editing` · `transition` · `time` · `effect` · `optics` · `aesthetics` · `graphics` · `sound`

## Statuses

- `code` — done in code on any video;
- `hybrid` — needs an object mask (mediapipe or `remove_background`);
- `footage` — needs a special shot; we look for it in the source footage;
- `generation` — the shot does not exist; we generate it with the user's consent.

## Genres (keys of the `genres` field)

`viral` · `epic` · `drama` · `calm` · `product` · `phonk` · `sport` · `travel` · `fashion` · `fanedit` · `teaser` · `clips` · `explainer` · `ugc` · `motivation`

The keys are the genre slugs, the same strings as the `genre:` field of the genre cards (`genres/*.md`).
Values: `signature` (the genre's signature move), `allowed`, `forbidden`. The link with the genre cards is two-way and is checked by a script.

## IP

- No media files, no titles of films/music videos, no brands/people, no text from source websites.
- Examples in general terms: "push-in on a face at the moment of a line", "pull-out reveals the aftermath".
- Proprietary names from other catalogs are used neither in ids nor in aliases.
