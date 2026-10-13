---
genre: viral
slug: viral
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [7, 30], typical_s: 16}
structure:
  - {part: hook,  t: "0–2 s (0–12 %)",   goal: "stop the scroll within 0.5 s: the strongest shot, motion and the text promise right away, no warm-up"}
  - {part: build, t: "2–6 s (12–38 %)",  goal: "don't let them leave: a new event every 0.5–1 s, accelerating into the drop"}
  - {part: drop,  t: "6–14 s (38–88 %)", goal: "deliver the promise: the best shot on the first beat of the drop, the densest cutting and the trending moves"}
  - {part: outro, t: "14–16 s (88–100 %)", goal: "the end goes unnoticed: the last frame flows into the first, the video plays a second time around"}
rhythm:
  shot_len_s: {hook: [0.5, 1.0], build: [0.5, 1.0], drop: [0.25, 1.0], outro: [0.75, 2.0]}
  cut_grid: {hook: "punch-in on beat 2 (0.5 s), the first cut on beat 3 (1.0 s), then every beat; or cut.jump jumps on every beat from 0.5 s", build: "every 1–2 beats, motion transitions on the snare; the last 2 beats in 1/8", drop: "a cut on every beat or a 2-beat shot with a punch-in on the second; a 1/8 burst no longer than 1 bar and no more often than once per 2 bars", outro: "1–2 beats per shot, the loop seam exactly on a bar boundary"}
  on_beat_share: 0.9
  max_shot_s: 2.0
moves:
  hook:  [zoom.punch, address.direct, type.kinetic, cut.jump, zoom.crash]
  build: [cut.quick, trans.whip, zoom.in_out, time.speed_ramp, cut.match, time.boomerang]
  drop:  [zoom.punch, cut.quick, trans.zoom, trans.whip, time.speed_ramp, time.freeze, shake.beat]
  outro: [loop.end, time.boomerang, zoom.punch, cut.match]
  signature: [cut.quick, zoom.punch, trans.whip, time.speed_ramp, loop.end]
  allowed: [dolly.crash, address.aside, address.lens_touch, pov.dialogue, cut.dance, lens.ultra_wide, trans.portal, trans.metamorphosis, time.fast_motion, fx.living_object, fx.talking_animal, fx.bobblehead, anim.doodle_overlay, mask.bg_replace, scene.forced_perspective, look.cheesy, look.vhs, trans.flash, fx.rgb_split, time.velocity, cut.flash, cut.stutter, light.flash, fx.glitch, type.subtitles, type.beat_text]
  forbidden: [trans.fade, type.credits, trans.dissolve, trans.double_exposure, fx.letterbox]
sfx: {hook: [sfx.impact, sfx.whoosh], build: [sfx.whoosh, sfx.riser], drop: [sfx.impact, sfx.whoosh, sfx.sub_drop], outro: []}
looks: [look.vhs, look.cheesy]
---

# Viral

## Goal and platform
A short vertical edit to a trending track for short-video feeds: 9:16, 7–30 s, typically 16 s = 8 bars at 120 BPM.
There is one goal — retention and rewatch: the viewer stops in the first 0.5–1 s, watches to the end and does not
notice that the video has started over. Target numbers: completion rate ≥ 70 %, not a single "dead" window longer than
1.5 s, a seamless loop. Any material works — people, places, a process, humor, animals; the video is also watched
without sound, so the hook must read through the picture and the text. How it differs from the neighbors: phonk —
aggression, bass, velocity and a dark grade; fan edit — a hero from a film or anime and sync with the song lyrics;
clips — cut by spoken words; viral — a universal fast edit built on trending moves, always with a hook in the first
second and a looping ending, bright and "juicy" in color.

## Structure by seconds
Parts are counted in bars of the track; the seconds are for 120 BPM (beat 0.5 s = 15 frames @30 fps / 12.5 @25 fps,
bar 2 s).

| part | time (16 s) | bars | on screen | in the music |
|---|---|---|---|---|
| hook | 0–2 s (0–12 %) | 1 | frame 0 is the most "scroll-stopping" shot (a face to camera or a motion peak), the promise caption from frames 0–3, a punch-in on beat 2 (0.5 s), the first cut on beat 3 (1.0 s) | the track starts on a downbeat, attack within the first 0.1 s — no intro and no fade |
| build | 2–6 s (12–38 %) | 2 | 2–3 shots per bar, one trending transition per bar (whip, zoom in and back, speed ramp), in the last 2 beats — a 1/8 burst into the drop | verse or build-up; if the track has no build-up of its own — a short riser of 2–4 beats |
| drop | 6–14 s (38–88 %) | 4 | the best shot of the video on the first beat of the drop (2 beats), then an event on every beat — a cut or a punch-in, 1/8 bursts, a speed ramp on strong action, one punchline freeze frame | chorus or drop — the densest part of the track |
| outro | 14–16 s (88–100 %) | 1 | the density drops to 1–2 shots, the last shot leads into the first frame, the hook caption returns to its place | the track is cut at a bar boundary with no fade-out; the next bar sounds like the first one |

Other lengths: the hook is always 1 bar, the outro 1 bar (2 bars at 25+ s); the build runs up to the drop of the track
(0.5–2 bars in 7–10 s videos); in 25–30 s videos the drop splits into two waves of 4 bars with a 1-bar "breath" (a
shot of 1–1.5 beats, no effects). Track window: start on a downbeat no earlier than 1 bar before the chorus or drop
(ed_audio drops[], otherwise the first section with label 'high'), the length is a whole number of bars; the end is
chosen so that the bar after the window resembles the first bar of the window (|Δ rms_db| ≤ 2 dB, |Δ low_db| ≤ 3 dB
over bars) — then the loop sounds continuous.

## Rhythm
- Shot lengths: hook 0.5–1.0 s; build 0.5–1.0 s (1–2 beats); drop 0.25–1.0 s (½–2 beats), bursts — 0.25 s (1/8); outro
  0.75–2.0 s. Average shot over the video 0.45–0.65 s → 25–35 cuts per 16 s.
- Grid: hook — a shot from frame 0, a punch-in on beat 2, the first cut on beat 3, then every beat (variant — cut.jump
  jumps on every beat from 0.5 s, with the punch-in across the cut); build — every 1–2 beats, the seams of motion
  transitions on the snare (beats 2 and 4), the last bar accelerates from 1 → ½ beat, the last 2 beats are 4 pieces of
  1/8; drop — an event on every beat: blocks of "a cut on every beat" (downbeat accents — a shake or a flash)
  alternate with blocks of "a 2-beat shot, cuts on kick 1 and 3, punch-ins on snare 2 and 4"; a cut.quick burst in 1/8
  no longer than 1 bar and no more often than once per 2 bars, after the burst a landing on a shot of 1–1.5 beats;
  outro — 1–2 beats per shot, the loop seam exactly on a bar boundary.
- A punch-in and a cut never sit on the same beat: a new shot has no "before" at ×1.0, so a punch-in on its first
  frame reads as a glitch (exception — a punch-in across a cut within the same source shot, cut.jump).
- Share of cuts on the grid (a beat or a half-beat ±1 frame) ≥ 0.9; all the seams of whip and zoom transitions on a
  beat.
- Pace curve: hook ≈1–1.5 cuts/s plus a punch-in and text → build 1–2/s → drop ≈2/s and an event on every beat, spikes
  up to 4/s for 1 bar → outro ≤ 1/s.
- Dead window: no stretch longer than 1.5 s without a visual event (a cut, a punch-in, a speed ramp, a text entry);
  exception — one 0.5–1 s punchline freeze frame.
- Pause: no more than one per video — a "hit-stop" in the drop (the music muted for 1 beat, the picture frozen); in
  the hook and the outro the music is never interrupted.
- Other tempos: at 130+ BPM, in the build and the drop cut on every other beat, 1/8 bursts only on the 2 beats before
  a downbeat; at 85–95 BPM — cuts on half-beats in the drop (a shot ≈0.32 s).

## Shot selection
The engine takes candidate windows from ed_analyze source and ranks the features within the source footage (rank 0–1).
1. Rejection: luma < 35 or > 225 (except intended silhouettes); sharp_rank < 0.25 on the beat frame (blur is
   acceptable only mid-motion); a face cut by the 9:16 crop (face center outside x 0.15–0.85); a shaky handheld camera
   (jitter > 3 %) — only after stabilize; shots with third-party logos and burned-in text in the zone y 0.12–0.80.
2. Hook (slots 1–2): score = 0.4·motion_rank + 0.3·face + 0.3·sharp_rank, where face = 1 when face_h ≥ 0.18 and
   looking into the camera (face center x 0.4–0.6). The motion peak of the window (motion_peak_t) falls within the
   first 0.5 s: something happens right away. Frame 0 is not a transition, not black, not blurred. If there is a shot
   addressing the lens, it goes first.
3. Build: medium shots and close-ups (face_h 0.08–0.33), motion_rank 0.4–0.8; adjacent slots differ in shot size by at
   least one class (wide → close-up); for a whip transition the shots on both sides of the seam move in the same
   direction (the sign of cam.tx matches).
4. Drop: on the first beat — the best shot of the video (0.5·motion_rank + 0.3·sharp_rank + 0.2·face); after that
   motion_rank ≥ 0.7; the motion peak is placed on the beat ±1 frame, the cut 0.14–0.28 s after the peak. For a speed
   ramp — a shot with one pronounced peak (motion at the peak ≥ 2× the window median), preferably a 50–60 fps source.
5. Outro: the last shot continues the same source shot as the first one (src_in 0.5–1.5 s before frame 0), or a frame
   from the last 1.5 s with the minimum difference to frame 0 (loop_close, threshold ≤ 1.6× the median of neighboring
   differences).
6. Repeats: one source shot ≤ 2 times (≤ 3 in videos > 20 s), never in adjacent slots, the ranges do not overlap (gap
   ≥ 0.5 s); exception — the hook shot in the outro for the loop. Any 4 s window has at least 3 different source
   shots; no more than 3 close-up faces in a row.
7. 9:16: reframe on a face or a person; the total crop (reframe × punch-in × shake margin) ≤ ×2.2 of the source. No
   faces in the source — the hook relies on motion, text and zoom.punch.

## Moves by part
**Hook.** zoom.punch ×1.25–1.3 hold on beat 2 (0.5 s, frame k0 = floor(t·fps + 0.4)): the shot needs ≥ 0.3 s at ×1.0
before the hit, so no punch-in on frame 0; it holds until the cut on beat 3. address.direct — a look or a gesture into
the lens in the first 0–1 s, if such a shot exists. type.kinetic — a promise caption of 1–5 words from frames 0–3,
held for the whole hook. cut.jump — if the hook comes from a single take: 2–4 jumps of 6–10 frames @25 fps with a
×1.15–1.25 punch-in across the cut. zoom.crash ×3–5 in 0.4 s — only on a reaction or a punchline, no more than one per
video.
**Build.** cut.quick — bursts of 4–6 pieces (1/8–¼, 0.25–0.5 s), the last one accelerates into the drop. trans.whip —
window 5 frames @25 fps / 6 @30 fps, the seam on the snare, no more than 4 in a row. zoom.in_out — a ×1.3 pair (zoom
in on the beat, back on the off-beat), ≤ 2 cycles in a row. time.speed_ramp — speed up ×2.5, slow down to 0.3 at the
action peak on the downbeat frame, 1 ramp per 4–8 bars. cut.match — a pose or shape rhyme on a change of place, a run
of 2–4 cuts. time.boomerang — once, cycle = 1 beat, 2 cycles (a swing, a gesture, a jump).
**Drop.** zoom.punch bounce ×1.12–1.2 on beats without a cut (in the "2-beat shot" blocks — on the snare), a run no
longer than 2–4 bars, then a bar without punch-ins; on the first beat of the drop the best shot holds for 2 beats with
a ×1.25–1.3 punch-in on the second. cut.quick in 1/8 — 1 bar, a landing of 1–1.5 beats. trans.zoom — the seam on the
first beat of the drop (×2–3 in 0.3 s, exit ×1.3 → 1 over 6–8 frames). trans.whip — a change of place on the snare.
time.speed_ramp — slow down on the hit. time.freeze 0.5–1 s with a word — once (the punchline), together with the
"hit-stop". shake.beat impact 1.5–2.5 % on downbeats for no longer than 2 bars.
**Outro.** loop.end — mandatory: video length = a whole number of bars, audio without a fade, a 30 ms crossfade at the
seam, no fades to black and no titles. time.boomerang — if the final gesture can return to the pose of frame 0.
zoom.punch — a reverse punch ×1.2 → ×1.0 on the last downbeat, if frame 0 is at ×1.0. cut.match — the last shot
matches the first one in shape and in the position of the main subject (±5 % of the frame).
**Limits per 10 s:** punch-ins ≤ 10 (outside the drop ≤ 1 per bar), whips ≤ 4 (a run of up to 5, no more than 1 per
beat), trans.zoom ≤ 2, speed ramps ≤ 2, RGB ≤ 4, flashes ≤ 3 per second and on ≤ 40 % of cuts, heavy shake ≤ 1 per 4
bars; zoom.crash and the freeze frame — one each per video. On one beat ≤ 2 accents from {punch-in, shake, flash,
RGB}, on the first beat of the drop — up to 3.
**Genre signature:** cut.quick, zoom.punch, trans.whip, time.speed_ramp and loop.end — every viral video has at least
4 of the 5, and loop.end always.
**Allowed** — depending on the material or on the user's request: trending content techniques (dolly.crash,
address.aside, address.lens_touch, pov.dialogue, cut.dance, lens.ultra_wide, trans.portal, trans.metamorphosis —
generation only with consent, time.fast_motion, fx.living_object, fx.talking_animal, fx.bobblehead,
anim.doodle_overlay, mask.bg_replace, scene.forced_perspective, look.cheesy) and editing accents (trans.flash,
fx.rgb_split, time.velocity, cut.flash, cut.stutter, light.flash, fx.glitch, type.beat_text; type.subtitles — if the
video has speech). The move cards mark many content techniques as signature for viral — here they are allowed, not
required: they need a special shot or an idea, so we do not place them automatically. sfx.whoosh — the sound that
accompanies transitions, lives in the SFX section.
**Forbidden:** trans.fade — a fade to black breaks the loop and eats the hook; type.credits — end credits break the
loop and signal "the end"; trans.dissolve — 0.6–2.6 s of a soft dissolve = a dead window; trans.double_exposure —
1–5 s of superimposition turns into mush on a phone in a fast video; fx.letterbox — in 9:16 the bars eat 25–60 % of
the screen, and sliding them in costs a second.

## SFX
- Hook: sfx.impact (punch, −6 LU, align='attack' on the punch-in frame) — only if the track starts without a strong
  kick; sfx.whoosh (air, −6 LU, peak on the seam) under the first whip or crash zoom.
- Build: sfx.whoosh on every transition with real motion (SHIFT ≥ 8 %/frame, ZOOM ≥ ×1.1/frame), ≤ 3 per 10 s; a run
  of whip transitions — up to 5 per 10 s and no closer than 0.5 s apart; sfx.riser 2–4 beats before the drop — only if
  the track has no build-up of its own (the riser ends on the attack of the first beat of the drop).
- Drop: sfx.impact on the first beat of the drop — punch −6 LU, boom −2 LU only after a pause before the drop;
  sfx.sub_drop — only together with the pause, both 3 dB below their normal levels; sfx.whoosh on trans.zoom and
  whips. If the track already has a powerful kick on that beat (low_flux in the top 2 %) — only the click and the
  crackle of the impact remain, through a 150 Hz high-pass filter.
- Outro: no sounds at the loop seam — any hit gives away the restart; the music is continuous, crossfade 20–50 ms.
- Under an impact the music is lowered by −3…−6 dB in the 30–150 Hz band (attack 2 ms, release 200 ms). In total ≤ 6
  sounds per 16 s, each with a new seed. The source audio is muted; exception — a 0.5–1.5 s hook line, with the music
  −8 dB under it.

## Color
- Direction: bright, vivid, natural skin, all shots brought to one exposure.
- Engine: grade={preset:'color', auto:0.6, contrast:1.12, sat:1.15, temp:0.04, black:0.02, gain:0.98}.
- Contrast ×1.10–1.15; saturation ×1.10–1.20, skin (hue 15–35° by the face mask) no higher than ×1.05; warm balance:
  temp +0.03…+0.06 (≈ +100–200 K), tint 0; black point: black 0.02 (everything below ≈5/255 goes to 0); white point:
  gain 0.98 (≈250/255), faces no higher than 235/255. Night shots: sat ×1.0, black 0.03.
- The median brightness of adjacent shots differs by ≤ 25/255, except for an intended contrast on the cut into the
  drop.
- Looks: look.vhs (a retro trend) or look.cheesy (ironic content) — only on the whole video, not in pieces.

## Text
- Hook caption: 1–5 words, ≤ 30 characters, appears on frames 0–3 and holds for the whole hook (≥ 1.2 s, +0.3 s for
  every word beyond three). Class: a wide or condensed extra-bold sans-serif 800–900, covering the caption language, an
  OFL-licensed font.
- Size: the caption line 5–7 % H (96–134 px at 1920), a single word up to 80 % W (≈10–14 % H). Position: y 0.14–0.30
  (above the face) or y 0.62–0.78; x 0.06–0.88 — the top 12 %, the bottom 20 % and the right 12 % of the frame are
  taken by the interface.
- Color: white with an outline of 4–6 % of the font size or on a #000 plate at 55 %; one accent word #FFE600; contrast
  ≥ 4.5:1.
- Animation: a "pop" ×0.9 → 1.0 over 4 frames (outCubic) or a straight appearance; no letter-by-letter animation in
  the hook.
- Drop: no text, except one word on the freeze frame (type.kinetic, 10–14 % H).
- Outro: the hook caption returns in the same position and size for the last 0.5–1 s — the loop does not blink with
  text.
- Speech in the video: type.subtitles 3.5–4.5 % H, block at y 0.62–0.78, ≤ 2 lines of 26 characters.
- Text is composited after the punch-ins and the shake (it does not scale or shake with the picture); ≤ 2 text layers
  on screen.

## Quality checks
- Hook: the first cut ≤ 1.0 s, the first visual event ≤ 0.5 s; frame 0 — sharp ≥ the video median, luma 40–220, not
  black; the caption is visible from frame ≤ 3.
- Grid: cuts_on_grid_share ≥ 0.90 (beats and half-beats, ±1 frame); the punch-in peak on the beat frame −1…0, the
  shake peak 0…+1.
- Pace: average shot 0.45–0.65 s; max_shot ≤ 2.0 s (freeze frame ≤ 1.0 s); no window > 1.5 s without an event on the
  timeline.
- Loop: length = a whole number of bars ±1 frame; the last → first frame difference (grayscale, 160 px) ≤ 1.6× the
  median of neighboring differences; the music RMS in the last and the first 100 ms differs by ≤ 3 dB; over the last
  0.5 s the loudness does not drop by more than 3 dB (no fade).
- Loudness: −14 LUFS ±1 (integrated), true peak ≤ −1.0 dBTP, master limiter gain reduction on the sounds ≤ 3 dB.
- Black frames (blackdetect d=0.06, pix_th=0.08) — only the intended 1–2 frame "black hits"; frozen ≥ 0.5 s
  (freezedetect) — only the planned freeze frame.
- Limits per 10 s on the timeline: punch-ins ≤ 10, whips ≤ 5, trans.zoom ≤ 2, speed ramps ≤ 2, RGB ≤ 4; ≤ 2 accents
  per beat (≤ 3 on the first beat of the drop); no punch-in sits on the first frame after a cut to a new source shot.
- Flashes: ≤ 3 per second with a brightness change > 10 % over > 25 % of the frame; no red flashes in series.
- Text: entirely within y 0.12–0.80 and x 0.06–0.88, contrast ≥ 4.5:1, a word on screen ≥ 6 frames @25 fps / 8
  @30 fps, not on a face.
- Crop ≤ ×2.2, face_issues = 0; source ranges do not repeat (except for the loop), one shot ≤ 2 times.
