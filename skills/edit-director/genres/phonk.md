---
genre: phonk
slug: phonk
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [10, 40], typical_s: 20}
structure:
  - {part: hook,  t: "0–2 s (0–10 %)",   goal: "feel threat and weight: a dark shot and one heavy hit on the first beat"}
  - {part: build, t: "2–8 s (10–40 %)",  goal: "rising tension: a tilted horizon, slow movement, small jabs on the snare, waiting for the bass"}
  - {part: drop,  t: "8–18 s (40–90 %)", goal: "every kick and 808 is visible on screen: speed, shake, flashes and RGB exactly on the beat"}
  - {part: outro, t: "18–20 s (90–100 %)", goal: "a hard full stop: a freeze on the last hit and silence, no soft fade-out"}
rhythm:
  shot_len_s: {hook: [1.0, 2.0], build: [0.5, 1.0], drop: [0.25, 1.5], outro: [1.0, 2.0]}
  cut_grid: {hook: "one shot per bar or a cut on beat 3; the hit on beat 1", build: "every 2 beats; last bar — every beat, the last 2 beats — a 1/16 stutter or a 1/4 staircase", drop: "only on the beats where velocity speed is at its minimum: no more often than every beat (clip 1–3 beats), at 140+ BPM no more often than every other beat; a 1/8 burst no longer than 1 bar", outro: "1 shot per 1–2 beats, the freeze on the last downbeat"}
  on_beat_share: 0.95
  max_shot_s: 2.5
moves:
  hook:  [zoom.punch, shake.beat, trans.flash, fx.rgb_split, angle.low, angle.dutch]
  build: [angle.dutch, zoom.in_out, fx.rgb_split, cut.stutter, time.speed_ramp, zoom.punch]
  drop:  [time.velocity, shake.beat, trans.flash, fx.rgb_split, zoom.punch, cut.quick, zoom.crash, fx.glitch]
  outro: [time.speed_ramp, time.freeze, shake.beat, fx.rgb_split]
  signature: [time.velocity, shake.beat, trans.flash, fx.rgb_split, zoom.punch]
  allowed: [time.slow_motion, light.flash, fx.glow, fx.color_shift, glitch.datamosh, glitch.vhs, look.dystopian, look.vhs, lens.vignette, light.silhouette, rig.locked_on, roll.whip, trans.whip, trans.zoom, trans.spin, trans.lens_distort, time.echo_trail, time.motion_blur, cut.flash, type.beat_text, type.kinetic, drone.fpv, sfx.sub_drop]
  forbidden: [trans.dissolve, trans.double_exposure, fx.light_leak, look.dreamcore, scene.liminal, anim.watercolor, shot.realization, type.karaoke, type.lower_third, gfx.callout]
sfx: {hook: [sfx.impact], build: [sfx.riser, sfx.glitch], drop: [sfx.impact, sfx.whoosh, sfx.glitch], outro: [sfx.impact]}
looks: [look.dystopian, look.vhs]
---

# Phonk

## Goal and platform
An aggressive vertical edit to phonk for short-video feeds: 9:16, 10–40 s, typically 20 s (10 bars at 120 BPM;
real phonk is more often 130–160 BPM — the rules below are given in beats and bars). Material: cars and drifting, martial arts and the gym,
running and stunts, the city at night, a hero in a "mean" persona. The video should press on the viewer: they don't hear the bass, they see it, because
every kick and 808 is played out with a shake, a punch-in, a flash, an RGB split or a speed pulse. Tone: darkness, threat,
cold, one acid or red accent. Differences from neighbors: viral — bright, universal, with a loop;
sport — readable peaks and stats; fan edit — sync with the song lyrics and a glow on the hero; phonk — everything is subordinate to the low end
of the track, velocity and the dark grade, almost no text.

## Structure by seconds
Seconds are for 120 BPM (beat 0.5 s = 15 frames @30 fps / 12.5 @25 fps, bar 2 s); at another tempo the parts keep their bars.

| part | time (20 s) | bars | on screen | in the music |
|---|---|---|---|---|
| hook | 0–2 s (0–10 %) | 1 | a dark low-angle shot or a silhouette, a stare into the camera or a car in smoke; on the first hit — a combo (heavy shake + flash + RGB; a punch-in if the shot runs ≥ 0.3 s before the hit) | the first hit of the track; if the track starts with a melody without drums — one slow-motion shot with micro RGB on the melody accents, the hit when the kick comes in |
| build | 2–8 s (10–40 %) | 3 | 1 shot per 2 beats, a tilted horizon alternating sides, slow motion or normal speed, jabs on the snare; last bar — a stutter or a punch-in staircase | intro or verse: melody, hats, a sparse kick; at the end — a rise, a fill or an empty beat |
| drop | 8–18 s (40–90 %) | 5 | velocity on every beat, cuts only on beats, shake on the kick, flashes on downbeats, RGB on the snare, one crash zoom | the full beat with 808 — the loudest part |
| outro | 18–20 s (90–100 %) | 1 | a ramp into a stop or a freeze frame on the last hit with a heavy shake and RGB, then a hard cut to black | the last hit, the 808 tail or a hard stop |

Track window: start on a downbeat 2–4 bars before the drop (ed_audio drops[]); if the video is ≤ 12 s — start 1 bar
before the drop. End on the last hit of a phrase; a 0.5–1 s tail on black is allowed.

## Rhythm
- Shot lengths: hook 1–2 s (one shot or two of one bar each); build 0.5–1.0 s; drop 0.25–1.5 s — a clip in velocity lives
  1–3 beats (0.5–1.5 s), 1/8 bursts of 0.25 s each; outro 1–2 s (including the freeze).
- Grid: hook — one shot per bar or a cut on beat 3, the hit on beat 1; build — a cut every 2 beats, in the last
  bar every beat, the last 2 beats — cut.stutter at 1/16 or a punch-in staircase in ¼ steps; drop — cuts only on beats
  (these are the speed minimums of velocity, the sharpest frames), no more often than every beat, at 140+ BPM no more often than every other beat; a cut.quick burst at
  1/8 — no longer than 1 bar; outro — 1 shot per 1–2 beats.
- Share of cuts on the grid ≥ 0.95 — phonk is the most "grid-bound" genre, a cut off the beat is visible immediately.
- Energy curve: build — 1 cut/s and small accents only on the snare; drop — 1–2 cuts/s plus a speed pulse on
  every beat; the second half of the drop may get harsher (velocity quint, a heavy shake every 4 bars); the last beat
  before the drop — empty (a black frame or a freeze), optional.
- Pause: the "inhale" before the drop — 1 beat of black or a freeze frame with no sounds on top; no pauses inside the drop, except
  a "rest" bar for the effects (the bass is carried only by speed or a micro shake).
- Track tempo: 90–140 BPM — a velocity cycle of 1 beat; 140+ BPM — a cycle of 2 beats, impact shake on every other beat; choppy
  velocity at 1/8 — only up to 125 BPM; a cut.quick burst at 1/8 at 140+ BPM — no longer than 2 beats (a piece ≈0.21 s).
  At 150 BPM a beat is 0.4 s = 12 frames @30 fps — flashes on every beat give 2.5 per second, that is the limit.

## Shot selection
1. Tone: low key takes priority — mean luma 25–110, high local contrast, practical lights (headlights, neon,
   welding flashes, sparks). Bright flat daytime shots (luma > 170, low contrast) — only in B&W sections, or
   do not use them.
2. Hook: a silhouette or a low angle (the person mask starts in the top 20 % of the frame, with sky or ceiling above), or
   a close-up face with a still stare into the camera (face_h ≥ 0.25, motion_rank ≤ 0.3), or the hardest action peak.
3. Build: atmospheric medium and wide shots — a night street, smoke, details of the car and the gear (extreme close-ups: a wheel rim, an exhaust,
   a fist, a hand wrap), slow-motion walk-bys; motion_rank 0.2–0.6.
4. Drop: motion_rank ≥ 0.6 and frequent action peaks (action_peaks ≥ 1 per 1–2 s): drifts and car passes, strikes,
   reps in the gym, running, dancing. Faces only in the slow zones on the beats; never a close-up face in the fast part
   (the blur disfigures it). Velocity slow zones come from 50–60 fps sources; 25–30 fps → rate_min 0.4 via optical flow.
5. Outro: the strongest "pose" (the hero facing the camera, a car stopped sideways) with sharp_rank ≥ 0.7 within a ±3-frame window.
6. Repeats: no more than 2 clips in a row with the same action; one source shot ≤ 2 times; ranges do not
   overlap.
7. Crop: 9:16 by the person or the car (object detection). A constant margin for shake: native 9:16 — ×1.05 (impact
   2.5 %) … ×1.15 (heavy 5 % with 1–2° rotation); reframe from 16:9 — ×1.03–1.06 (there is already horizontal margin).
   Digital roll angle.dutch: S = cos θ + 0.56·sin θ when reframing from 16:9 (×1.08 at 10°, ×1.11 at 15°, ×1.13 at 20°)
   and S = cos θ + 1.78·sin θ from native 9:16 (×1.29 / ×1.43 / ×1.55) — do not give a native vertical source a roll above
   12°. Total together with the punch-in ≤ ×2.2, otherwise reduce the amplitude or upscale.

## Moves by part
**Hook.** A combo hit on the first beat that has a hit in the track: shake.beat heavy (A 4–6 %, rotation 1–2°, τ 0.11 s) +
trans.flash, 2 frames of white (on dark footage — a black hit or a 0.8 peak; if the hit is on frame 0 — the shot comes out of white with
τ 60 ms) + fx.rgb_split heavy 14–20 px with a decay of τ 2 frames; zoom.punch ×1.3 hold — on the same hit only if the shot
runs ≥ 0.3 s before it (a cold start on the melody), otherwise on the next downbeat within the same shot: never put a punch-in on frame 0 or on
the first frame after a cut. The hook combo and the first beat of the drop are the only places where 3–4 accents are allowed on one
beat. angle.low — from the sources (a power angle);
angle.dutch — a digital roll of 12–20° (10–12° for native 9:16) with the crop margin from "Shot selection", if the sources have no such angle.
**Build.** angle.dutch — roll 10–20° (native 9:16 — up to 12°), sides alternate from shot to shot, no less than 10°
(less than 8° looks like a camera operator's mistake).
zoom.in_out ×1.3 on the snare, ≤ 2 cycles in a row. fx.rgb_split micro 2–4 px on the snare (beats 2 and 4). time.speed_ramp —
one ramp into the drop: slow motion 0.3 → acceleration to ×3 into the frame of the drop's first beat. Last bar: cut.stutter (3 frames × 8 repeats
@25 fps, in sync with the audio stutter) or a zoom.punch staircase ×1.12 ×3 in ¼ steps with a reset to ×1.0 on the drop beat.
**Drop.** time.velocity — classic (r̄ 2.5, m 0.85, inOutCubic), in the second half it can be hard (quint, m 0.9,
motion blur 270–360°); action peaks on beats ±1 frame; no more than 50 % of the video and 2–3 sections per 30 s. shake.beat impact 2–2.5 %
on the kick/808 of downbeats — a series no longer than 2 bars (8 hits), then a bar of the bass-follow variant (amplitude follows the envelope of
30–150 Hz, 1–2 %) or a change of accent. trans.flash, 1 frame on the downbeat cuts — ≤ 40 % of cuts. fx.rgb_split
8–12 px on the snare (pick one layer — snare or kick, not both), the sign alternates. zoom.punch bounce ×1.15–1.2 —
only on beats inside a clip (velocity clips of 2–3 beats; no punch-in on the beat of a cut), alternating bar by bar with
the shake. First beat of the drop: if build enters the drop as one shot through a ramp — the combo punch-in + heavy shake +
flash + RGB; if there is a cut on the beat — flash + heavy shake + RGB, and the punch-in on the next beat. cut.quick — a burst of
1/8 for 1 bar (strikes, sparks,
faces). zoom.crash ×3–4 over 0.4 s into a face or a detail — one per 8 bars, landing on a downbeat. fx.glitch — bursts of
2–4 frames under the track's fills and rolls, ≤ 1 per 2–4 bars.
**Outro.** time.speed_ramp into a stop → time.freeze 1–2 s on the last hit; on the hit frame shake.beat heavy and
fx.rgb_split 20 px; then a hard cut to black for the 808 tail (≤ 1 s), no fade.
**Limits per 10 s:** impact shake ≤ 1 per beat and series ≤ 2 bars, heavy ≤ 1 per 4 bars; punch-in ≤ 1 per beat,
≤ 16 in a row; RGB ≤ 12 pulses, heavy (from 14 px) ≤ 1 per 2 bars; flashes ≤ 3 per second and ≤ 40 % of cuts,
red ≤ 1 per second; glitch ≤ 1 burst per 2 bars; zoom.crash ≤ 1 per 8 bars; cut.stutter 1–2 per 30 s.
≤ 2 accents per beat out of {punch-in, shake, flash, RGB}; the exceptions are the first beat of the hook and the first beat of the drop.
**Genre signature:** time.velocity, shake.beat, trans.flash, fx.rgb_split, zoom.punch — "shake and flashes on the beat,
ramps, RGB split, reacting to the bass". All the moves that the cards mark as signature for phonk are placed in the parts of the video.
**Allowed:** time.slow_motion (build and a hook without drums), light.flash (strobe in the verse, ≤ 3 Hz), fx.glow (neon
at night, pulsing on the kick), fx.color_shift (red monotone for 1 beat, ≤ 1 per 8 bars), glitch.datamosh and glitch.vhs
(a transition on the drop, retro tape), lens.vignette, light.silhouette, rig.locked_on (the world spins around the hero or
the car on the drop), roll.whip, trans.whip, trans.zoom, trans.spin, trans.lens_distort (≤ 1 trick transition per 8 bars,
not adjacent), time.echo_trail and time.motion_blur (a pass, a strike), cut.flash (entering the drop), type.beat_text and
type.kinetic (one word), drone.fpv, the looks look.dystopian and look.vhs.
**Forbidden:** trans.dissolve and trans.double_exposure — a semi-transparent dissolve smears the hit; fx.light_leak,
look.dreamcore, scene.liminal, anim.watercolor — a warm, pastel, dreamy texture works against threat and cold;
shot.realization — a face at the "it dawned on me" moment shows confusion, while the phonk hero is confident and cold; type.karaoke — phonk vocals are chopped samples, karaoke turns the edit into a lyric video; type.lower_third and
gfx.callout — information plates and arrows break the mood.

## SFX
- The track itself carries all the hits: no separate sounds on every beat, the shake and flashes are the "visible kick".
- Hook: sfx.impact (boom, −4 LU) — only if the video's first hit falls where there is no kick (a cold start on the
  melody); otherwise nothing on top of the track.
- Build: sfx.riser 1–2 bars before the drop — only if the track has no rise of its own (ending on the attack of the drop beat);
  sfx.glitch — a 1/16 stutter of the track under cut.stutter (it replaces the music for 1–2 beats rather than being layered on top).
- Drop: sfx.impact on the first beat of the drop — only the click and crackle through a 150 Hz high-pass at −10 LU: the 808 already occupies
  30–80 Hz; sfx.whoosh (air, −6 LU, peak on the cut) — under zoom.crash and trick transitions with real movement; sfx.glitch
  (burst, −6 LU) — in sync with every fx.glitch.
- Outro: sfx.impact "hit-stop" variant on the last hit — the music switches off until the end of the video (0.5–1 s); or
  a tape stop (sfx.glitch tape_stop) — once per video.
- sfx.sub_drop is not used: phonk's heavy 808 causes beating and limiter "pumping"; the exception is a first beat of the drop
  without an 808 (low_db of the first bar 6+ dB below the drop average).
- Usually 3–5 sounds per 20 s, at most 7 including glitch bursts; master limiter gain reduction ≤ 3 dB.

## Color
- Direction: dark, cold, contrasty, muted; one accent — red or acid (headlights, neon).
- Engine: grade={preset:'teal', contrast:1.35, sat:0.72, temp:-0.12, tint:-0.02, gamma:1.15, black:0.05, gain:0.95}.
- Contrast ×1.30–1.45; saturation ×0.60–0.80; balance cooler by temp −0.10…−0.15 (≈ −350…−500 K) with a slight
  magenta tint (tint −0.02: green channel ×0.995); darker midtones (gamma 1.10–1.20); a hard black point — black 0.04–0.06 (everything below
  10–15/255 goes to 0); whites ≤ 242/255 (gain 0.95). Target mean frame luma 40–90/255.
- Accent: keep the reds at 345–15° following the look.dystopian variant (accent hues ×1.1–1.3 with overall
  desaturation) or a red fx.color_shift monotone on a downbeat.
- B&W variant: preset bw_hi (contrast 1.45, black 0.04) on build or on the whole video; color returns on the drop beat.
- A constant light vignette, lens.vignette (corners ×0.6–0.8). Looks: look.dystopian, look.vhs (tape grain
  on top of the dark grade).

## Text
- No text by default. At most — one "slap" word on the first beat of the drop (type.beat_text: ×1.6 → ×0.97 → ×1.0
  over 3 + 2 frames @25 fps / 4 + 2 @30 fps) or a name or nickname on the final freeze frame (type.kinetic).
- Class: display — blackletter, a "spiky" hand-drawn face, a condensed black-weight sans-serif in uppercase; one typeface per video.
- Size: the slap word up to 84 % W (≈14–22 % H depending on word length); the name on the freeze 8–10 % H.
- Position: center x 0.47, y 0.40–0.55; everything within y 0.12–0.80 and x 0.06–0.88; not over the face.
- Color: white #FFFFFF or red #FF1E3C; for 1–2 frames of the slap — inversion (black on white); if contrast < 4.5:1,
  darken under the word by 35 %.
- The slap word holds 1–2 bars, then 2–4 bars without text; the word has its own shake of 1–1.5 % H decaying over 6 frames
  @25 fps / 7 @30 fps; the frame's overall shake does not affect the text. No subtitles and no karaoke.

## Quality checks
- Grid: cuts_on_grid_share ≥ 0.95; action peaks in velocity sit on beats ±1 frame in ≥ 70 % of cycles; beat frames are
  1.6–3 times sharper than mid-beat frames (blur only between beats).
- Accent sync: shake peak — beat frame 0…+1, punch-in peak −1…0, RGB peak — the beat frame; after each pulse the frame
  returns to scale 1.00 and shift ≤ 0.1 %.
- Accents: ≤ 2 per beat (except the first beat of the hook and of the drop — up to 4); no punch-in on frame 0 or on the first frame after
  a cut; the per-10 s limits from the moves section hold across the timeline.
- Flashes: ≤ 3 per second, gap ≥ 9 frames @25 fps / 10 @30 fps, red ≤ 1 per second.
- Tone: mean luma 40–90/255, p1 ≤ 6/255, p99 ≤ 245/255; mean saturation (HSV S) ≤ 0.35, except accent shots.
- Crop: total ≤ ×2.2; the margin for shake and roll covers the edges — no mirrored or black borders, except on 1–2 frames
  with motion blur.
- Loudness: −14 LUFS ±1, true peak ≤ −1.0 dBTP; sounds have no energy below 100 Hz if an 808 plays on that beat.
- Black frames — only 1–2-frame "black hits", the empty beat before the drop and the closing cut to black ≤ 1 s; frozen
  frames — only intended freeze frames.
- velocity ≤ 50 % of the running time; text within the safe zone y 0.12–0.80, x 0.06–0.88.
