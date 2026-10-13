---
genre: fashion
slug: fashion
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16", "4:5"], duration_s: [10, 40], typical_s: 20}
structure:
  - {part: hook,  t: "0–2 s (0–10 %)",   goal: "a magazine cover: the model in the center with a big word behind, or a photo flash with a freeze frame — 'this is stylish' in one second"}
  - {part: build, t: "2–8 s (10–40 %)",  goal: "a closer look: texture, details, a mirror, a walk toward the camera — the look comes together"}
  - {part: drop,  t: "8–18 s (40–90 %)", goal: "a kaleidoscope of looks: a look change on every beat, photo flashes, a choppy step, strobes"}
  - {part: outro, t: "18–20 s (90–100 %)", goal: "the final pose and the sign-off: the heroine or hero in slow motion, the collection title"}
rhythm:
  shot_len_s: {hook: [1.0, 2.0], build: [0.5, 1.5], drop: [0.45, 1.0], outro: [1.0, 2.5]}
  cut_grid: {hook: "one shot per bar or a cut on beat 3; the title on beat 1", build: "every 2 beats, details one beat each; light flashes on the snare without a cut", drop: "a look change on every beat (at 135+ BPM every other beat); downbeat — a photo flash with a freeze frame; a cut.flash stream from downbeat to downbeat", outro: "once per bar"}
  on_beat_share: 0.9
  max_shot_s: 3.0
moves:
  hook:  [type.behind_subject, trans.flash, time.freeze, shot.video_portrait, track.lead, type.title_card]
  build: [light.flash, shot.extreme_close_up, cut.insert, pov.mirror, track.lead, time.slow_motion, cut.match]
  drop:  [cut.jump, trans.flash, time.step_print, cut.flash, time.freeze, layout.frame_division, light.flash, cut.match]
  outro: [shot.video_portrait, time.slow_motion, type.title_card, trans.flash, type.credits]
  signature: [trans.flash, light.flash, time.step_print, cut.jump, type.behind_subject]
  allowed: [arc.horizontal, arc.orbit, orbit.turntable, rig.robot_arm, tilt.basic, track.subject, angle.overhead, angle.profile, frame.central, frame.tableau, cut.dance, reflect.mirror, anim.pixilation, anim.stop_motion, focus.bokeh, focus.shallow, light.halation, light.hard, trans.arc, trans.chain, trans.side_scroll, trans.wipe, time.echo_trail, time.motion_blur, fx.color_shift, fx.kaleidoscope, fx.refraction, fx.wigglegram, layout.aligned_split, gfx.collage, type.repeat, anim.line_art, scene.void, scene.levitation, product.shoes, look.film, look.photo_prints, look.maximalism]
  forbidden: [gfx.counter, gfx.callout, type.karaoke, fx.bobblehead, fx.living_object, anim.doodle_overlay, look.cheesy, look.news]
sfx: {hook: [sfx.glitch], build: [sfx.whoosh], drop: [sfx.glitch, sfx.impact], outro: [sfx.impact]}
looks: [look.film, look.photo_prints, look.maximalism]
---

# Fashion

## Goal and platform
A fashion and beauty edit: a lookbook, look changes, "get ready with me", a collection teaser, a model's or stylist's portfolio.
9:16 for short-video feeds (and 4:5 for the profile grid), 10–40 s, typically 20 s (10 bars at 120 BPM; house, techno,
afro and pop are more often 115–128 BPM). The hero is the look: the silhouette, the fit of the garment, the fabric texture, the makeup and the face must read clearly and
look expensive. The genre's language: photo flashes and freeze frames as on a shoot, strobes, mirrors, a choppy stepped motion,
look changes on the beat in the same framing, and typography laid out like a magazine cover. Differences from neighbors: viral — humor and any
material with a loop; phonk — aggression and bass; fan edit — a film character and the song lyrics; fashion — beauty and precision of the look:
no comedic body distortion, the colors of the clothes never lie.

## Structure by seconds
Seconds are for 120 BPM (beat 0.5 s = 15 frames @30 fps / 12.5 @25 fps, bar 2 s).

| part | time (20 s) | bars | on screen | in the music |
|---|---|---|---|---|
| hook | 0–2 s (0–10 %) | 1 | the "cover": the model centered, full length or waist up, a big word behind the model on beat 1; or a photo flash + a 0.5 s freeze with a shutter click | the first bar with the kick; no intro |
| build | 2–8 s (10–40 %) | 3 | a burst of details (fabric, hardware, shoes, lips, eyes), a mirror, a 2–3 s walk toward the camera, hair and fabric in slow motion; light flashes on the snare | verse or rise, hats and snare |
| drop | 8–18 s (40–90 %) | 5 | a look change on every beat in the same framing; on the downbeat — a photo flash and a 0.3–0.8 s freeze; stepped motion; a cut.flash stream of looks for 1–2 s; a frame split into looks | drop or chorus |
| outro | 18–20 s (90–100 %) | 1 | the final pose in slow motion, the collection or name title, the last flash; optionally a credits card for 1–2 s | the last phrase or the final chord |

Drop order by bars: beat 1 — flash and freeze (look A, 1 beat); beats 2–4 — looks B, C, D change on cuts in the same
framing; the next bar — a step-printed walk or a cut.flash stream; a new device every 2 bars so it does not turn into a slideshow.
Track window: start on a downbeat, the track's drop at 35–45 % of the video; the length is a whole number of bars.

## Rhythm
- Lengths: hook 1–2 s; build 0.5–1.5 s (details one beat each, 0.5 s; the walk 2–3 s — that is max_shot); drop 0.45–1.0 s per
  look (one beat or two, with 0.3–0.8 s freeze frames inside); separate devices — a cut.flash stream of 2 frames per image and a step-printed
  walk of 1.5–3 s; outro 1–2.5 s.
- Grid: hook — one shot per bar or a cut on beat 3, the title enters on beat 1; build — a cut every 2 beats,
  a series of details one beat each, light flashes (light.flash) on the snare without a cut; drop — a look change on every beat (at
  135+ BPM every other beat: a look must read for ≥ 0.45 s), a photo flash with a freeze on the downbeat, the cut.flash stream
  starts and ends on downbeats; outro — once per bar.
- Share of cuts on the grid ≥ 0.9; look changes exactly on beats ±1 frame (this is the genre's main "click").
- Pace curve: build 1–1.5 cuts/s → drop 2 look changes/s plus freezes → outro 0.5/s; stepped motion and strobe add
  nervous energy without speeding up the cutting.
- Pauses: the freeze frame is the genre's "pause"; 1 beat of silence before the drop is allowed if the track has a break.

## Shot selection
1. Silhouette: for looks — full-length or waist-up shots, the person mask 15–45 % of the area, the whole figure in frame
   (the mask's bounding box does not touch the top or bottom edge, except intended waist-up shots), center x 0.38–0.62.
2. Grouping looks: cluster the shots by clothing color (HSV histogram inside the person mask, k-means) —
   one cluster = one look; look order — alternating light/dark or going around the color wheel.
3. Change in the same framing (cut.jump): candidates are pairs of shots with a similar background outside the mask (correlation ≥ 0.8), the person's
   bounding-box center within 3 % of the frame and height ±5 %; if the boxes differ — align the frame by the mask (shift and scale), otherwise
   the change reads as a mistake.
4. Details: sharp_rank ≥ 0.7, rich texture (high-frequency energy in the top third across the video), extreme close-up
   (no face, or face_h > 0.33); one action or one item per piece.
5. Face and beauty: for a freeze frame — the sharpest face frame within a ±3-frame window; blinks are filtered out by a contrast drop in the eye
   area (the face detector's eye points) of more than 30 %; skin without motion blur.
6. Strobe (light.flash) — only on dark and evening shots (mean luma ≤ 110), where the flash reads as light.
7. Walks toward the camera and stepped motion — the hero moves evenly, height 35–100 % of the frame height, the camera without jerks.
8. Repeats: each look appears 1–3 times; one source shot ≤ 2 times; ranges do not overlap.
9. Crop: 9:16 by the person with 4–8 % of the height as headroom; total crop ≤ ×2.0 — fabric texture and skin must not
   get "mushy"; 4:5 — reframe by the same mask.

## Moves by part
**Hook.** type.behind_subject — the title word behind the model (a giant word of 30–60 % H behind the head, or blocks above and
below the head), entering "from behind the back" in 0.2 s (outExpo) on beat 1. trans.flash — the photo variant: 1 frame of white or an overexposure
of +3…+4 EV with glow. time.freeze 0.5 s after the flash — "the snapshot". shot.video_portrait and track.lead —
from the sources: a pose to camera or a walk toward the camera. type.title_card — a poster with a high-contrast serif if the word behind
the hero does not work (busy background, the hero narrower than 20 % of the width).
**Build.** light.flash — single flashes of 2–4 frames on the snare or a strobe reveal in a dark scene (light 0.24–0.4 s,
darkness 1–1.5 s), no more than 3 flashes per second. shot.extreme_close_up — a series of 3–4 details of 0.55–1.1 s each.
cut.insert — an axial insert ×2 into a detail on a downbeat. pov.mirror — getting ready at the mirror, optionally a look change in the mirror on
every 1/8 (10–15 changes). track.lead — a 2–3 s walk toward the camera. time.slow_motion ×0.4–0.5 — hair, fabric,
a turn. cut.match — a pose rhyme across different looks and places.
**Drop.** cut.jump — a look change on every beat in the same framing (background ±3 %, scale 1.00 ± 0.03), a series of 2–7 changes; optionally
alternating ×1.0/×1.15. trans.flash — a photo flash on the downbeat (white or a color from the look's palette: the most
saturated of the 5 clusters), ≤ 40 % of cuts. time.step_print — the choppy step: hold 3 frames @25 fps / 4 @30 fps (≈8 unique
frames/s), blur 0.8–1, phase changes on 1/16, a stretch of 1.5–4 s. cut.flash — a lookbook stream: 12–25 looks of 2 frames each
(≈12 changes per second @25 fps, 15 @30 fps), anchor — the body center or the eyes ±3–5 % of the frame, 1–2 s from downbeat to downbeat;
brightness of adjacent looks matched (safe mode). time.freeze 0.3–0.8 s — a freeze on the look after the flash,
≤ 1 per bar. layout.frame_division — 2–4 looks in strips without gaps, rearranged on every beat, closing up on
the downbeat, once. light.flash — strobe on the snare in dark looks. cut.match — the look changes in the same pose.
**Outro.** shot.video_portrait — the final pose, 1.5–2.5 s. time.slow_motion — a turn or a sweep of fabric. type.title_card
— the collection name, the name of the model or of the user's brand. trans.flash — the last flash on the final beat.
type.credits — one card of 1–2 s with 1–3 roles (model, stylist, photography), if the user provided the names.
**Limits per 10 s:** all flashes (trans.flash + light.flash) ≤ 3 per second and ≤ 12 per 10 s, red ≤ 1 per second;
freeze frames ≤ 1 per bar; stepped motion ≤ 2 stretches per 20 s, ≤ 5 s each; cut.flash ≤ 1 stream per video (≤ 2 in
videos of 30+ s); layout.frame_division ≤ 2 per video; text blocks ≤ 3 per video.
**Genre signature:** trans.flash, light.flash, time.step_print, cut.jump, type.behind_subject — "flashes, strobes,
choppy steps, look changes on the beat, typography". Mirrors — pov.mirror in build; reflect.mirror and the symmetry of
fx.kaleidoscope and layout.aligned_split are in allowed. A "choppy stop-motion" in code is time.step_print; real
pixilation of the model (anim.pixilation) and object stop-motion of accessories (anim.stop_motion) come from the sources or
the user's photo series, 1 episode of 1–2 s per video.
**Allowed:** shooting techniques that the cards mark as signature but that cannot be done in code — arc.horizontal, arc.orbit,
orbit.turntable, rig.robot_arm, tilt.basic, track.subject, angle.overhead, angle.profile, frame.tableau, cut.dance,
product.shoes — used when they exist in the sources; frame.central and focus.bokeh — in code (centering, a background of lights);
focus.shallow, scene.void, scene.levitation — with a mask; light and optics — light.halation, light.hard; transitions —
trans.arc, trans.chain, trans.side_scroll, trans.wipe; time — time.echo_trail, time.motion_blur; color and form —
fx.color_shift, fx.kaleidoscope, fx.refraction, fx.wigglegram, layout.aligned_split; graphics — gfx.collage, type.repeat,
anim.line_art; looks — look.film, look.photo_prints, look.maximalism. All of them are signature for fashion according to their cards,
but they need a special shot or shooting style, so they are not in the skeleton — the engine places them based on the material and on request.
**Forbidden:** gfx.counter and gfx.callout — infographics and arrows turn the look into a product listing; type.karaoke —
the tone of a lyric video; fx.bobblehead, fx.living_object, anim.doodle_overlay, look.cheesy — comedy distorts the body and
cheapens the look; look.news — TV lower thirds work against luxury.

## SFX
- The music leads; sounds are only "photo-shoot" sounds, and rare.
- Hook: sfx.glitch "shutter" variant (a 3 kHz click + a second 1.5 kHz click 40 ms later at −4 dB + a dull 180 Hz sine
  for 15 ms at −10 dB), −14 LU, align='attack' on the flash frame.
- Build: sfx.whoosh swish (0.15–0.3 s, −10 LU) — only under a fast walk into the camera or a jerk with real movement.
- Drop: a shutter (sfx.glitch) on every photo flash with a freeze, ≤ 1 per bar and ≤ 6 per 10 s — not on every look change;
  a gentle sfx.impact ("soft", −10 LU) on the first look of the drop, only if the track has no kick on that beat.
- Outro: sfx.impact soft or boom (−6 LU) when the title appears.
- Do not duck the music under shutters; under the hit — 30–150 Hz −3 dB. In total ≤ 8 sounds per 20 s.

## Color
- Direction: clean "editorial" color with soft blacks, accurate skin and accurate garment colors.
- Engine (default): grade={preset:'natural', auto:0.5, contrast:1.12, sat:0.92, temp:0.02, fade:0.015, gain:0.97}.
- Contrast ×1.10–1.20; saturation ×0.85–1.0 (muted, the accent is the garment); balance temp 0…+0.05, tint 0; black
  point slightly lifted — fade 0.015 (≈4/255, matte shadows); white 247/255 (gain 0.97) with a soft shoulder; skin —
  hue 15–35°, saturation ≤ 0.5; do not shift the hue of the clothes by more than 3°.
- Night photo flash: contrast 1.25, sat 0.95, black 0.03 (crushed shadows), light.halation 0.2–0.3.
- B&W edition: preset bw_hi (contrast 1.45, black 0.04) on the hook or build; color returns on the drop beat (fx.color_shift).
- Not allowed: strong teal-orange and monotones that change the color of the garment (except short accents ≤ 1 beat).
- Looks: look.film (grain level 1–2), look.photo_prints (photo prints in the intro or outro), look.maximalism (campaign).

## Text
- Class: a high-contrast serif with strong stroke contrast or a wide sans-serif in uppercase with tracking +8…+15 %;
  ≤ 2 typefaces per video; fonts cover the caption language; OFL.
- The word behind the hero: 30–60 % H (in 9:16 width ≤ 90 % W), behind the head; no letter overlaps the face; the blocks above and
  below the head in 9:16 — y 0.12–0.30 and 0.62–0.80.
- Look labels ("look 03", item, material): 2.4–3.2 % H in uppercase, tracking +12 %, on the left at x 0.08, y 0.70–0.78;
  they appear on a cut on the beat and hold ≥ 1 s or until the look changes.
- The collection title in the outro: 6–10 % H, center y 0.40–0.55; credits (type.credits) 2.4–3.2 % H, 2–3 lines, ≥ 1.5 s.
- Animation: on a cut on the beat, "from behind the back" in 0.2 s for the title, letter-by-letter typing for labels; no bounces or springs.
- Color: white, black or cream; the accent is the garment's color (k-means over the look's mask); contrast ≥ 4.5:1.
- Safe zone 9:16: y 0.12–0.80, x 0.06–0.88; 4:5 — 5 % margins on all sides.

## Quality checks
- Flashes: all together ≤ 3 per second with a brightness change > 10 % over > 25 % of the frame area; strobe rate ≤ 3 Hz;
  red ≤ 1 per second.
- Look change in the same framing: adjacent looks — background outside the mask shifted ≤ 3 % of the frame, scale 1.00 ± 0.03 (ECC), IoU of the person
  masks ≥ 0.7; changes on beats ±1 frame.
- Freeze frames 0.3–0.8 s (hook up to 1 s); freezedetect finds only the planned freezes.
- Garment color: ΔE76 of the mean clothing colors within the mask before and after the grade ≤ 6 (except B&W stretches); skin after the grade —
  hue 15–35°.
- Stepped motion: 6–9 unique frames per second, stretch ≤ 5 s.
- cut.flash: the anchor stays within ±5 % of the frame, ≥ 12 different images, adjacent ones differ in mean
  relative brightness by ≤ 0.1, large brightness changes ≤ 3 per second.
- Text: 0 letter pixels inside the face mask; all text within the safe zone; contrast ≥ 4.5:1.
- Grid: cuts_on_grid_share ≥ 0.9; max_shot ≤ 3.0 s.
- Loudness: −14 LUFS ±1, true peak ≤ −1.0 dBTP; crop ≤ ×2.0, face_issues = 0.
