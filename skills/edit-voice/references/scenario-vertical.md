# Scenario 5: vertical 9:16 with infographics, subtitles and voiceover

From horizontal (or any) material, a vertical video with a smart crop, infographics, subtitles and voice. The
framework is a genre card from edit-director (most often `explainer`; for ads, `ugc` or `product`).

## 0. Inputs

- Source footage (16:9 or any), the text or voiceover script (or speech already in the source footage), data for
  the infographics (numbers, facts, labels), language.
- Voice: the user's recording (best, and free) → synthesis with a preset voice or a clone (paid) → no voice
  (on-screen text only).

## 1. Crop to 9:16

The usual way: a talk part of a sequence (`crop: "speaker"`, edit-director `references/scenario-composite.md`) or a
speech-genre plan (`edit.py plan --genre clips|ugc|explainer …`) — both run the chain below by themselves. By hand:

1. **Content box** — `ed_video.content_box(path, t0, t1)` → the live picture inside a screen recording or between
   letterbox bars (`sources.<name>.box`; source px, even-rounded; the full frame when nothing is found).
2. **Overlays** — `ed_video.static_overlays(path, box, t0, t1)` → `[{"box", "kind": "logo" | "text" | "ui" |
   "popup", "coverage", "spans"}]`: graphics that stay identical across camera angles (logo, lower third, watermark,
   notice, burned-in captions), and transient pop-ups (an app window or a toast that appears or goes while the rest
   of the frame stays; reported whatever its coverage); `spans` say when each is on screen, `coverage` how often
   (≥ 0.1 counts). The talk crops keep logos, lower thirds and UI out throughout and a pop-up while it is on screen;
   QA judges every overlay only inside its spans.
3. **Speaker crops** — `ed_reframe.speaker_crop(path, t0, t1, box=box, avoid=overlays, canvas=(1080, 1920), fps=30,
   words=words)` → one item per camera shot and speaker turn: `{"t0", "t1", "crop": {"cx", "cy", "z", "path"?},
   "shot", "speaker", "face", "subject"}`. `z` is the smallest zoom whose window holds the whole head (eyes near 38 %
   of the height), misses every `avoid` box and stays inside the box; within 2× upscale, then up to 3×, then the
   lowest-priority boxes are released (`ui`, then `text`, then `logo`; listed in `released`) — the face is never cut.
   `crop_pieces(items, a, b, fps)` cuts the items to a kept range (one segment each).
CLI: `python3 -I $ED/engine/ed_video.py box SRC`, `ed_video.py overlays SRC --box x0,y0,x1,y1`,
`python3 -I $ED/engine/ed_reframe.py speaker SRC T0 T1 [--box …] [--avoid auto|none] [--words WORDS.json]`.
Other material (no speech): `ed_reframe.crop_path(src, t_in, dur)` follows a face, a person, motion, else the centre.

If the crop still cuts something important (two people far apart, wide action, a chart):
1. free — the layouts `layout.windowbox` (the 16:9 frame as a window, headline above, captions below) or
   `layout.split_screen` (top / bottom for two speakers);
2. paid — Higgsfield AI reframe (generated edges out to 9:16) via edit-gen.
Check: QA `parts` / `faces` (talk framing, overlays visible, faces cut) and a window sheet
(`python3 -I $ED/engine/tools_win.py SRC sheet.jpg 't@cx,cy,z' …`); a soft-looking crop at 1:1: `edit.py frame EDL T
--out f.png` (enlargements over 1.1× get gentle, halo-free sharpening; a tight crop of a small player stays soft).

## 2. Voice

- Own recording: recognize it (`references/transcription.md`), clean out pauses and filler words, cut on words.
- Synthesis from the script: `generate_audio` (preset voice or clone) — paid, `get_cost` → "yes"
  (`references/higgsfield-voice.md`). Long text — phrase by phrase, so you can fix one phrase rather than all of it.
- After synthesis, recognize the generated voice: you need word timings for the subtitles and for the edit.

## 3. Editing to the voice

The voice is the time axis: the picture changes on phrase boundaries and points of emphasis; a visual change (cut,
shot size, graphics) at least once every 4 s; punch-in zoom on stressed words and numbers (≤ 1 per 3–6 s). Music is
a bed, ducked under the voice.

## 4. Infographics (code, `ed_text` layers)

| what | layer | rule |
|---|---|---|
| a number that is spoken | `counter` (`gfx.counter`), `mode: number` or `roll` | the count lands on the end of the number word; ≤ 1 per 8–10 s |
| a simple chart: shares, growth, progress | `counter` with `mode: bars`, `line`, `ring`, `progress` and `data` | one idea per chart, large labels, 2–4 s |
| point at an object, a line, a detail | `callout` (`gfx.callout`): `arrow`, `ring`, `pin_label`, `spotlight`…; the target is a point or a tracked object | ≤ 1 per 3–4 s, do not cover the face |
| the speaker's name and role | `lower_third` (`plate`, `minimal`, `location`, `topic`, `handle`) | 0.5–1 s after their first appearance, 3–5 s, once |
| headline, key point, chapter | `title_card` / `intertitle` | ≤ 7 words, in the safe zone |
| key words | `kinetic` | 1–3 words large, 0.4–0.5 s per word |
| route, places | `route_map` | the line draws on with the voice, point labels |

Layer fields: the `ed_text` docstring and `edit-director/references/edl-cookbook.md`. Check the numbers and facts on
screen against the user's data twice — an error in an infographic is worse than no infographic. 9:16 safe zone:
top 12 %, bottom 20 %, right 12 %; no more than two graphics layers at a time, not counting subtitles.

## 5. Subtitles, audio, checks

- Captions from the words of the voice with a preset (`references/subtitles.md`), the block at y 0.58–0.78, not
  on the face, never over the source's own captions.
- Mix: the voice leads, music −18…−24 dB under the voice, −14 LUFS, true peak ≤ −1 dBTP.
- edit-director QA (`speech`, `parts`, `safe_zone`, `faces`): 0 cuts inside words, ≤ 20 characters/s as displayed,
  text and graphics inside the zone, faces whole, overlays out of the crop; the numbers on screen match the data.
