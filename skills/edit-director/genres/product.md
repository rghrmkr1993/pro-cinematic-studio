---
genre: product
slug: product
kind: music
platforms: [TikTok, Reels, Shorts, marketplace listing video]
format: {aspect: ["9:16", "4:5", "1:1"], duration_s: [10, 30], typical_s: 20}
structure:
  - {part: hook,  t: "0–2 s (0–10 %)",     goal: "stop the scroll with a recognizable product detail in close-up: what is it and why does it look so good?"}
  - {part: build, t: "2–8 s (10–40 %)",    goal: "build desire: 3–4 details and facts, one per 1–2 beats; the whole product is not shown yet, the reveal starts in the last bar"}
  - {part: drop,  t: "8–16 s (40–80 %)",   goal: "the reveal: the whole product exactly on the first downbeat of the drop, then the feature in action, a spin and a wow shot"}
  - {part: outro, t: "16–20 s (80–100 %)", goal: "a centered packshot with the name, the key fact or the price and a call to action: the viewer knows what to buy and where"}
rhythm:
  shot_len_s: {hook: [1.0, 2.0], build: [0.5, 3.0], drop: [0.5, 2.7], outro: [2.0, 4.0]}
  cut_grid: {hook: "the first frame is already the product; 1–2 shots: cut on downbeat 1, the second shot from beat 3", build: "shot change every 1–2 beats (0.5–1 s); a callout lands on a beat, its label on the next half-beat; last bar: the reveal move or a ladder of inserts on 1/2 beats", drop: "the reveal lands on the first downbeat of the drop (±1 frame); then 1–2 beats per shot, a burst of details on 1/2 beats no longer than 1 bar, the spin plays whole over 1–2 bars (2–4 s) and is not split", outro: "the packshot enters on the downbeat of the last phrase and holds to the end: 1–2 bars; the last hit of the track = the last frame"}
  on_beat_share: 0.85
  max_shot_s: 4
moves:
  hook:  [shot.extreme_close_up, focus.shallow, dolly.in, type.kinetic]
  build: [cut.insert, gfx.callout, truck.lateral, angle.overhead_close, type.kinetic, gfx.counter]
  drop:  [product.hero, orbit.turntable, time.super_slow_motion, rig.robot_arm, cut.quick, zoom.punch, trans.flash]
  outro: [frame.central, scene.void, zoom.slow, type.title_card, time.cinemagraph, gfx.callout, gfx.counter]
  signature: [product.hero, shot.extreme_close_up, cut.insert, gfx.callout, orbit.turntable]
  allowed: [time.slow_motion, time.speed_ramp, time.freeze, zoom.out, cut.match, cut.vector_match, trans.whip, trans.zoom, fx.letterbox, focus.bokeh, light.hard, angle.low, fx.film_overlay, layout.split_screen, type.subtitles, product.bottle_hero, product.shoes, product.car, angle.ground, pov.object, lens.probe, crane.telescopic, rig.locked_on, trans.screen, trans.set_change, anim.stop_motion, scene.tiny_people, fx.living_object, anim.cgi_3d, anim.live_mix, sfx.sub_drop]
  forbidden: [shake.beat, time.velocity, time.step_print, glitch.datamosh, glitch.pixel_sort, fx.rgb_split, lens.fisheye, look.vhs, look.psychedelic, handheld.shaky]
sfx: {hook: [], build: [sfx.glitch, sfx.riser], drop: [sfx.impact, sfx.whoosh], outro: [sfx.impact]}
looks: []
---

# Product

## Goal and platform
The video sells one specific product: it shows the product better than a photo does, gets across 2–4 key advantages and
leaves the packshot with the name and a call to action in the viewer's memory. Platforms: TikTok, Reels, Shorts (9:16),
a marketplace listing video and in-feed seeding (4:5, 1:1). Length 10–30 s, typically 20 s: 10–15 s for a listing and
an ad, 30 s if the product needs a feature demonstration. It is mostly watched with the sound off, so every fact is
duplicated in text, and the music has no vocals or has vocals only in the instrumental breaks.

How it differs from neighboring genres: from UGC, there is no talking head and no "everyday" camera; the frame is clean,
the light sculpts the contour, the product is always the center of attention; from teaser, the product is shown whole
and with facts, the intrigue lives only in the hook; from fashion, the hero is an object, not a person and a look, and
the rhythm is calmer (a cut every 1–2 beats, no strobes and no choppy stop motion); from epic, there is no slow motion
for mood's sake: every shot answers "what is it and why do I need it".

## Structure by seconds
Times are given for 20 s at 120 BPM (beat 0.5 s = 12.5 frames @25 fps / 15 @30 fps, bar 2 s). The track is cut so
that the first drop (`drops[0].t` from ed_audio) falls at 35–45 % of the video length and the end of the video lands
on a downbeat.

| part | time | music | on screen | which shot to use |
|---|---|---|---|---|
| hook | 0–2 s, bar 1 | intro or the first bar of the verse | a recognizable detail (texture, cap, sole, button, engraving) in close-up, shallow DOF, slow push-in; optionally 1–3 words | the best macro shot: product at 60–100 % of the frame, maximum sharpness, dark or neutral background, logo not yet shown whole |
| build | 2–8 s, bars 2–4 | verse or rise; the last bar builds tension (the track's own rise or sfx.riser) | 3–4 feature details, one per 1–2 beats, each with a callout carrying a fact, or with a word; in the last bar, the reveal move from the detail to the whole | close-ups and medium shots of details in script order; overhead: "what's in the box"; a tracking move along the product or the product line |
| drop | 8–16 s, bars 5–8 | drop or chorus, the densest stretch | on the first downbeat, the whole product (the reveal landing); then the feature in action with a hand, the product in hands, a spin on a turntable, a wow shot (a splash, a pour, a camera rush to a detail) | the best and most dynamic shot goes on the first beat of the drop; the feature with a hand; an HFR splash, if available |
| outro | 16–20 s, bars 9–10 | the last phrase, the final hit or an ending on the bar | the packshot strictly centered on a clean background, zoom-in ×1.05–1.08, the name, the price or the key fact, a call to action | the cleanest centered packshot; if there is none, build one from a product photo (background removal + void) |

Other lengths: 10 s: hook 1 s, build 3 s, drop 4 s, outro 2 s; 15 s: 1.5 / 4.5 / 6 / 3 s; 30 s: 2 / 10 / 12 / 6 s
(the drop holds two four-bar blocks: "reveal + spin" and "feature + wow shot"). The packshot is no shorter than 2 s
(2.5 s on a marketplace), the drop no shorter than 2 bars.

## Rhythm
- Shot length: hook 1–2 s (1–2 shots), build 0.5–3 s (a detail 1–2 beats, a shot with a series of callouts 2–3 s), drop
  0.5–2.7 s (the reveal 1.3–2.7 s, a feature 1–2 beats, a burst piece 0.25–0.5 s), outro 2–4 s. The longest shot is
  the spin or the packshot, 4 s (2 bars).
- Grid: cuts on a beat or half-beat ±1 frame, at least 85 % of cuts; the rest on action (a cap click, a touch, a hand
  entering), but no further than a half-beat from the grid. The strongest cut is the first beat of the drop.
- Pace over the track: average shot 1.5 s in the hook → 0.9 s in the build → 0.7 s in the drop (with landings) → 3 s in
  the outro: "acceleration → hit → exhale". The shortest readable product shot is 0.4 s (10 frames @25 fps, 12 @30 fps);
  a shot with a kinetic word is no shorter than 0.5 s, a shot with a callout no shorter than 1.5 s + 0.3 s per word of
  the label.
- Tempo adjustment: at 90–100 BPM, a shot change on every beat; at 120 BPM, every 1–2 beats; at 140+ BPM, every 2 beats
  (otherwise shots get shorter than 0.4 s) and bursts only on beats, not on half-beats.
- Pauses: if the track has a "breath" before the drop (the bass drops out for a half-beat to a beat), the reveal is not
  interrupted: it still lands on the first beat of the drop. There is no silence and no black frames inside the video.

## Shot selection
1. Product tracking: `track(object:<product>)` on every source (detector + optical flow, re-detection every 10
   frames); if the class is not recognized, the user points out the product once ("the bottle in #3").
2. Scoring 0.5–3 s windows: the product's share of the frame; sharpness inside the product mask (Laplacian variance
   ≥ 0.6 of the clip maximum); stability (jitter ≤ 0.3 % of the frame); clipping inside the mask ≤ 0.5 % of pixels at
   255 (the label is readable); background cleanliness (texture energy outside the mask; third-party text and logos are
   found by OCR and a logo detector, and such windows are discarded); color vs. the reference ΔE2000 ≤ 3; motion energy
   (mean optical-flow magnitude).
3. Where things go:
   - hook: the maximum of "sharpness × product share 0.6–1.0 × clean background"; the detail is recognizable, but not
     the whole logo; shallow DOF (sharp-to-soft ratio 2.3–5); no hands;
   - build: one feature per shot in the order of the script or the user's text; for a callout, the product takes
     ≥ 3 % of the area, stays in frame ≥ 1.5 s and moves ≤ 2 % of the frame per frame; the kit: an overhead view; the
     product line: a lateral tracking move; medium energy;
   - drop: first beat: the window with the highest "value" (product at 30–60 % of the height, center ±5 %, motion
     energy in the top 20 %: a reveal, an orbit, a splash); a feature: the hand enters 0.3–0.7 s after the cut and
     leaves before the next one; clips at 120+ fps per metadata are candidates for super slow motion; orbits and spins
     go here too;
   - outro: center ±5 %, static (jitter ≤ 0.1 %), product at 30–60 % of the height, ≥ 2 s, a texture-free band above or
     below the product for the name and the call to action.
4. Avoid: a product cut off by the frame edge (except macro), dust and fingerprints on glossy surfaces (small bright
   specks inside the mask), reflections of the crew and the phone, third-party brands and text, a cluttered background,
   color that has drifted from the reference, handheld shake, a crop larger than ×2 from a 1080p source.
5. Repeats: each source window is used once; one clip gives no more than 2 windows, and they differ in shot size by
   ≥ ×1.3 or in angle; the same angle twice in a row is forbidden; no more than 2 macro shots in a row without a shot of
   the whole product (context).
6. What is missing and how to replace it: macro: a crop from 4K (an axial insert up to ×2.7), otherwise generation with
   consent; packshot: from a product photo (`mask(method='hf_remove_background')` + scene.void); spin: a series of
   photos taken around the product, or `generate_3d`; the product's "world" and the feature in action: generation from
   the product photo with the user's consent.

## Moves by part
**Hook.** shot.extreme_close_up — the detail fills 50–100 % of the frame, 1–2 s, with a zoom-in ×1.04–1.12 inside the
shot; focus.shallow — sharp zone 20–45 % of the frame, background blurred into discs (synthetic DOF only via a mask with
a depth map); dolly.in — if the sources contain a real push-in, it beats a digital one; type.kinetic — 1–3 hook words
("thinner than a pencil"), pop ×0.9 → 1.07 → 1.0 over 7 frames, beside the product, not over it. No callouts and no
prices: the hook is pure spectacle.

**Build.** cut.insert — an insert on a detail ×2–3 (from 4K or a separate shot), 0.5–1.5 s, on a beat, back to the wide
after 2–3 details; gfx.callout — a pin with a fact of ≤ 24 characters on a detail, a series of 2–3 pins on one shot, one
per beat (shot 2–3 s; the third pin replaces the first, ≤ 2 on screen), each held ≥ 1.5 s + 0.3 s per word;
truck.lateral — a tracking move along the product or the product line, 1–2 s, cut on the frame where the nearest object
covers more than half of the frame; angle.overhead_close — "what's in the box", 3–6 overhead inserts of 0.5–0.7 s on
beats, then the whole set in one shot; type.kinetic — a list of advantages, 0.4–0.5 s per item between product shots
(not over the callouts); gfx.counter — one spec as a number (capacity, weight, runtime hours), counting for 0.8–1.2 s,
landing on a downbeat. The last bar of the build: the reveal move product.hero (see drop) or a ladder of inserts
1 → 1.4 → 2.6 on 1/2 beats (cut.insert) with the largest step on the last beat before the drop.

**Drop.** product.hero — the reveal from the detail to the whole: a pull-out ×0.3–0.7 over 1.3–2.7 s with an arc of up
to 45°, inOutCubic, landing with the product centered exactly on the first downbeat of the drop; from a 4K packshot in
code: `transform(scale=[2.5, 1], center=track(object), rotate=[-10, 0], ease='inOutCubic')`. trans.flash — one exposure
flash (+2…+4 EV, 2-frame peak, decay τ 60 ms) on the cut into the drop, if the reveal starts with a cut; a white fill
will not do, it eats the product's color. orbit.turntable — a spin on a turntable, played whole over 1–2 bars (2–4 s):
a full 360° in 3.5–4 s (≈100°/s) or a slow 60–120° turn (25–35°/s); the light stays fixed, so highlights run across
the product; once per video.
time.super_slow_motion — a splash, a pour, powder: only from 240+ fps (`speed(rate=25/source_fps, interp='drop')`),
2–4 s on screen, once per video; without HFR, time.slow_motion ×2 (from 50–60 fps) or a freeze at the peak + zoom-in.
rig.robot_arm — a camera rush to a detail, 0.3–0.5 s, with a hard landing on a downbeat; in code only on 4K and no
longer than 0.4 s. cut.quick — a burst of features, 4–6 pieces of 1/2 beat (0.25 s) or of a beat, no longer than 1 bar,
one action per piece, the cut 0.14–0.28 s after the action peak, the landing a 1–1.5 s hold on the product.
zoom.punch — ×1.1–1.2 without motion blur (shutter 0) on the downbeats of the drop, no more than 1 per bar and 4 per
video; not on top of a running reveal or spin.

**Outro.** frame.central — the product strictly centered (0.48–0.52), horizon and shelves level; scene.void — the
product on a smooth dark or light field without walls (from a cut-out, with a soft 30–40 % shadow and level-1 grain
against banding on the gradient); zoom.slow — a zoom-in ×1.05–1.08 over the whole packshot, linear; type.title_card —
the product name (and the logo mark, if the user provided it) over the packshot, fade-in 0.4–0.6 s, held to the end;
time.cinemagraph — a food or drink packshot: only the steam, the bubbles or a drop move, loop 0.6–2 s; gfx.callout — a
price sticker by the product (rotated 4–8°, bounce ×1.15) or one callout with the key fact; gfx.counter — the price
"was → now" (the old number is struck through over 6 frames, the new one rolls up over 1 s). The price is either a
sticker or "was → now", not both.

**Situational (allowed).** By product category: product.bottle_hero — drinks and bottles (a flavor change on a beat or
a bar), product.shoes and angle.ground — footwear (a step = a beat), product.car — cars (an orbit with the reveal on the
drop), lens.probe — food and ingredients (a 1.5–3 s pass in the build), pov.object — the product "looks" at whoever
picks it up (hook or build, 2–3 s), trans.screen — gadgets and apps, crane.telescopic — a glide over the table to the
product (once, ≥ 1.5 s), rig.locked_on — the product stays put in the frame while the world spins around it (1–2
fragments on beats). By footage: time.slow_motion (×2 if there is no HFR), time.speed_ramp (one ramp on a pour or a
throw, the slowdown on a beat), time.freeze (a freeze at the splash peak + a callout), zoom.out (a reveal in code if
there is no 4K for product.hero), cut.match (the product rhymes with a shape from everyday life), cut.vector_match (a
series of details in one gesture), trans.whip and trans.zoom (a color or model change on a downbeat), angle.low (the
product as a monument), light.hard and focus.bokeh (light and backdrop from the source), layout.split_screen (comparing
colorways or "with / without", top/bottom). By style, only on request: fx.letterbox (bars slide in on the reveal),
fx.film_overlay (level-1 grain, no dust on macro), type.subtitles (if there is a voiceover), anim.stop_motion (the
product assembles or unpacks "by itself", 1–2 s), trans.set_change (the set around the product leaves on a beat),
scene.tiny_people and fx.living_object (a playful tone, a mascot), anim.cgi_3d and anim.live_mix (generation only, with
the user's consent). Every move the cards mark as signature for product is used, either in the parts or here: category
and generative moves do not suit every product, so they are not in the parts.

**Limits per 10 s:** callouts ≤ 3 (≤ 2 on screen at once), punches ≤ 2, cut.quick bursts ≤ 1. Per video: kinetic
text no more than 30 % of the running time, the exposure flash: 1, on the entry into the drop, super slow motion and the
spin: 1 each, slow motion of all kinds ≤ 25 % of the running time.

**Forbidden.** shake.beat and time.velocity — the product shakes and smears, neither the shape nor the label reads;
time.step_print — choppy step printing gives a "cheap" effect on a premium object; glitch.datamosh and glitch.pixel_sort
— melt and recolor the product; fx.rgb_split — color fringes ruin the brand color and the contour; lens.fisheye —
distorts the product's proportions; look.vhs and look.psychedelic — change the product's true color and sharpness (the
same goes for look.drunk, look.dystopian, fx.night_vision: they are outside the genre's tone); handheld.shaky — a product
is shot on a tripod, slider or stabilizer, and shake reads as a defect.

## SFX
- The main sound is foley from the sources: a cap click, a zipper, a pour, fabric rustle, a button click; raise it by
  +3…+6 dB on detail shots. Synthesized sounds only on frame movement and events.
- build: sfx.glitch (a single "tick") on a callout pin if the pin lands off the beat, −18…−22 dB relative to the music,
  `align='attack'` on the frame where the dot appears; pins on beats get no sound. sfx.riser only if the track itself
  does not build: the last 1–2 bars before the drop, cut off exactly on the first beat of the drop, its level by the end
  −6 dB relative to the music.
- drop: sfx.impact on the reveal landing (the first beat of the drop): the "boom" variant at −6…−8 LU relative to the
  music if the track has a weak kick; with a powerful kick, only a gentle "soft" at −12 dB or nothing. sfx.whoosh on the
  robot-arm rush, a whip or a crash zoom: peak in the middle of the move, −10…−14 dB. A sub drop instead of the hit is
  allowed, but not together with it at full level.
- outro: a soft hit or a "metal" ring on the packshot landing at −10 dB, then the music tail up to the downbeat.
- Limits: ≤ 6 synthesized sounds per 20 s; the main hit: 1 per video (≤ 1 per 15 s); the riser: 1.
- With a voiceover: the music under the voice at −12…−15 dB (`duck(music, under=voice)`), SFX only in speech pauses
  ≥ 150 ms.
- Master loudness: −14 LUFS integrated, true peak ≤ −1 dBTP; the limiter reduces no more than 3 dB on hits.

## Color
- The product's true color matters more than a "look": the median Lab inside the product mask vs. the reference (a
  product photo or a color from the user): ΔE2000 ≤ 3; a deviation is corrected locally through the mask, not on the
  whole frame.
- Base: contrast +5…+10 % (gentle S-curve, pivot 0.45), saturation of the whole frame 0…+5 %, the background and the
  "world" through the mask up to +10…+15 %; neutral white balance: a gray background with a*, b* within ±2; black point
  4–8 of 255 (keep a dark studio background at 30–75), white point 245–250 with a soft shoulder: clipping inside the
  product mask ≤ 0.5 % of pixels; the skin of the hands natural (hue 20–30°, no pink or green cast).
- Consistency: the product's average brightness in neighboring shots differs by no more than 8 %, background ΔE ≤ 4;
  one grade for the whole video.
- Sharpness: after a crop of ×1.3+, unsharp 0.3–0.5; only gentle noise reduction, texture is the product's main
  argument.
- No looks by default; level-1 fx.film_overlay grain without dust and fx.letterbox bars on the reveal are allowed.

## Text
- Font: one sans-serif typeface (neutral or geometric, covering the caption language, OFL), weights 500 / 700 / 900, tabular
  figures for numbers. Color: white #FFFFFF on dark or #111 on light, one accent from the product's palette; contrast
  ≥ 4.5:1.
- Sizes in 9:16 (% of the frame height H): hook words: 1–3 words across 70–86 % of the width (≈10–14 % H); the list of
  advantages: 5–7 % H, ≤ 3 words; a callout label: 2.2–2.8 % H, ≤ 18 characters per line, ≤ 2 lines; a counter
  number: ≤ 72 % of the width (≈9–13 % H), the unit 2.4–3.0 % H; the name on the packshot: 6–9 % H; the price: 7–10 % H;
  the call to action: 3.5–4.5 % H. In 4:5 and 1:1, the same fractions of the frame height, labels no smaller than 3 % H.
- Placement: everything inside x 0.06–0.88 and y 0.12–0.80 (the top 12 %, the bottom 20 % and the right 12 % are
  platform UI); text does not touch the product mask (gap ≥ 2 % H) and sits on the free side (`free_side`); on the
  packshot, the name goes above the product (y 0.14–0.30) or below it (0.62–0.78), the call to action at the bottom, but
  no lower than y 0.78.
- Animation: one entry animation per video: pop ×0.9 → 1.07 → 1.0 over 7 frames @25 fps (outBack); callouts per the
  gfx.callout card (dot 4 frames, line 6–8, box 6–8, text 4); the name: fade-in 0.4–0.6 s; exit: a cut on the next
  beat.
- Sync: words enter on a beat ±1 frame; a word holds 0.4–0.5 s (no less than 0.3 s per word); a callout ≥ 1.5 s + 0.3 s
  per word; the call to action ≥ 1.5 s, the name and the call to action stay until the last frame.
- Content: facts and prices come only from the user, the engine does not invent them; no more than 2 text blocks on
  screen at once.

## Quality checks
| check | threshold |
|---|---|
| share of cuts on a beat or half-beat (±1 frame), `cuts_on_grid_share` | ≥ 0.85 |
| reveal landing: the whole-product frame on the first beat of the drop, `qa_drop_landing` (new) | ±1 frame |
| product in frame (mask present), `qa_product_presence` (new) | ≥ 85 % of frames; first frame: product ≥ 20 % of the area |
| packshot: last shot, center, length | center ±5 %, 30–60 % of the height, ≥ 2.0 s (marketplace 2.5 s) |
| shot length | ≤ 4 s; product shots ≥ 0.4 s, except burst pieces (≥ 0.25 s) |
| product color vs. the reference, `qa_product_color` (new) | ΔE2000 ≤ 3; clipping inside the mask ≤ 0.5 %; brightness of neighboring shots ±8 % |
| crop relative to source pixels | ≤ ×2.0 (hard limit ×2.2), product sharpness ≥ 0.6 of the clip maximum |
| text: `qa_text_safe_zone(layout='tiktok')`, `qa_overlap(object)` | 100 % in the safe zone; 0 overlaps with the product mask |
| callouts: `qa_track_jitter`, numbers: `qa_numbers(source=user_data)` | jitter ≤ 0.2 % of the width per frame; all numbers match the data |
| loudness | −14 LUFS ±1, true peak ≤ −1 dBTP |
| black and frozen frames | no black frames; freezes > 0.5 s only for the planned freeze and cinemagraph |
| flashes, `flash_guard` | ≤ 3 per second; the exposure flash only at the entry into the drop, ≤ 1 per drop |
| frame jitter in product shots | ≤ 0.3 % of the frame |
| video length and ending | 10–30 s; the last frame on a downbeat |
