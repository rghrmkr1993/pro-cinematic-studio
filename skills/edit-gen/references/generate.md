# Model, price, run, result

## Model

- Choosing: `models_explore(action="recommend", type="video", query="<what is needed: text-to-video or image-to-video,
  9:16, 5 s, realistic flyover above mountains, no people>")`; the limits of the chosen one: `models_explore(action="get",
  model_id=…)`: durations, aspect ratios, media roles (`start_image`, `image`, …).
- A consistent hero via Elements — only the models listed in the `manage_reference_elements` description (check it
  at call time: the list changes); some also need a `start_image` for Elements.
- The model list and defaults change — do not rely on memory, ask `models_explore`. If the user named a model, use
  it.

## Direct shot or via a keyframe

| path | when | price |
|---|---|---|
| video straight from text | background and transition shots, a wide shot without the hero | one generation |
| keyframe (`generate_image`) → video from it (`start_image`) | the drop shot, the hero, the product — when the exact look matters | two generations, but the look is approved cheaply before the video |
Offer the path in the price question: "shot #9: first an image (N cr.), after your OK — the video (M cr.)".

## Price and the question

```
generate_video(params={"model": "…", "prompt": "…", "duration": 5, "aspect_ratio": "9:16",
                       "medias": [{"role": "start_image", "value": "<media_id>"}], "get_cost": true})
```
`get_cost` does not launch anything. The batch tools `generate_video_batch` / `generate_image_batch` give no cost
preview — price each request with a single call with `get_cost` and add them up. `balance` — what is left. Then the
question per the SKILL.md protocol: what, the price of each and the total, the balance, what happens without it.

Do not set `use_unlim`: if the user has free generations, the tool will not launch anything and will return
`unlim_choice` — ask the user how to pay and repeat the call with their answer.

## Running

- Folder: before the first generation in the conversation, `get_preferences`; create a project only if it has
  `auto_create_project: true` or the user asks (`create_project` once, then the same `folder_id`).
- One shot — `generate_video` / `generate_image` (the user sees the result in the widget). 2–12 independent
  shots — `generate_video_batch` / `generate_image_batch`, then `jobs_wait` (in groups of up to 12, wait ≤ 15 s per
  call, repeat until done) and one `show_generation_by_ids` for the whole set.
- `count` 2–4 — variants of one request; the price multiplies — only on request.
- Timeout or dropped connection: the outcome of the submission is unknown — do not resubmit until you have checked
  the job by `job_id`.

## Result

1. The file link comes from the `jobs_wait` response or from the generation tool; download it into the project:
   `curl -sSfL "<url>" -o $PROJ/gen/c09.mp4`. If it does not download, tell the user and ask for the file.
2. Record it in `$PROJ/gen/provenance.json`: `{"slot": "C09", "job_id", "model", "prompt", "elements": [...],
   "cost": N, "date", "file"}`.
3. Add it to `$PROJ/gen/map.json` (`{"C09": "gen/c09.mp4"}`) and run `edit.py fill` — `references/conform.md`.
4. If a shot does not work, say what is wrong (light, motion, shot size, artefacts), offer a prompt fix and a new
   price; do not regenerate without a new "yes".

## A whole video (storyboard)

- Price every slot with its own `get_cost` call and give one question: the per-shot prices, the total, the balance,
  and what happens without it (the slates stay, or fewer shots). Allow partial answers ("only the first 4").
- Generate the approved set as a batch (`generate_video_batch`, groups of up to 12), `jobs_wait`, one
  `show_generation_by_ids`, then download all, one `map.json`, one `edit.py fill`.
- A recurring character: the Element first (`references/elements.md`) — every prompt carries its placeholder.
- Music is the user's track; generated music is a separate paid question.

## Uploading your own files to Higgsfield

- Things made by the engine (a source frame for `start_image`, a video fragment): `media_upload(filename=…)` → run
  the returned PUT command (curl) → `media_confirm(media_id=…, type="image"|"video")`.
- The user's original as is: `media_upload_widget` — the user picks the file themselves.
- A link from the internet: `media_import_url` (up to 50 MB). In `medias[].value` — only a `media_id` or `job_id`,
  not a URL.
