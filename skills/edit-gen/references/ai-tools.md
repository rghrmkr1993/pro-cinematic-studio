# AI processing of shots: reframe, upscale, outpaint, background

Everything paid follows the consent protocol in SKILL.md. Always check the engine's free path first. Upload only
the needed **fragment** (a piece cut out by the engine), not the whole source: the price grows with the length.

| tool | what it does | price in advance | free alternative |
|---|---|---|---|
| `reframe` | generates the video's edges out to a new aspect ratio (16:9 → 9:16, etc.) | `get_cost` | subject-tracked crop, the layouts `layout.windowbox` / `layout.split_screen` |
| `upscale_video` | raises the resolution and cleans up the video | **no** | a smaller crop, dropping the deep zoom-in |
| `upscale_image` | raises a photo's resolution | `get_cost` | — |
| `outpaint_image` | extends a photo to the aspect ratio | `get_cost` | crop, a blurred background from the same photo |
| `remove_background` | removes the background (photo and video) | **no** | local person mask (`hybrid` moves) |
| `virality_predictor` | estimates engagement and retention risks of a finished video | **no** | — |

## reframe — vertical without losing what matters

When: a 9:16 crop cuts off something important — two people far apart, wide action, text or a chart at the edges —
and the layouts do not suit the genre.
1. Cut out the slot's fragment with a 0.5 s handle: `ffmpeg -ss T -i SRC -t DUR -c:v libx264 -crf 16 -c:a aac frag.mp4`.
2. Price: `reframe(params={"get_cost": true, "duration_seconds": DUR, "resolution": "1080p"})`.
3. After the "yes": upload the fragment (`media_upload` → PUT → `media_confirm(type="video")`) →
   `reframe(params={"medias": [{"role": "video", "value": "<media_id>"}], "aspect_ratio": "9:16"})`.
   Longer than 15 s — add `duration_seconds` and `resolution` and do not pass reference images; at most 60 s per call.
   To hint at what should fill the edges — up to two images with the role `image`.
4. Download, insert in place of the slot's source (`references/conform.md`), check the edges with a contact sheet —
   the generated areas can show in motion.

## upscale_video — when a crop or a zoom-in turns soft

When: the source is 1080p but you need a 9:16 crop with a zoom-in of ×1.5 or more (a crash zoom into the eyes
×4–5); old or low-quality sources. Milder enlargements get the engine's own adaptive, halo-free sharpening: check one
frame at full size first (`edit.py frame EDL T --out f.png`, edit-director) and offer the paid upscale only when it
still looks soft.
- Options: `{"provider": "topaz", "video_id": …, "resolution": "2160p" | "1080p"}` (depending on the format) or
  `{"provider": "bytedance", "video_id": …, "width": W, "height": H, "resolution": "1080p" | "2k" | "4k",
  "preset": "common" | "ugc" | "aigc" | "short_series" | "old_film", "fps": 24 | 30 | 60}` — `fps` above 30 doubles
  the price.
- No cost preview: "the price can't be calculated in advance; it is charged after the fact; upscaling a 3 s fragment
  for the crash zoom on #12".
- Only the slot's fragment; the result becomes the segment's new source; recalculate the crop for the new resolution
  (in fractions of the frame it does not change).

## upscale_image and outpaint_image — photo sources

`upscale_image(params={"image_id", "width", "height", "resolution": "2k" | "4k", "get_cost": true})`;
`outpaint_image(params={"image_id", "aspect_ratio": "9:16", "get_cost": true})` — a photo fitted to vertical with no
bars. Then a slow zoom-in or a photo parallax in the edit.

## remove_background — a mask for hybrid moves

When the local mask is not enough: hair, fast motion, not a person (a product, an animal). For text behind the
subject, double exposure, background replacement, a "cut-out" subject over graphics.
`remove_background(params={"media_id": …, "media_type": "video" | "image"})` — no cost preview. Only the slot's
fragment. The result becomes the slot source's subject matte: `sources.<name>.mask` = the file (or `{"path", "invert",
"channel": "luma" | "alpha", "offset", "fps"}`), decoded and warped like the picture — region fx (`region:
"background"`), `mask_flash`, text behind the subject and layers use it (edit-director `references/edl-cookbook.md`).

## virality_predictor — assessing a finished video

At the user's request, on the final render: `virality_predictor(action="create", params={"model":
"virality_predictor", "medias": [{"role": "video", "id": "<media_id>"}]})`. The price is not known in advance — a
"yes" is mandatory. The result is a forecast, not a guarantee; turn it into concrete changes to the edit (hook,
length, pace), not into promises.
