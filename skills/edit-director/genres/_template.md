---
genre: epic                     # genre key = the slug (one of the 15); exactly as in the genres field of move cards
slug: epic                      # file name: genres/<slug>.md
kind: music                     # music (cut to the beats) | speech (cut to the words)
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:                      # video parts; time in seconds for the typical length and as a share of the length ("A–B s (P–Q %)", the planner reads the % range)
  - {part: hook,  t: "0–2 s (0–7 %)",   goal: "what the viewer should feel"}
  - {part: build, t: "2–12 s (7–40 %)", goal: "..."}
  - {part: drop,  t: "12–24 s (40–80 %)", goal: "..."}
  - {part: outro, t: "24–30 s (80–100 %)", goal: "..."}
rhythm:
  shot_len_s: {hook: [1.5, 3.0], build: [1.0, 2.0], drop: [0.25, 0.75], outro: [2.0, 4.0]}
  cut_grid: {hook: "a cut once per bar", build: "every 2 beats", drop: "every beat, half-beats on the accents", outro: "once every 2 bars"}
  on_beat_share: 0.85           # share of cuts that land on a beat/half-beat (±1 frame)
  max_shot_s: 4
moves:                          # only ids from moves/index.json (moves + planned)
  hook:  [zoom.slow, fx.letterbox]
  build: [time.speed_ramp, cut.quick]
  drop:  [cut.flash, zoom.crash, time.freeze]
  outro: [zoom.out, trans.fade]
  signature: [zoom.crash, time.speed_ramp]   # a subset of the parts: the genre's signature moves
  allowed: [shake.beat, fx.glow]             # fit situationally in any part
  forbidden: [fx.kaleidoscope, glitch.pixel_sort]
sfx: {hook: [], build: [sfx.riser], drop: [sfx.impact, sfx.sub_drop], outro: []}
looks: [look.film]              # (optional) looks that sit well on top of the genre
---

# Epic

<!-- The body has exactly these nine ## headings, in this order; the planner and scripts/check_genre.py read them by name. -->

## Goal and platform
Why the video exists, who it is for, where it is published, how the genre differs from its neighbors.

## Structure by seconds
A table of the parts: time, what happens on screen and in the music, which shot we use.

## Rhythm
Shot lengths per part, the cut grid relative to beats and bars, how the editing pace changes over the course of the track, pauses.

## Shot selection
Which shots are needed and where (the best one on the drop), criteria: shot size, motion in the frame, faces, light, repeats; what to avoid.

## Moves by part
Hook / build / drop / outro — which moves, why and with which parameters; frequency limits; forbidden moves and why.

## SFX
Which sounds, on which events, loudness relative to the music, the limit per video.

## Color
The grade direction in numbers: contrast, saturation, balance, black and white points; suitable looks.

## Text
Whether text is needed, the font class, size in % of the frame height, position and 9:16 safe zones, animation, sync.

## Quality checks
Measurable checks after the render: share of cuts on the beat, max shot length, loudness (LUFS), black and frozen frames, text in the safe zone, effect limits.
