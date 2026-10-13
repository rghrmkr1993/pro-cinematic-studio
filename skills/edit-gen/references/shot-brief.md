# Shot briefs: from a timeline slot to a prompt

The generator knows nothing about editing. A brief turns a slot into a shot that sits in it seamlessly: duration,
shot size, motion, light and role. The planner writes one for every gap; you check it, complete it with what the
user said, and hand it to cinema-skills for the model's prompt.

## Where the briefs come from

- **Storyboard** (a whole video to generate): `edit.py storyboard --track T --brief "what the video is about"
  [--character "who appears in every shot"] [--style "…" (English words) | --genre …] [--n-shots N] [--dur S]
  --project P --background` (poll `edit.py status P`) plans the track like a genre edit over stand-in shots; every
  slot is a gap of kind `storyboard` and the preview is an animatic of slates (QA lists the slots to fill).
- **Gaps of a normal plan**: slots the footage could not serve (`missing`, `weak`, `reused`, `stretched`).
Both live in `meta.gaps` of `edl_vN.json`:
```json
{"slot": 0, "id": "C01", "part": "hook", "role": "hook", "kind": "storyboard", "t": [0.0, 2.0], "f": [0, 59],
 "dur": 2.0, "need_s": 2.0,
 "brief": {"shot_size": "full length, walking toward the camera", "subject": "…", "action": "…",
           "camera": "slow push-in", "duration": {"slot_s": 2.0, "source_s": 2.0, "handles_s": 0.5, "generate_s": 5},
           "speed": "normal", "continuity": ["the same character in every shot: …", "screen direction left to right"],
           "look": "…", "aspect": "9:16", "fps": 24, "prompt": "…"}}
```
`source_s` is how much picture the slot consumes (speed ramps and slow motion change it); `generate_s` is what to
ask for: `source_s` + 2 × `handles_s` (0.5 s), rounded up to 5 or 10 s (beyond 10: the next whole second). `speed` says whether the slot plays slow or ramps — ask for
real motion through the braking beat, not a static pose.

## Checking and completing a brief

| field | check |
|---|---|
| subject | the user's words (`--brief`); one Element for a recurring character or product (`references/elements.md`) |
| action | one clear action peak; where it should fall in the shot ("at ~1.2 s"), so the edit can put it on the beat |
| shot size, camera | variety across neighbours (wide → close → detail), the direction of motion matching for match cuts |
| look | the style's look in words (light, colour, texture) — no equipment brands; the same for every shot |
| aspect, fps, duration | the canvas aspect (9:16), `generate_s`; no text, logos or watermarks in frame |
| continuity | wardrobe, props, time of day, screen direction across all slots |

Read the plan sheet (`plan_vN.jpg`) for the slot's neighbours and the genre card's "Shot selection" for the role
(`references/genres.md` in edit-director). A move card that needs the shot has a `gen_hint` field
(`find_move.py --show ID --fields gen_hint,frames`) — an English starter, rewrite it for the slot.

## Prompts via cinema-skills

Use `cinema-skills:cinema-pipeline` (it picks the specialist and the writer for the chosen model); pass the brief, the
model from `references/generate.md` and the Element placeholders (`<<<element_id>>>`, kept as is). Check each prompt
before pricing: duration, aspect and motion match the brief; no film titles, brands, creators or real people.

## A whole video

- Order the shots by importance (the drop shot and the hook first): if the user approves only some, the best slots
  are filled; the rest stay slates or get stand-ins.
- One price question for the set: per shot and the total (`references/generate.md`).
- After generation: `gen/map.json` maps slots to files, `edit.py fill` plugs them in (`references/conform.md`).
