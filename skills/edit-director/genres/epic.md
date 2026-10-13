---
genre: epic
slug: epic
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–4 s (0–13 %)",   goal: "feel the scale from the first frame: a huge world, a small person, a low hit — the 'movie' switches on"}
  - {part: build, t: "4–16 s (13–53 %)", goal: "slow acceleration: the hero and the world come closer, shots get shorter, pressure rises; a black inhale before the drop"}
  - {part: drop,  t: "16–26 s (53–87 %)", goal: "catharsis: the best shot of the video in slow motion on the first beat, then powerful actions exactly on the beats"}
  - {part: outro, t: "26–30 s (87–100 %)", goal: "exhale and grandeur: pull-out to the landscape, the bars close in, black on the last note"}
rhythm:
  shot_len_s: {hook: [2.0, 4.0], build: [1.0, 2.0], drop: [0.5, 1.5], outro: [2.0, 4.0]}
  cut_grid: {hook: "once per bar; picture from the first downbeat, the second cut on the downbeat of bar 2", build: "staircase: 2 bars of 2 s shots → 2 bars of 2-beat shots → a bar of 1-beat shots with dips to black → 1–2 beats of black pause before the drop", drop: "first beat: slow motion for a whole bar; then every 2 beats, on orchestral hits every beat (no more than 2 bars in a row); a wide shot lasts no less than 3 beats", outro: "1–2 shots of one bar each; fade to black on the last note"}
  on_beat_share: 0.9
  max_shot_s: 4
moves:
  hook:  [shot.extreme_wide, drone.aerial, fx.letterbox, zoom.out, type.title_card, trans.fade]
  build: [time.slow_motion, angle.low, light.silhouette, zoom.slow, cut.vector_match, trans.fade]
  drop:  [time.slow_motion, time.speed_ramp, angle.low, arc.horizontal, trans.flash, shake.beat, cut.vector_match]
  outro: [zoom.out, drone.aerial, shot.extreme_wide, fx.letterbox, type.title_card, trans.fade]
  signature: [fx.letterbox, time.slow_motion, shot.extreme_wide, zoom.out, trans.fade]
  allowed: [shot.wide, angle.birds_eye, arc.orbit, zoom.extreme, scene.giant, time.bullet_time, time.super_slow_motion, time.timelapse, time.hyperlapse, cut.crash, cut.quick, cut.match, time.freeze, light.haze, fx.glow, fx.film_overlay, type.intertitle, type.subtitles, sfx.whoosh]
  forbidden: [zoom.in_out, time.velocity, time.boomerang, fx.glitch, fx.rgb_split, glitch.pixel_sort, trans.iris, trans.page, look.cheesy, fx.bobblehead]
sfx: {hook: [sfx.impact], build: [sfx.impact, sfx.riser], drop: [sfx.sub_drop, sfx.impact], outro: [sfx.impact]}
looks: [look.dystopian]
---

# Epic

## Goal and platform
An epic edit sells scale and grandeur: a huge world, a small person in it, a slow build-up and catharsis on the drop. Material: nature and travel, mountains, the sea, a city from above, sport and extreme sports, events with crowds, machinery, the user's staged "cinematic" scenes. The viewer should feel "this is bigger than me".

- Platforms: TikTok, Reels, Shorts — 9:16, 15–60 s, typically 30 s. A horizontal 16:9 version for long-form platforms is built by the same rules, with 2.39:1 bars (12.8 % of the height each).
- Music: an orchestral or hybrid trailer track, epic drums, cinematic post-rock. A rise and a drop are required: `drops[0]` from the track analysis (a jump of ≥ 3 dB in loudness and in the low end on a downbeat) or the start of the section with the highest `energy`. Without such a contrast the genre does not come together — suggest another track or the calm genre.
- Neighbors: vs motivation — no voice, picture and music carry everything; vs sport — space and scale matter more than stats, slow motion is held longer; vs teaser — we show rather than hide; vs travel — transitions are almost invisible (a cut on the beat, a fade to black instead of whip transitions), the color is contrasty rather than sunny; vs fan edit and phonk — no digital "breakage", no velocity and no song lyrics.

## Structure by seconds
A typical 30 s video at 120 BPM: beat 0.5 s, bar 2 s, 15 bars in total.

| part | time | bars | on screen | in the music | which shot |
|---|---|---|---|---|---|
| hook | 0–4 s (0–13 %) | 1–2 | picture from the first frame (out of black ≤ 0.3 s); an extreme wide shot or a flyover from above, a slow reveal pull-out; the bars slide in to 4:5; on bar 2 — the title | first downbeat — a low hit; pad, choir, strings | the biggest-scale shot: EWS or an aerial shot, a person ≤ 12 % of the height or no person at all |
| build | 4–16 s (13–53 %) | 3–8 | the hero and the preparation, details in slow motion, low angles, a silhouette at sunset; in bar 7 — dips to black on the hits; bar 8 ends with a black pause of 1–2 beats | drums and strings swell; a riser over the last 2 bars; an "inhale" before the drop | medium shots and close-ups with action; motion in frame grows from quiet to fast |
| drop | 16–26 s (53–87 %) | 9–13 | first beat — the best shot of the video in slow motion for a whole bar, the bars open up; then powerful actions: speed ramps, low angles, an arc around the hero, flashes on the main hits; bar 13 — a single wide shot in slow motion | the main hit and a sub drop on the first beat; full orchestra, percussion on every beat | the best shot of the video, then the top quarter by motion |
| outro | 26–30 s (87–100 %) | 14–15 | pull-out from the hero to the landscape or a drone flying away, the bars close to 1:1, final title, fade to black | the last hit or a long note, the tail | the calmest wide shot: EWS, aerial fly-away, sunset |

Track window: the engine places `drops[0].t` (or the start of the section with the highest `energy`) at 16 s ± 2 s (50–60 % of the length); the video starts on a downbeat 8 bars before the drop; it ends on a downbeat 5–7 bars after the drop, preferably at the end of a musical phrase. If the track has fewer than 6 bars before the drop, compress build (minimum 4 bars), but not hook.

Other lengths (the parts keep their proportions, boundaries fall on bars): ≈16 s (8 bars) — hook 1 bar, build 3, drop 3, outro 1; 60 s (30 bars) — hook 0–8 s, build 8–32 s in two waves (a small rise, a dip and an inhale pause at 18–20 s, then the main build-up), drop 32–52 s (with a "half-time" bar of slow motion inside), outro 52–60 s.

## Rhythm
| part | shot length | cut grid | shots per bar |
|---|---|---|---|
| hook | 2–4 s | once per bar; the first picture on the first downbeat | 0.5–1 |
| build | 2 → 1 → 0.5 s | bars 3–4 — 2 s each; 5–6 — 2 beats each (1 s); 7 — one beat each with dips to black; 8 — 2–3 one-beat shots + 1–2 beats of black pause | 1 → 2 → 4 |
| drop | 0.5–1.5 s; first shot 2 s | first beat — slow motion for a bar; then every 2 beats; on orchestral hits — every beat, no more than 2 bars in a row; a wide shot ≥ 3 beats (1.5 s) | 2–4 |
| outro | 2–4 s | once per bar or one shot per 2 bars; black on the last note | 0.5–1 |

- The cutting pace rises only in build (staircase bar → ½ bar → beat). In the drop the step is even and long (2 beats); splitting down to single beats comes in bursts of 1–2 bars on the hits; half-beats — no more than 4 cuts in a row and only on a drum roll or an orchestral roll in bars 10–12 (the first bar of the drop is taken by a single slow-motion shot).
- Pauses: a black pause of 1–2 beats before the drop (0.5–1 s; 12–25 frames @25 fps, 15–30 @30 fps); in the 60-second version — one more between the build waves. The last bar of the drop is "half-time": one wide shot in slow motion for the whole bar.
- Sync: cuts on the beat ±1 frame; a slow-motion shot starts on a downbeat; the action peak (landing, impact, swing) falls on a beat, and the speed ramp is anchored to it as well.
- Different track tempo: keep the grid in beats and bars, and use the seconds from the table only as a guide; on slow tracks (≤ 80 BPM) a drop shot is 1 beat, on fast ones (≥ 140 BPM) 2 beats, but not shorter than 0.5 s and not longer than 4 s.

## Shot selection
Features come from the source analysis: `scale` (shot size by face: extreme-close / close / medium / wide / wide/no-face), `motion` (motion energy), `sharp` (sharpness), `luma`, `face_share`, `cam` (camera scale, roll and shift), `person` (share of the frame covered by a person), the source frame rate. Thresholds are percentiles P across all of the user's sources, not absolute numbers.

| slot | what goes there | criteria |
|---|---|---|
| hook, shot 1 | the biggest-scale shot of the video | `scale` = wide/no-face or a person ≤ 12 % of the height (`person` ≤ 5 % of the area); horizon in frame, roll ≤ 1°; `sharp` ≥ P60; the camera is static or gliding (shift ≤ 0.5 %/frame, jitter ≤ 0.3 %); backlight, sunset, fog or night with lights (brightness spread P95−P5 ≥ P70) |
| hook, shot 2 | the second establishing shot (aerial or wide with the hero) | wide; a different scale or direction of motion than shot 1 |
| build | hero, preparation, details, silhouettes, low angles | medium / close and details; `motion` grows along the way: bars 3–4 — P30–P60, bars 6–8 — P60–P85; 50/60/100+ fps sources go into the first half of build for slow motion |
| drop, first beat | the best shot of the video | maximum of the score E = 0.40·rank of the `motion` peak + 0.25·rank of `sharp` + 0.20·hero clarity (a person or object 5–40 % of the frame, face or silhouette readable) + 0.15·contrast rank; sources ≥ 50 fps are preferred; the action peak lands on the first beat |
| drop, after that | the most dynamic | `motion` ≥ P75; every cut changes shot size (wide ↔ close) or angle; adjacent shots share one direction of motion (cut.vector_match) |
| outro | the calmest wide shot | wide / wide/no-face, `motion` ≤ P40, a smooth pull-out or fly-away; sunset or blue hour |

- Repeats: each source segment only once; one source shot no more than 2 times (different segments) and not closer than 8 s apart; no more than 2 aerial shots in a row, with a ground-level shot between them; two extreme wide shots in a row only with a different scale or direction.
- Do not use: handheld footage with jitter > 1 % of the frame, selfies and talking to the camera, comedic moments, screens and interfaces, third-party logos, a close-up face mid-speech, sources below 1080p if the crop needs ×1.5 or more.
- Vertical: crop by `track(person)` or by the object, horizon on a third. Put a 16:9 landscape into the 4:5 band — the crop is 1.4 times smaller than for full 9:16 (45 % of the source width visible versus 32 %). If something important gets cut off — Higgsfield `reframe` (with consent).
- No extreme wide shot for the hook: zoom.out from a 4K wide shot (start at ×2) → `outpaint` a simple background ×1.5–2 → offer to generate an extreme wide shot of "a small figure in a huge landscape" (edit-gen, after the price is confirmed).
- No HFR sources: slow motion in code only down to 0.5 (optical flow); for anything deeper, time.freeze with a zoom-in instead of slow motion.

## Moves by part
**hook (0–4 s)**
- trans.fade — opening from black ≤ 8 frames @25 fps / 9 @30 fps, 100 % picture by the first downbeat. Any longer and the viewer scrolls away.
- shot.extreme_wide / drone.aerial — the first shot, 2–4 s; the second establishing shot comes next.
- zoom.out — the reveal: crop ×1.3 (1080p) or ×2 (4K) → ×1.0 over 3–4 s, linear; start on a detail (a figure, a fire, a car), end with the horizon on a third. Not used in the drop — a pull-out kills the hit.
- fx.letterbox — the bars slide in 9:16 → 4:5 (14.8 % of the height each) over 2 s, linear, from the first downbeat; #000000, hard edge without feathering.
- type.title_card — the title on the downbeat of bar 2, held 1.5–2 s, gone before build. If the track opens with vocals — no title.

**build (4–16 s)**
- time.slow_motion — 1–3 shots in the first half of build (where shots are 2 s long): rate 0.5 (from 50 fps — no frame synthesis; from 25/30 — optical flow, not below 0.4); the action peak at 40–70 % of the shot; slow motion ≤ 50 % of build time.
- angle.low — 1–2 shots of the hero against the sky: strength and monumentality.
- light.silhouette — 1 shot of 2–4 s in backlight: figure ≤ 20 of 255, background 100–235.
- zoom.slow — on every static shot ≥ 2 s: ×1.05–1.15 over the shot (no faster than 0.3 %/frame @25 fps), centered on the face or figure.
- cut.vector_match — in bars 5–7: a series of 3–4 cuts in one direction (cosine of the vectors ≥ 0.75, speed B/A 0.65–1.5), then a landing.
- trans.fade — (1) the trailer pulse in bar 7: 2–4 dips on downbeats (fade out 2–4 frames, black 1–3 frames, fade in 4–6 frames) on the hits; (2) a black pause of 1–2 beats before the drop, exit with a hard cut on the first beat of the drop.

**drop (16–26 s)**
- First beat: out of black — the best shot in time.slow_motion 0.4–0.5 for a whole bar + a white trans.flash, peak 2 frames, τ 60 ms + a heavy shake.beat (4–5 % of the short side, τ 0.11 s, rotation 1–2°). This is the only beat in the video with three accents. The bars open 4:5 → 9:16 over 1.5 s — "the world expands". Option B: the bars stay until the end of the video if the drop has many 16:9 landscapes.
- time.speed_ramp — on key actions, ≤ 1 per bar: fast ×2–2.5 → slow 0.3–0.4 (0.25 only from 50+ fps), deceleration over 4–6 frames inOutCubic, slow-motion hold 0.5–0.8 s, slow motion starts on the beat.
- angle.low, arc.horizontal — the hero from below and an arc of 60–120° over 1–2 s, the "hero entrance"; arcs — 1–2 per video.
- trans.flash — after the first beat only 1 frame on the main orchestral hits: ≤ 3 per 10 s and ≤ 25 % of the drop's cuts; if both shots are bright (brightness > 180) — a black hit instead of white.
- shake.beat — impact 1.5–2.5 % on the main hits, ≤ 1 per bar, no more than 2 bars in a row; not on slow-motion landscapes and not under text.
- cut.vector_match — links adjacent actions by one direction: series of 3–4 cuts, ≥ 1 bar between series.

**outro (26–30 s)**
- zoom.out / drone.aerial — fly-away: scale 1.6 → 1.0 over 3 s, outCubic (for a real drone — ×0.6–0.9 per second).
- shot.extreme_wide — if there is no fly-away: a static EWS with a slow zoom-out of ×1.05 over the shot.
- fx.letterbox — the bars close 9:16 → 1:1 (21.9 % of the height each) over 2 s.
- type.title_card — the end card, 2–3 s, inside the picture band.
- trans.fade — to black over 1–1.5 s on the last note, black is held 0.5 s; the music fades out with the picture to −60 dB.

**Limits**
| move | limit |
|---|---|
| trans.flash | ≤ 3 per 10 s and ≤ 25 % of the drop's cuts; 0 in hook and outro |
| shake.beat | heavy — 1 per video (first beat of the drop); impact ≤ 3 per 10 s and ≤ 1 per bar |
| time.speed_ramp | ≤ 2 per 10 s, ≤ 1 per bar, only on a shot with an action peak |
| time.slow_motion | ≤ 50 % of the running time; no more than 2 slow-motion shots of the same shot size in a row |
| trans.fade | dips — up to 4 in a row only in the trailer pulse, otherwise ≤ 1 per 4 bars; 0 in the drop |
| fx.letterbox | ≤ 3 aspect changes per video (hook, drop, outro) |
| zoom.slow / zoom.out | only on static shots ≥ 2 s; not both on the same shot |

**Forbidden and why**
- zoom.in_out — a "pulsing" frame: the language of viral and phonk, breaks the grandeur.
- time.velocity — a speed pulse on every beat: the language of phonk and fan edits; epic holds long slow motion, a ramp only on a key action.
- time.boomerang — a comedic "rubber band".
- fx.glitch, fx.rgb_split, glitch.pixel_sort — digital breakage of the picture destroys the "movie" feel; in epic the accent on a hit is a flash and a shake.
- trans.iris, trans.page — graphic wipes from a video editing app, read as cheap and childish.
- look.cheesy, fx.bobblehead — irony and comedy.

Not forbidden, but not used by default: zoom.crash and zoom.punch (they chop up the scale — speed_ramp and the flash take over their role), cut.flash and cut.stutter (fan-edit energy), trans.whip and trans.zoom (travel transitions; in epic we change location with a cut on the beat, a fade to black or cut.vector_match).

**Signature moves from the cards.** The cards mark 16 signature moves for epic. The genre signature has five: fx.letterbox, time.slow_motion, shot.extreme_wide, zoom.out, trans.fade. drone.aerial, angle.low, arc.horizontal are in the parts but not in the signature: they are special source shots, and the video must come together without them. shot.wide, angle.birds_eye, zoom.extreme, scene.giant, time.bullet_time are in allowed: appropriate, but they require a special shot or a generation, so they cannot be mandatory. sfx.impact, sfx.riser, sfx.sub_drop are the genre's signature sound and sit in the `sfx` field.

## SFX
| part | sound | sync point | level vs music | limit |
|---|---|---|---|---|
| hook | sfx.impact, "boom" variant | attack on the first downbeat (first frame or the title) | −2 LU (−4…0) | 1; skip it if the track itself opens with a hit (onset ≥ P90 within ±50 ms) |
| build | sfx.impact, "punch" (not "boom" — the video has only two main hits) | the black frame in the dips of the trailer pulse | −6 LU | ≤ 3 per 10 s |
| build | sfx.riser | the last 2 bars, end = first beat of the drop with a 1/16 gap (125 ms) | −6 LU in the last 400 ms | 1; only if the track does not build up by itself (loudness rise over 2 bars < 3 dB) |
| drop | sfx.sub_drop + sfx.impact "boom" | attack on the first beat of the drop, sample-accurate | each 3 dB below its normal level: sub −9 LU, boom −5 LU | 1 pair |
| outro | sfx.impact, "stretched boom" or "stop" | the final title or the last note | −4…−6 LU | 1 |

- Ducking: under the boom the music goes −3…−6 dB in the 30–150 Hz band (attack 2 ms, release 400 ms); under the sub drop −4…−8 dB in 25–150 Hz; in the last quarter of the riser — music −3 dB in 2–10 kHz.
- Per 30 s video: main booms ≤ 2 and not closer than 15 s to each other (hook and drop), 1 sub drop, 1 riser, ≤ 6 hits in total; the limiter does not compress more than 3 dB.
- Whoosh — only under real fast camera movement (a drone dive, a whipping arc), ≤ 1 per 10 s, −6 LU. No glitch sounds.
- Ambience from the sources (wind, surf, crowd) — only in hook and outro, −18…−24 LU under the music.

## Color
Direction: a contrasty "cinema" look — cool shadows, warm highlights, deep but living blacks.

| parameter | value |
|---|---|
| contrast | S-curve +15…+25 % (0.25 → 0.21, 0.75 → 0.80); brightness spread P95 − P5 ≥ 0.70 |
| black point | P1 = 4–10 of 255; no more than 2 % of the area at 0–2 |
| white point | P99 = 235–248, soft shoulder; ≥ 250 — no more than 0.5 % of the area (except the sun in frame) |
| saturation | overall ×0.95–1.05, vibrance +10 %; sky and greenery ≤ ×1.10; skin — hue 18–28°, saturation ≤ 0.5 |
| balance | split toning: shadows hue 190–200° (teal), strength 8–12 %; highlights 30–40° (amber), 6–10 %; overall temperature neutral, on sunset shots +200…+300 K |
| vignette | 15–25 % toward the edges |
| grain | fx.film_overlay level 1 over the whole video if the sources are mixed (phone, drone, camera) |
| bars | pure #000000 |

- Adjacent shots of the same location: mean brightness difference ≤ 15 %, ΔE of the mean colors ≤ 6.
- Look on request: look.dystopian — a cold, almost colorless picture with one warm accent (fire, signal smoke) for themes of disaster and struggle; B&W variant — saturation 0, contrast +25 %, grain level 2.

## Text
- Little text: a title in the hook (or nothing), an end card in the outro; in build — at most one single-line card (type.intertitle) on a dip to black; no text in the drop.
- Typeface: a wide, letter-spaced sans-serif or Roman capitals in uppercase; one typeface per video, no more than 2 styles.
- Size (9:16, H = 1920 px): the title line ≤ 76 % of the width (≤ 820 px — the right 12 % is taken by the interface) — this is the main constraint; cap height 4–6 % H (77–115 px) for words of up to 6 letters, smaller for longer ones but not below 3 % H, otherwise break into 2 lines; letter spacing 25–40 % of the font size; subheading (place, year) 2.2–2.8 % H (anything smaller is unreadable on a phone); the single-line card in build 3.5–4.5 % H.
- Position: block center x 0.47–0.50, y 0.42–0.48 — inside the 4:5 band (y 0.148–0.852) and always within the safe zone y 0.12–0.80, x 0.06–0.88. No text on the letterbox bars — they coincide with the interface zones. Do not cover the face (by the face mask).
- Color: white or cream #F2EDE4 without an outline; on a bright sky — a shadow of 1–2 % H with 40 % transparency or darkening under the block by 20–30 %; contrast ≥ 4.5:1.
- Animation: in — fade 0.5–0.75 s (outQuad) or blur-in 1.4 s; while on screen, letter spacing slowly grows by 5–10 %; out — dissolve 0.6–0.9 s or together with the shot. No bounces, springs or per-letter effects.
- Sync: enters on a downbeat, fully visible by the next beat; reading time ≥ 0.3 s per word + 0.5 s; title 1.5–3 s; the end card 2–3 s, leaving with the fade to black.
- Subtitles only if the sources contain speech or a voice-over: type.subtitles 3.5–4.5 % H, block at y 0.62–0.78.

## Quality checks
1. Grid: share of cuts on a beat or half-beat (±1 frame) ≥ 0.90; the first cut of the drop on `drops[0].t` ±1 frame; slow-motion starts and ramp peaks on beats ±1 frame.
2. Shot lengths: per-part medians within `shot_len_s` (±20 %); no shot longer than 4 s; in the drop, no more than 4 shots shorter than 0.5 s in a row; EWS and aerial ≥ 1.5 s.
3. Best shot: the first shot of the drop is top-1 by score E among the selected shots; the first shot of the hook has `scale` wide/no-face or a person ≤ 12 % of the height.
4. Loudness: −14 ±1 LUFS integrated; true peak ≤ −1.0 dBTP; short-term loudness (3 s window) in the first 4 s of the drop ≥ the build median + 3 LU.
5. Black (blackdetect d = 0.06 s, threshold 0.08): only the planned ones — the opening ≤ 0.3 s, the pulse dips, the pause before the drop 0.5–1 s, the final fade to black; not a single black frame inside the drop.
6. Frozen frames (freezedetect ≥ 0.5 s): only planned time.freeze and the end card.
7. Slow motion: from 25/30 fps rate ≥ 0.4; slow-motion share ≤ 50 % of the video; no duplicated adjacent frames in slow-motion segments.
8. Effects: flashes ≤ 3 per 10 s and ≤ 25 % of the drop's cuts; brightness changes > 10 % over > 25 % of the area — no more than 3 per second; heavy shake — 1; impact shake ≤ 1 per bar; bar aspect changes ≤ 3.
9. Bars: outside the three animations the height is constant (±1 px); the animation is linear, 0.05–0.12 of the frame height per second, without jerks; the bars are pure black (0–2 of 255); faces and text stay inside the open part of the frame.
10. Text: all blocks within y 0.12–0.80 and x 0.06–0.88; contrast ≥ 4.5:1; on screen ≥ 0.3 s/word + 0.5 s; no text in the drop.
11. Color: P1 4–10, P99 235–248; mean saturation within ±10 % of the target; horizon on EWS and aerial shots — roll ≤ 1°.
12. Repeats and faces: no source segment repeats; faces are not cut off by the crop (`face_issues` = 0).
