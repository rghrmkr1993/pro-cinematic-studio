---
genre: fanedit
slug: fanedit
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [10, 60], typical_s: 20}
structure:
  - {part: hook,  t: "0–2 s (0–10 %)",   goal: "recognize the hero and be moved: an iconic close-up, glow, the first word of the song or a line from the hero"}
  - {part: build, t: "2–8 s (10–40 %)",  goal: "story and feeling: the words of the song land on the hero's moments, slow motion, scene rhymes, memories"}
  - {part: drop,  t: "8–18 s (40–90 %)", goal: "the explosion: the hero in action on every beat — speed, flashes, shake, a stream of the best moments"}
  - {part: outro, t: "18–20 s (90–100 %)", goal: "the aftertaste: the hero's last look in slow motion, a freeze or a fade into light, the last word of the song"}
rhythm:
  shot_len_s: {hook: [0.5, 2.0], build: [0.5, 1.5], drop: [0.25, 1.5], outro: [1.0, 3.0]}
  cut_grid: {hook: "a cut on a downbeat or on the first stressed syllable of the vocal", build: "every 1–2 beats or on stressed vocal syllables: a word of the song = a cut or the word coming in", drop: "only on beats: every beat or every 1–2 beats inside a velocity clip; flashes and trick transitions on downbeats; a cut.flash stream for 1 bar", outro: "once every 1–2 bars"}
  on_beat_share: 0.85
  max_shot_s: 3.0
moves:
  hook:  [shot.close_up, fx.glow, fx.film_overlay, type.kinetic, zoom.punch, trans.flash]
  build: [type.kinetic, time.slow_motion, cut.match, trans.double_exposure, fx.color_shift, zoom.crash, time.echo_trail, fx.glow]
  drop:  [time.velocity, trans.flash, shake.beat, cut.flash, zoom.punch, fx.rgb_split, type.beat_text, trans.lens_distort]
  outro: [time.speed_ramp, time.freeze, time.slow_motion, fx.glow, fx.film_overlay, type.kinetic]
  signature: [type.kinetic, fx.glow, fx.film_overlay, time.velocity, trans.flash, cut.flash]
  allowed: [time.bullet_time, anim.cel, anim.comic, anim.live_mix, anim.pixilation, anim.rotoscope, anim.scribble, layout.aligned_split, layout.windowbox, rig.locked_on, roll.whip, zoom.infinite, cut.quick, cut.stutter, trans.arc, trans.chain, trans.morph, trans.portal, trans.spin, trans.zoom, frame.two_shot, fx.glitch, glitch.datamosh, glitch.vhs, light.flash, fx.letterbox, type.subtitles, loop.end, look.film, look.vhs, look.video_game]
  forbidden: [gfx.counter, gfx.callout, type.margin_notes, type.lower_third, look.news, trans.page]
sfx: {hook: [sfx.impact], build: [sfx.riser, sfx.whoosh], drop: [sfx.impact, sfx.whoosh, sfx.sub_drop, sfx.glitch], outro: [sfx.whoosh]}
looks: [look.film, look.vhs, look.video_game]
---

# Fan edit

## Goal and platform
An edit about a hero, a couple or a scene from a film, a series, an anime or a game for short-video feeds: 9:16,
10–60 s, typically 20 s (10 bars at 120 BPM; tracks — phonk, remixes, slowed versions with reverb, 70–150 BPM). The
rights to the source footage are the user's; the skill does not store other people's footage or song lyrics. The
viewer is a fan: the video should trigger recognition and feeling — delight, longing, pride in the hero. The language
of the genre is editing and words synced to the vocals, glow, film and tape texture on top, scene rhymes and an
explosive drop built on velocity and flashes. Differences from the neighbors: phonk — bass and menace on any material,
almost no text; viral — a universal video with a loop; fashion — the look; fan edit — the story and emotion of a
specific character, with the words of the song as their voice.

## Structure by seconds
The seconds are for 120 BPM (beat 0.5 s = 15 frames @30 fps / 12.5 @25 fps, bar 2 s); for slowed tracks at 70–90 BPM
the parts are the same in bars, and the seconds are longer.

| part | time (20 s) | bars | on screen | in the music |
|---|---|---|---|---|
| hook | 0–2 s (0–10 %) | 1 | an iconic close-up of the hero (the eyes, a turn to the camera) with glow, the name or the first word of the song, a punch-in on beat 2 or on a stressed syllable within the shot; variant — a cold open with a 1–3 s line from the hero with the source audio | the first vocal phrase or a downbeat; with a spoken line, the music comes in on the downbeat after it |
| build | 2–8 s (10–40 %) | 3 | the words of the song on stressed syllables, the hero's moments in slow motion, pose rhymes across different scenes, a double-exposure memory, B&W → color on an accent word, the glow grows | verse, pre-chorus, build-up |
| drop | 8–18 s (40–90 %) | 5 | the hero in action on every beat (velocity), flashes and shake on the kick, RGB on the snare, a 1-bar stream of the best moments, a slam word on the first beat, a trick transition 1–2 times | drop or chorus |
| outro | 18–20 s (90–100 %) | 1 | the hero's last look in slow motion, a ramp into a freeze, a fade into light, the last word of the song | the last phrase, the tail |

Track window: start on a downbeat or on the first syllable of a vocal phrase (if the vocal starts on a pickup — from
the pickup), the drop of the track at 35–45 % of the video; the length is a whole number of bars. Long edits of
40–60 s — two build → drop cycles.

## Rhythm
- Lengths: hook 0.5–2 s; build 0.5–1.5 s (slow-motion moments up to 3 s); drop 0.25–1.5 s — a clip in velocity lives
  for 1–3 beats, bursts and the stream are shorter; outro 1–3 s.
- Grid: hook — a cut on a downbeat or on the first stressed syllable; build — every 1–2 beats or on stressed vocal
  syllables (vocal onsets from the 300 Hz–3 kHz band, snapped to the nearest 1/16): a word of the song = a cut or the
  word coming on screen; drop — cuts only on beats, every beat or every 1–2 beats inside a velocity clip, flashes and
  trick transitions on downbeats, a cut.flash stream for 1 bar; outro — once every 1–2 bars.
- Share of cuts on the grid of beats and half-beats ≥ 0.85; together with the cuts on vocal syllables, ≥ 0.95 of cuts
  sit on one of the two events ±1 frame.
- Energy curve: hook — a single hit; build — 1–1.5 cuts/s, toward the end it speeds up and the glow grows; the last
  beat before the drop optionally empty (a black frame or a freeze); drop — 1–2 cuts/s plus a speed pulse on every
  beat; outro — 0.5/s.
- Slowed tracks at 70–90 BPM: in the drop, cuts on beats (0.67–0.86 s) and on half-beats in bursts; at 140+ BPM —
  velocity with a 2-beat cycle.

## Shot selection
1. Sources — films, series, anime, games: shot detection, then the hero = a cluster of faces or silhouettes that the
   user marks on a contact sheet. On drawn and game footage the face detector often misses — the center of interest
   comes from the person mask, contrast and motion.
2. Cleanliness: burned-in subtitles, channel logos and the source's own titles — a text-zone detector in the bottom
   25 % and in the corners; such zones are cropped out or the shot is not used; shots with the creators' credits are
   not used.
3. Hook: a close-up of the hero (face_h ≥ 0.25, the eyes visible), sharp_rank ≥ 0.7, a still gaze or a turn to the
   camera (a motion peak in the window); preferably backlight or highlights (p97 luma ≥ 200) — so that the glow has
   something to catch on.
4. Build: emotional moments — close-ups and two-shots (frame.two_shot for couples), motion_rank 0.1–0.5; pairs for a
   rhyme — the same pose and position in the frame in different scenes (mask IoU ≥ 0.5, centers within 5 % of the
   frame).
5. Drop: action — motion_rank ≥ 0.7 with frequent peaks (a hit, a run, a jump, a transformation, an explosion); for
   cut.flash — 12–30 close-ups of the hero aligned by the eyes ±3–5 % of the frame; do not put a face in close-up in
   the fast part of velocity.
6. Outro: the "last look" — a close-up with slow movement or the hero leaving; bright areas for the fade into light.
7. Words of the song: if the user has noted what a line is about (a name, "fire", "fall"), a shot with that content
   goes under the word; otherwise by rhythm.
8. Repeats: a source shot ≤ 2 times (frames of the cut.flash stream do not count), not in adjacent slots, the ranges
   do not overlap.
9. 16:9 → 9:16: reframe on the face or the silhouette; if the crop cuts something important — layout.windowbox (the
   shot as a window on a dark field) or a blurred background; low resolution — crop ≤ ×2.2 or upscale.

## Moves by part
**Hook.** shot.close_up — crop to a face of 60–90 % H, the eyes at 0.33 of the height. fx.glow dreamy (threshold 0.72,
strength 0.25) or a rim glow around the hero in an accent color (0.6–1.2) — from frame 0. fx.film_overlay level 1–2 —
from frame 0 to the end, never switched on mid-shot. type.kinetic — the hero's name or the first word of the song,
entering on the syllable ±1 frame. zoom.punch ×1.25 on beat 2 or on the first stressed syllable — after ≥ 0.3 s of the
shot at ×1.0 (no punch-in on frame 0 or on the first frame after a cut). trans.flash, 1 frame, on the first cut. Cold
open: a 1–3 s line from the hero (source audio, type.subtitles), the music comes in on the downbeat after it — the
hook then runs up to 3 s.
**Build.** type.kinetic — lines of the song, 1–3 words per screen, entering on the syllable onset −1…+2 frames, a word
≥ 0.3 s.
time.slow_motion ×0.5 (optical flow) on emotional moments, 1.5–3 s. cut.match — a pose or shape rhyme between scenes,
a run of 2–4 cuts. trans.double_exposure — a memory: a face + a scene for 1.5–3 s, screen 80 %, 1–2 times per video.
fx.color_shift — B&W → color or a monotone on an accent word, ≤ 1 per 8 bars. zoom.crash ×3 into the eyes on a
stressed word, ≤ 1 per 8 bars. time.echo_trail — a turn or a swing, 1–2 s. fx.glow — strength rising 0.1 → 0.6 over
the last 2–4 bars together with the build-up.
**Drop.** time.velocity — classic (r̄ 2.5, m 0.85) on action, the peaks on the beats; ≤ 50 % of the video. trans.flash
— 1 frame on the downbeat cuts, the color taken from the palette of the incoming shot, ≤ 40 % of cuts. shake.beat —
impact 2–2.5 % on the downbeat kicks, a run ≤ 2 bars; rotational 2.5° on the snare once every 1–2 bars. cut.flash — a
1-bar stream: 12–30 close-ups of the hero at 2 frames each, anchored on the eyes, the brightness of adjacent frames
evened out. zoom.punch bounce ×1.15–1.2 on the kick inside a clip (not on the beat of a cut), alternating bar by bar
with the shake. fx.rgb_split 8–12 px on the snare. type.beat_text — one slam word on the first beat of the drop (≤
84 % W), held for 1–2 bars.
trans.lens_distort — a bulge or a vortex on the seam of the first beat of the drop or of a part change, 6–7 frames in
and 7–8 back, ≤ 2 per video and not near other trick transitions.
**Outro.** time.speed_ramp — slow down into a freeze on the last downbeat. time.freeze 1–2 s — the last look.
time.slow_motion — the hero walking away. fx.glow — a fade into white over 1–2 bars (strength 0.3 → 3, threshold
0.72 → 0.3) and an exit to white of 0.3 s. fx.film_overlay — the same level up to the last frame. type.kinetic — the
last word of the song on the final beat.
**Limits per 10 s:** flashes ≤ 3 per second and on ≤ 40 % of cuts; RGB ≤ 12 pulses; impact shake — a run ≤ 2 bars;
glow pulses ≤ 1 per beat, strong ones ≤ 2 per second; trick transitions (lens_distort, spin, zoom, morph, portal) ≤ 1
per 8 bars and ≤ 3 per video, not on adjacent cuts; cut.flash ≤ 2 per video; double exposure ≤ 2 per video; text
≤ 35 % of the running time and ≤ 3 words per second. On one beat ≤ 2 accents from {punch-in, shake, flash, RGB}, on
the first beat of the drop — up to 4 (flash + shake + RGB + the slam word; a punch-in only if the shot runs through
the beat of the drop without a cut).
**Genre signature:** type.kinetic, fx.glow, fx.film_overlay, time.velocity, trans.flash, cut.flash — "sync with the
lyrics, glows, overlays" plus speed, flashes and a stream of the hero's moments.
**Allowed** — moves the cards mark as signature that depend on the material or the request: time.bullet_time
(generation with consent), anim.cel, anim.comic, anim.live_mix, anim.pixilation, anim.rotoscope, anim.scribble (drawn
inserts, 1 segment per video), layout.aligned_split, layout.windowbox, rig.locked_on, roll.whip, zoom.infinite,
cut.quick, cut.stutter, trans.arc, trans.chain, trans.morph, trans.portal, trans.spin, trans.zoom (trick transitions
within the shared limit), frame.two_shot (couples), fx.glitch, glitch.datamosh, glitch.vhs (a transition on the drop,
tape texture), look.video_game (edits about games). Also allowed: light.flash, fx.letterbox (a cinematic hook opening
out of a slit), type.subtitles (a line in the cold open), loop.end (a looping ending instead of the fade into light),
the looks look.film and look.vhs.
**Forbidden:** gfx.counter, gfx.callout, type.margin_notes — explanatory graphics break the immersion in the hero's
story; type.lower_third and look.news — reportage and news plates; trans.page — a slideshow "page turn" cheapens the
cinematic tone.

## SFX
- Hook: with a cold open — the line from the source (short-term loudness −16…−14 LUFS, the music under it ≤ −24 LUFS
  or muted); sfx.impact (boom −2 LU or a hit-stop) on the music entry — only if the track has no strong hit on that
  beat.
- Build: sfx.riser 2–4 beats before the drop — only if the track has no build-up of its own; sfx.whoosh (air −6 LU,
  peak on the seam) under zoom.crash and transitions with real motion.
- Drop: sfx.impact on the first beat of the drop (punch −6 LU; if the track has a powerful kick — only the click
  through a 150 Hz high-pass filter); sfx.sub_drop — only after a pause and without an 808 on that beat, one per drop;
  paired with an impact, both 3 dB lower; sfx.whoosh — under trick transitions; sfx.glitch — in sync with fx.glitch
  bursts and the datamosh (bitcrush the track for the duration of the mosh).
- Outro: a reverse sfx.whoosh (−8 LU) cut off on the frame of the fade into white or of the freeze; optionally a tape
  stop (sfx.glitch tape_stop) — once.
- Diegetic hits: on 1–3 peaks the source sound can be kept (a sword strike, a gunshot, a roar) for 0.3–0.6 s at −10 LU
  under the music. In total ≤ 3 sounds per 10 s; limiter gain reduction ≤ 3 dB.

## Color
- First, even out the sources: each shot gets auto 0.6 (levels stretched by p0.5–p99.6) and exposure so that the luma
  median lands in 90–120/255: film, anime and game footage sit side by side without jumps (|Δ median| of adjacent
  shots ≤ 25/255).
- Engine: grade={preset:'teal', auto:0.6, contrast:1.18, sat:1.0, temp:-0.05, black:0.03, gain:0.96}.
- Contrast ×1.15–1.25; saturation ×0.9–1.1 (anime 1.0–1.05, live action 0.9 with a teal split: shadows [0.0, 0.35,
  0.4], highlights [1.0, 0.85, 0.7], strength 0.25–0.35); balance temp −0.05…−0.10 for night and action or +0.08 for
  romance — one per video; black point black 0.03; whites ≤ 245/255, except for the fade into white.
- Glow: a constant dreamy glow — threshold 0.72, strength 0.2–0.3, radii 0.4/1.5/4 % of the short side; neon 0.5–1.0
  only on night shots; blacks below the threshold are not lifted.
- Texture: fx.film_overlay level 1–2 (grain σ 2–5 levels) over the whole video; the level changes only on the downbeat
  of a part boundary (for example, a flashback — level 3).
- Looks: look.film, look.vhs, look.video_game (for game edits).

## Text
- Words of the song (type.kinetic): the user provides the text — the engine does not transcribe or store the lyrics of
  other people's songs; timing from the vocal onsets with manual correction. 1–3 words per screen (4 at most),
  entering on the syllable onset −1…+2 frames, a word ≥ 0.3 s, ≤ 3 words per second.
- Class: a high-contrast serif (lyrical) or a condensed extra-bold sans-serif in caps (hype); a display face only for
  the slam word; 1 typeface + 1 display face per video; the font covers the caption language.
- Size: a single word 60–80 % W (≈8–14 % H), a line of 2–4 words ≤ 76 % W at 5–7 % H, the slam word up to 84 % W; the
  hero's name in the hook 9–12 % H.
- Position: center y 0.40–0.55; if the hero's eyes are there — a free anchor at y 0.24 or 0.68; everything within y
  0.12–0.80 and x 0.06–0.88.
- Color: white with a letter glow of 0.3–0.5 or an accent color from the shot; contrast ≥ 4.5:1, otherwise a 35 %
  darkening.
- Animation: one per series of words — an impact entry ×1.15 → 1.0 over 3–4 frames or a 2–3 frame fade-in; the word on
  the drop is a slam; no different animation for each word.
- A line in the cold open — type.subtitles 3.5–4.5 % H, block at y 0.62–0.78.

## Quality checks
- Word sync: ≥ 90 % of word entries within −1…+2 frames of the vocal syllable onsets.
- Grid: cuts_on_grid_share ≥ 0.85; together with the cuts on syllables, ≥ 0.95 of cuts on an event ±1 frame.
- Glow: the brightness p1 after the glow is not more than 3 levels above the original (no haze); strength > 0.35 only
  on shots with a luma median ≤ 90.
- Flashes: ≤ 3 per second; adjacent frames of the cut.flash stream differ in mean relative brightness by ≤ 0.1 (safe
  mode), large brightness jumps ≤ 3 per second; no red flashes in series.
- Source cleanliness: no burned-in subtitles or logos in the frame (the text-zone detector in the bottom 25 % and the
  corners = 0).
- Texture: the grain level is constant within a part (the grain σ of adjacent shots differs by ≤ 20 %).
- Loudness: −14 LUFS ±1, true peak ≤ −1.0 dBTP; the cold-open line −16…−14 LUFS short-term.
- Crop ≤ ×2.2 or upscale; face_issues = 0.
- Black frames — only intended ones (the empty beat before the drop, 1–2 frame hits); frozen frames — only freeze
  frames.
- Text in the safe zone, ≤ 35 % of the running time, not over the hero's eyes.
