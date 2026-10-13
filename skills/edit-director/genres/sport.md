---
genre: sport
slug: sport
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–4 s (0–13 %)",   goal: "wow from the first second: the best moment of the video as a teaser: a ramp into the contact, a freeze frame with the name and a hit"}
  - {part: build, t: "4–12 s (13–40 %)", goal: "who and where: preparation, faces before the start, the run-up: anticipation of the big moment"}
  - {part: drop,  t: "12–26 s (40–87 %)", goal: "a series of the best plays: every contact on a downbeat, a slowdown at the peak, hits, numbers on freeze frames"}
  - {part: outro, t: "26–30 s (87–100 %)", goal: "emotion and the result: the celebration in slow motion, the final stats, a final freeze with the name"}
rhythm:
  shot_len_s: {hook: [1.5, 4.0], build: [0.5, 2.0], drop: [0.25, 3.0], outro: [1.5, 4.0]}
  cut_grid: {hook: "the contact on the downbeat of bar 1 or 2, the exit from the freeze on a downbeat", build: "every 2 beats (1 s); the prep burst on ¼", drop: "the contact of each play on a downbeat (or beat 3); link shots on every beat or on 1/8 for no longer than 1 bar; a freeze frame starts on the beat frame", outro: "once per bar; the final freeze on the last downbeat"}
  on_beat_share: 0.85
  max_shot_s: 4.0
moves:
  hook:  [time.speed_ramp, time.freeze, type.behind_subject, zoom.crash, time.slow_motion]
  build: [cut.quick, track.subject, time.slow_motion, zoom.punch, trans.whip, type.kinetic]
  drop:  [time.speed_ramp, time.freeze, sfx.impact, gfx.counter, rig.locked_on, cut.quick, shake.beat, zoom.crash]
  outro: [time.slow_motion, gfx.counter, time.freeze, type.kinetic]
  signature: [time.speed_ramp, time.freeze, gfx.counter, sfx.impact, time.slow_motion]
  allowed: [time.super_slow_motion, drone.fpv, rig.mounted, pov.first_person, fx.omni_360, angle.low, shot.close_up, handheld.shaky, trans.flash, trans.zoom, fx.rgb_split, fx.color_shift, time.velocity, time.echo_trail, time.motion_blur, cut.match, cut.stutter, zoom.in_out, light.flash, layout.split_screen, layout.frame_division, type.lower_third, look.vhs]
  forbidden: [trans.dissolve, trans.double_exposure, fx.kaleidoscope, look.drunk, look.dreamcore, scene.liminal, anim.oil_paint, anim.watercolor]
sfx: {hook: [sfx.impact, sfx.whoosh], build: [sfx.whoosh, sfx.riser], drop: [sfx.impact, sfx.sub_drop, sfx.whoosh], outro: [sfx.impact]}
looks: [look.vhs]
---

# Sport

## Goal and platform
A sports highlight for short-video feeds: 9:16, 15–60 s, typically 30 s (15 bars at 120 BPM). The hero is an athlete, a
team, a match or a training session; the audience is fans, the athlete themselves, the club, the school, parents. The
main thing is readability: every play is shown whole, following the "run-up → contact → result" pattern; the action peak
lands on a downbeat, is stretched by a slowdown or stopped by a freeze frame with text, and is underlined with a hit.
Numbers come only from the user's data.
How it differs from neighboring genres: phonk uses motion as raw material for a pulse of speed and does not care about
readability; epic is a slow build-up, letterbox and pathos; motivation is cut to a voiceover; sport is facts, peaks,
numbers and hits, all on the track's grid, but in a way that gives the viewer time to understand what happened.

## Structure by seconds
Seconds are for 120 BPM (beat 0.5 s = 15 frames @30 fps / 12.5 @25 fps, bar 2 s). The building block of the drop is a
"play": a run-up of 1–2 beats, the contact on a downbeat, the result 1–2 beats; with a freeze frame, up to 6 beats.

| part | time (30 s) | bars | on screen | in the music |
|---|---|---|---|---|
| hook | 0–4 s (0–13 %) | 2 | the best moment of the video (a goal, a dunk, a knockdown, a landing): the run-up at ×2, a slowdown to 0.3 into the contact frame on a downbeat, a 0.8–1.5 s freeze with the name behind the athlete | hit-stop: the music goes silent on the freeze and returns on the next downbeat |
| build | 4–12 s (13–40 %) | 4 | preparation (laces, tape, chalk, the ball in hands) as a burst, faces before the start, a tracking shot of the run-up, the walk-out in slow motion; the name and the team in words | verse or rise; at the end, a riser if the track has none |
| drop | 12–26 s (40–87 %) | 7 | 3–5 plays in a row, each with the contact on a downbeat; 1–2 freeze frames with stats; 1/8 link shots of crowd and teammate reactions; the world spins around the ball or the athlete 1–2 times | the drop or chorus: maximum energy |
| outro | 26–30 s (87–100 %) | 2 | the celebration in slow motion (faces, hugs, the stands), the final number lands on the last downbeat, a final freeze with the name | the last phrase of the track, the final hit |

Other lengths: 15 s: hook 1 bar (the freeze with the name only), build 2 bars, drop 3 bars (2–3 plays), outro 1.5 bars;
60 s: two drop waves of 6–8 bars each with a 2-bar build insert between them. Track window: start on a downbeat so that
the track's drop (ed_audio drops[]) falls at 40 % ± 1 bar; the length is a whole number of bars.

## Rhythm
- Lengths: hook 1.5–4 s (one play with a ramp and a freeze, or 2 shots); build 0.5–2 s (preparation on ¼ = 0.5 s,
  tracking shots 1.5–2 s); drop: plays 1–3 s (with a ramp or a freeze), link shots 0.25–0.5 s; outro 1.5–4 s.
- Grid: the timing is set by the contact frame: the engine shifts the clip's in-point so that the contact (a strike, a
  touch of the ball, a landing, crossing the line) lands on the downbeat frame ±1 frame and the ramp's acceleration fits
  into the beats before it. Hook: the contact on beat 3 of the first bar (1.0 s) or on beat 1 of the second (2.0 s):
  the acceleration needs 0.5–1 s before the contact; build: a cut every 2 beats, the prep burst on ¼; drop: contacts on
  downbeats (or on beat 3 if the plays come thick and fast), the exit from a play on the nearest beat after the result,
  1/8 link shots for no longer than 1 bar; outro: once per bar.
- Share of cuts on the grid ≥ 0.85 (some play exits legitimately wait for the result); share of contacts on beats ≥ 0.8.
- Energy curve: hook: a burst and a freeze; build: 1 cut/s, rising to 2/s in the last bar; drop: alternating "a play of
  2–6 beats → 1/8 link shots for 2–4 beats"; outro: 0.5 cuts/s.
- Pauses: a hit-stop on the hook freeze frame and at most one more in the drop (the music off for 0.5–1 beat, back on a
  downbeat).
- Tempo: at 140+ BPM, the contact on the downbeat of every other bar, link shots on beats; at 90–100 BPM, 1/8 link shots
  are allowed for the whole bar.

## Shot selection
1. Finding contacts: action_peaks (the flow minimum after a burst, the acceleration maximum) + transients in the source
   audio (a ball strike, a whistle, a glove hit): the contact frame is where they coincide ±2 frames; objects via object
   detection (person, ball) for anchoring and locking.
2. Scoring a play: a motion peak ≥ 3× the shot median, sharp_rank ≥ 0.6 within ±3 frames of the contact, the athlete
   fully in frame (person mask 5–40 % of the area, the box does not touch the edges), a visible result (0.3–1 s after
   the contact). The best play goes into the hook as a teaser (≤ 1.5 s before the freeze) and in full at the end of the
   drop as the climax, preferably from another angle.
3. Shot size: plays in wide and medium shots (face_h ≤ 0.18, the whole body in frame), emotions before and after in
   close-ups (face_h ≥ 0.18). Do not leave a play before the result has been visible for 0.3–0.5 s.
4. Source speed: slow parts from 50–60 fps (rate 0.5/0.42 without synthesis); from 25–30 fps no slower than 0.4 via
   optical flow; super slow motion only from 120–240 fps per metadata; HFR under artificial light: deflicker.
5. Build: preparation as extreme close-ups of hands and gear (motion_rank 0.3–0.6, one action per piece); faces before
   the start as still close-ups; tracking shots via track.subject with the hero at x 0.4–0.6.
6. Stands and reactions ≤ 20 % of the running time; each play in full only once (+ the teaser in the hook); never show
   the same angle of the same play twice.
7. Broadcast graphics: scoreboards and league and channel logos in the corners (static zones with text) are removed by
   cropping during the reframe or covered with a box; no third-party logos make it into the video.
8. 9:16: reframe on the athlete and the ball (center of interest = the weighted center of the person and the ball), the
   ball no closer than 10 % to the edge; total crop ≤ ×2.2.

## Moves by part
**Hook.** time.speed_ramp: acceleration ×2 from frame 0 (0.5–1 s) → a slowdown over 3–8 frames to 0.3 exactly into the
contact frame on beat 3 of the first bar or on the downbeat of the second. time.freeze 0.8–1.5 s on the contact frame
(the sharpest within ±3 frames), a 2-frame white flash on entry, optionally B&W. type.behind_subject — the surname or the
number behind the athlete on the freeze (a giant word at 30–50 % H, or blocks above and below the head). zoom.crash ×3
into the face after the freeze: optional, no more than one per 8 bars. time.slow_motion ×0.4–0.5 — if the best moment
was shot in HFR and no freeze is needed.
**Build.** cut.quick — the prep routine: 3–6 extreme close-up pieces on ¼ (0.3–0.6 s), landing on the face for 1–1.5 s.
track.subject — the run-up and the walk-out, 1.5–2 s. time.slow_motion — walking out onto the field at ×0.5, 1.5–3 s.
zoom.punch ×1.15–1.25 on a downbeat inside a shot (a 2-beat shot, the punch on the second beat; not on the beat of the
cut), ≤ 1 per bar. trans.whip — a change of venue or angle on the snare. type.kinetic — name, team, event: 1–3 words per
screen, 0.5–1 s per word.
**Drop.** time.speed_ramp — on every play: acceleration ×2–3, slow 0.25–0.4 for 0.5–1 s around the contact, exit at
×1–2. time.freeze 0.5–1.2 s on 1–2 key contacts with a number. gfx.counter — stats on the freeze (the count starts on a
beat, lands on the next downbeat, holds ≥ 1.2 s). sfx.impact — on every contact and freeze (see the SFX section).
rig.locked_on — the ball or the athlete stays in the center while the world spins at 50–110°/s, 1.5–3 s, in and out on
beats, 1–2 times. cut.quick — 1/8 link shots of teammate and crowd reactions, no longer than 1 bar. shake.beat — heavy
(4–5 %) on the contact frame, a 2 % hit shake on the kick of the downbeats for no longer than 2 bars. zoom.crash ×3–4
into the face after a goal or a winning shot.
**Outro.** time.slow_motion ×0.4–0.5 on the celebration, 2–3 s. gfx.counter — the final tally (points, goals, seconds)
lands on the last downbeat. time.freeze 2–3 s — the final freeze with the name. type.kinetic — the name or a short
summary.
**Limits per 10 s:** ramps ≤ 3 (one per play), freeze frames ≤ 1 per 8–10 s (≤ 3 per 30 s, including the hook and
outro), counters ≤ 3 per video and one on screen, heavy shake ≤ 1 per 4 bars, punches outside the drop ≤ 1 per bar,
rig.locked_on 1–3 per video, zoom.crash ≤ 1 per 8 bars, RGB ≤ 4. Within one beat ≤ 2 accents from {punch, shake, flash,
RGB}, on the frame of the key contact up to 3.
**Genre signature:** time.speed_ramp, time.freeze, gfx.counter, sfx.impact, time.slow_motion: "action peaks, freeze
frames with text, hits, stats".
**Allowed:** the shooting techniques the cards mark as signature (time.super_slow_motion, drone.fpv, rig.mounted,
pov.first_person, fx.omni_360) are used when such shots exist in the sources (they cannot be made in code); angle.low
and shot.close_up — faces and strength; handheld.shaky — behind the scenes and the locker room; trans.flash, trans.zoom,
fx.rgb_split, fx.color_shift (a B&W freeze that keeps the team color), time.velocity (a training montage, not on plays),
time.echo_trail and time.motion_blur (sprint speed), cut.match (identical movements from different plays), cut.stutter
(the wind-up before a strike), zoom.in_out, light.flash (stadium lights), layout.split_screen and layout.frame_division
(comparing two players, the athlete + the scoreboard), type.lower_third (name and team in a post-game interview),
look.vhs (a retro mixtape).
**Forbidden:** trans.dissolve and trans.double_exposure — a semi-transparent dissolve blurs the contact and the
trajectory; fx.kaleidoscope — breaks the play into a pattern, and the fact disappears; look.drunk — the rocking frame
makes it hard to follow the ball; look.dreamcore, scene.liminal, anim.oil_paint, anim.watercolor — a dreamy, painterly
texture replaces fact with mood. An emotional tribute with dissolves and empty spaces belongs to the epic and dramatic
genres.

## SFX
- The hit is the genre's signature: the contact of every play and every freeze frame get sfx.impact (align='attack',
  +0…+10 ms to the frame) within the limits below; extra contacts stay silent rather than being shifted.
- Hook: the sfx.impact "hit-stop" variant on the freeze frame (punch at −6 LU or boom at −2 LU, the music off until the
  next downbeat, 0.3–1 s); sfx.whoosh (air at −6 LU, peak on the last frame of the rush) under zoom.crash.
- Build: sfx.whoosh under whip transitions and fast tracking shots (≤ 3 per 10 s); sfx.riser 2–4 beats before the drop,
  only if the track has no rise.
- Drop: sfx.impact punch on contacts: up to 1 per beat for no longer than 2 bars, then ≤ 1 per bar; the "stretched"
  variant (pitch ×0.7, decays ×2) on a contact in super slow motion; sfx.sub_drop on the first beat of the drop or on
  the entry into the first super slow motion, one per section; paired with a hit, both go 3 dB lower; sfx.whoosh on the
  start of the rig.locked_on spin and on zoom.crash.
- Outro: sfx.impact boom (−2 LU) on the landing of the final counter or the final freeze; the metallic variant for the
  final title.
- Game sound: on 1–3 key contacts, the real source sound (a strike, a whistle, the roar of the stands) for 0.3–0.6 s
  around the contact at −12…−8 LU under the music; under it, a synthetic hit 3 dB quieter.
- Counter ticks are not needed in a music video: the count lands on a downbeat. Limits: in the drop up to 1 hit per beat
  for no longer than 2 bars, then ≤ 1 per bar; outside the drop ≤ 3 per 10 s; the main boom ≤ 1 per 15 s; under a hit
  the music at 30–150 Hz −3…−6 dB.

## Color
- Direction: clean, contrasty, rich uniform colors, crisp edges.
- Engine: grade={preset:'color', auto:0.7, contrast:1.20, sat:1.12, temp:0.0, black:0.03, gain:0.98} + unsharp
  sharpening 0.3–0.5 on 1080p sources.
- Contrast ×1.15–1.25; saturation ×1.10–1.20; do not shift the hue of the uniforms and the team colors by more than 5°;
  balance: arenas with sodium or LED lighting temp −0.05 (≈ −150 K), outdoors by day 0…+0.03; black point black 0.03
  (≈8/255 → 0); whites ≤ 250/255.
- Freeze frame: optionally B&W with preset bw_hi (contrast 1.35), or desaturation to 0.3 with the team color kept
  (fx.color_shift) for the duration of the freeze; the color returns with the cut.
- Night stadiums: sat ×1.05, black 0.04; HFR under artificial light: deflicker (a 5–9 frame window) before the grade.
- Look: look.vhs only for a video that is a retro mixtape as a whole.

## Text
- Name and number on the hook freeze: type.behind_subject: the number at 30–50 % H behind the athlete, or blocks above
  and below the head (y 0.12–0.30 and 0.62–0.80); a narrow extra-bold sans-serif 800–900 in uppercase, tabular figures.
- Words in the build: type.kinetic, 1–3 words, a single word at 70–86 % W (≈10–14 % H), a phrase at 5–7 % H.
- Stats: gfx.counter: the number ≤ 72 % W wide (≈9–13 % H), the label 2.4–3.0 % H; position y 0.32–0.55 or a free third
  next to the athlete; no closer than 5 % of the frame to the ball and the contact point, never over a face; a #000
  backing at 50–60 % when contrast is < 4.5:1. Number format follows the caption language (English: 12,500 and 4.5; Russian: a thin-space digit group from 5
  digits up, a decimal comma, "45 %"). Numbers and names come only from the user's data.
- Name plate (type.lower_third, interviews): the name at 3.5–4.5 % H, the block in y 0.66–0.78.
- Safe zone: y 0.12–0.80, x 0.06–0.88. Text appears 3–8 frames after the freeze starts and holds ≥ 1 s (+0.3 s for
  each word beyond three); one text block on screen; no text during fast play, only on freezes, in slow motion and
  between plays.

## Quality checks
- Contacts: ≥ 80 % of contact frames within ±1 frame of a beat, ≥ 50 % on downbeats.
- Readability: after each contact ≥ 0.3 s of the result before the cut; the ball and the athlete stay within x
  0.15–0.85 of the 9:16 frame during the play; the face is not cut by the crop (face_issues = 0).
- Freeze frames: hold 0.5–1.5 s (hook and outro up to 3 s); freezedetect finds only the planned freezes; the freeze
  frame has sharp_rank ≥ 0.7 within ±3 frames.
- Slow parts: rate ≥ 0.4 for 25–30 fps sources; super slow motion only from sources of ≥ 120 fps.
- Counters: the final value on screen = the value in the data (qa_numbers), landing on a beat ±1 frame, held ≥ 1.2 s.
- Grid: cuts_on_grid_share ≥ 0.85; max_shot ≤ 4.0 s.
- Loudness: −14 LUFS ±1, true peak ≤ −1.0 dBTP, limiter gain reduction on hits ≤ 3 dB; hits: outside the drop ≤ 3 per
  10 s, in the drop ≤ 1 per bar after a 2-bar series.
- Text within y 0.12–0.80 and x 0.06–0.88, does not cross the face and ball boxes, contrast ≥ 4.5:1.
- Broadcast graphics: no static logos or scoreboards in the frame corners (a static text-zone detector).
- Black frames only where intended; flashes ≤ 3 per second.
