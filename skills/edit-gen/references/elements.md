# Elements: the same hero, product or location in every shot

An Element is a character, object or environment card saved in the Higgsfield workspace. It is inserted into the
prompt and keeps the appearance the same across all generations — and similar to the hero in the user's source
footage.

## When

- There are two or more generated shots with the same hero or product — always for a storyboard made with
  `--character` (every brief's `continuity` names the same character).
- A generated shot must match a hero, product or location from the user's source footage.

## Where the reference comes from

- The user's footage or photo of themselves, their product or location: a still frame (below).
- A whole video from scratch with no footage: generate one keyframe of the character from the storyboard's
  `--character` description (`generate_image`, paid — price and "yes" first), let the user approve it, then make the
  Element from that image. Every shot of the storyboard then uses the same Element.

## Rights

We make an Element only from what is the user's own: the user themselves, their product, their character, their
location — or with the explicit consent of the person in the frame. We do not make: celebrities, other people's
characters, third-party brands and logos. If in doubt, ask.

## Creating one

1. One clear reference: the product or person in full or in close-up, good light, no extra objects.
   From the user's video — a still frame (pick the best one from a contact sheet):
   `ffmpeg -v error -ss 12.4 -i SRC -frames:v 1 -q:v 2 $PROJ/gen/ref_hero.jpg`
2. Upload: `media_upload(filename="ref_hero.jpg")` → run the returned PUT command (curl) →
   `media_confirm(media_id=…, type="image")`.
3. `manage_reference_elements(action="create", medias=[{"id": "<media_id>", "url": "<upload link>",
   "type": "media_input"}], category="auto", name="hero")` — specify the category (`character`, `prop`,
   `environment`) only if the user said so explicitly.
4. It is ready when `manage_reference_elements(action="get", element_id=…)` returns `status: completed`.
   `processing` / `ip_checking` — wait and check again; `failed`, `nsfw` and others — do not use it, and say why.
Creating an Element may charge credits — say so before the call and get a "yes".

## Using it

- In the generation's `params.prompt` — the placeholder `<<<element_id>>>` (UUID); several are allowed:
  "`<<<A>>>` lifts `<<<B>>>` toward the camera at dawn". The `@name` form does not work in a call.
- Do not put the Element into `medias` — the placeholder inserts the image by itself.
- Only the models listed in the `manage_reference_elements` description; if the model needs a `start_image` for an
  Element, provide a start frame or choose another model.
- Record the `element_id` in `project.json` (`elements`) — the Element lives in the workspace and will be useful in
  later sessions and videos.

## Checking the likeness

You compare frames; you do not "recognize" people: a "reference | generated shots" sheet — silhouette, clothing,
colors, product proportions, the text on the (user's own) packaging. Name the differences and offer: another
reference, a prompt fix or another model — with a new price.
