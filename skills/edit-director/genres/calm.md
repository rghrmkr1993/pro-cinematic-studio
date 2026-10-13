---
genre: calm
slug: calm
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–4 s (0–13 %)",   goal: "stop the feed with beauty and stillness: one composed living shot, soft light, something in the frame barely moving"}
  - {part: build, t: "4–14 s (13–47 %)", goal: "immersion: details, textures, time flowing — long shots melt into one another"}
  - {part: drop,  t: "14–24 s (47–80 %)", goal: "the climax of light: the most beautiful shot of the video holds for a long time, the music opens up"}
  - {part: outro, t: "24–30 s (80–100 %)", goal: "an exhale: a long final shot quietly fades to black together with the last note"}
rhythm:
  shot_len_s: {hook: [3.0, 4.0], build: [2.0, 4.0], drop: [3.0, 6.0], outro: [4.0, 6.0]}
  cut_grid: {hook: "one shot per 2 bars; the first change is the middle of a dissolve on the downbeat of bar 3", build: "once every 1–2 bars; the middle of the dissolve on a downbeat", drop: "once every 2 bars; the best shot — 2–3 bars; no half-beats", outro: "one shot per 2–3 bars; the fade to black ends on the last note"}
  on_beat_share: 0.8
  max_shot_s: 6
moves:
  hook:  [time.cinemagraph, frame.tableau, shot.wide, zoom.slow, fx.film_overlay]
  build: [trans.dissolve, zoom.slow, time.timelapse, focus.shallow, light.haze, pan.basic]
  drop:  [shot.extreme_wide, drone.aerial, time.slow_motion, zoom.slow, trans.dissolve, light.halation]
  outro: [shot.wide, zoom.out, trans.dissolve, trans.fade, fx.film_overlay]
  signature: [trans.dissolve, zoom.slow, fx.film_overlay, shot.wide]
  allowed: [anim.watercolor, fx.light_leak, focus.bokeh, trans.double_exposure, reflect.window, shot.video_portrait, angle.overhead_close, tilt.basic, track.roam, dolly.float, type.title_card, type.intertitle, type.hand_drawn]
  forbidden: [zoom.crash, zoom.punch, shake.beat, time.speed_ramp, trans.whip, trans.flash, cut.quick, cut.flash, fx.glitch, fx.rgb_split]
sfx: {hook: [], build: [], drop: [sfx.riser], outro: []}
looks: [look.film, look.dreamcore]
---

# Calm

## Goal and platform
A calm edit is a pause in the feed: slow living, nature, morning, home, coffee, the road, rain, the sea, a walk. The viewer's eyes get a rest; the video makes you want to watch it to the end and watch it again, not "get through" it. It works with long shots, soft dissolves, warm color and grain.

- Platforms: TikTok, Reels, Shorts — 9:16, 15–60 s, typically 30 s; a horizontal 16:9 version follows the same rules, without bars.
- Music: acoustic, lo-fi, ambient, neoclassical, quiet indie; 60–100 BPM (the seconds in the tables are for 120 BPM). The climax is not a drop but an opening-up: the entry of the vocals, the strings or the full ensemble; the engine finds it as the transition into the section with the highest `energy`, and `drops[]` is often empty for such tracks. If the beat tracker is unsure (`steady` = false or a low `tempo_conf`) — cut by bars and phrases (`bars`), not by beats.
- Neighbors: vs. drama — no conflict and no turning point, the color is light and warm; vs. travel — no whip transitions, no chronicle of the route and no upbeat pace, the mood matters more than the places; vs. epic — no impacts, no orchestral build-up and no "wow scale"; a wide shot here is about stillness, not grandeur.

## Structure by seconds
Typical video: 30 s at 120 BPM — bar 2 s, 15 bars. In this genre a shot change is the middle of a dissolve.

| part | time | bars | on screen | in the music | which shot |
|---|---|---|---|---|---|
| hook | 0–4 s (0–13 %) | 1–2 | one composed shot: a cinemagraph (only water, steam or leaves move), a tableau, or a wide shot with a slow push-in; an optional small title | intro, the first phrase | the "quietest" and most beautiful still shot |
| build | 4–14 s (13–47 %) | 3–7 | 3–4 shots of 2–4 s: details and textures with a shallow depth of field, hands, light in a window, a timelapse of clouds, a slow pan; everything flows through dissolves | the theme unfolds | details, textures, processes |
| drop | 14–24 s (47–80 %) | 8–12 | the climax of light: the best shot of the video (golden hour, open space, water, flight) holds for 4–6 s, gentle slow motion, glowing highlights; 2–3 shots | the opening-up: vocals, strings, the full ensemble | the best shot for light and composition |
| outro | 24–30 s (80–100 %) | 13–15 | a long final shot of 4–6 s: a slow pull-out, the hero walks away or the light fades; a fade to black of 1.5–3 s | the last phrase and the tail | the calmest wide shot |

Track window: place the start of the opening-up at 14 s ± 2 s (40–55 %); the video starts on the downbeat at the start of a phrase; it ends at the natural end of the track or of a phrase — we do not cut the music off but take it out with a 1.5–3 s fade to black. Other lengths: ≈16 s — hook 1 bar, build 3, drop 3, outro 1–2 (2–3 dissolves in the whole video); 60 s — hook 0–8, build 8–28, drop 28–48, outro 48–60, with one timelapse or cinemagraph inside the build as a pause.

## Rhythm
| part | shot length | cut grid | dissolve |
|---|---|---|---|
| hook | 3–4 s | one shot per 2 bars | the middle of the first dissolve on the downbeat of bar 3 |
| build | 2–4 s | once every 1–2 bars | 1–1.5 s |
| drop | 3–6 s | once every 2 bars; the best shot — 2–3 bars | 1.5–2.5 s (lyrical) |
| outro | 4–6 s | one shot per 2–3 bars | fade to black 1.5–3 s |

- Shot length is measured between the middles of dissolves. The middle of a dissolve lands on a downbeat ±1 frame (on a track without a confident grid — on the start of a bar or a phrase from `bars`).
- The editing pace does not speed up toward the climax — on the contrary, the shots in the drop are the longest. Energy grows through light, scale and music, not through the frequency of cuts.
- Straight cuts are allowed only within one scene (detail → detail of the same place), also on a downbeat; no shorter than 2 s.
- No pauses to black inside the video: the only fade to black is the final one (plus an opening from black ≤ 0.5 s).

## Shot selection
Features: `motion`, `cam` (camera movement), `sharp`, `luma`, `scale`, `person`, `face_share`. Thresholds are percentiles P over the user's source footage.

| slot | what goes there | criteria |
|---|---|---|
| hook | the most beautiful still shot | the camera is locked off (jitter ≤ 0.1 %, shift ≤ 0.05 %/frame) or barely drifts; local motion in one zone (water, steam, leaves, hair) makes it a cinemagraph candidate; `motion` ≤ P30; soft light (backlight, a window, golden hour); `sharp` ≥ P50 |
| build | details, textures, processes | close / details (hands, a cup, fabric, leaves, drops), shallow depth of field; `motion` P10–P50; a static or smooth camera (pan ≤ 0.25 %/frame @25 fps ≈ 6 % of the width per second, no jerks); timelapses with even exposure |
| drop | the best shot for light and composition | the maximum of the score C = 0.35·rank of "light quality" (golden hour, backlight, soft haze: warm tone, a mid-range brightness spread) + 0.25·rank of `sharp` + 0.25·open space (`scale` wide/no-face, horizon) + 0.15·camera smoothness; `motion` P20–P60 (alive but not busy) |
| outro | the calmest wide shot | wide / wide/no-face, `motion` ≤ P30, the light is fading (sunset, dusk) or the hero walks away into depth |

- Reject: shaky handheld footage (jitter > 0.5 % of the frame), sharp camera jerks and zooms in the source, crowds and bustle, close-up faces mid-conversation, hard midday light with blown highlights, neon and flickering light sources, screens and text.
- Repeats: each source segment is used once; no more than 2 details in a row without a wide shot; no more than 2 wide shots in a row without a detail.
- A pair for a dissolve: the mean brightness of the two shots differs by no more than 1.5×, otherwise the middle of the dissolve sinks into gray — even out the brightness or choose another pair; best of all is a match of the main shape (horizon, a bright patch) within ±5 % of the frame.
- Vertical: a landscape from 16:9 — a window on the brightest or most "eventful" area, the horizon on a third; if the sense of space is lost — `reframe` (with consent) or move the landscape to the hook/outro, where it holds longer.
- No shot for a cinemagraph — build the hook on a tableau or a wide shot with zoom.slow; no "climax of light" shot — the warmest wide shot + light.halation + a little more push-in.

## Moves by part
**hook (0–4 s)**
- time.cinemagraph — if there is a static shot with motion in one zone: a 1.5–4 s loop, a feathered mask, the loop seam through a 6–10 frame dissolve; hold it for the whole hook.
- frame.tableau — otherwise a composed still shot of 3–4 s.
- shot.wide — otherwise a wide shot with a slow push-in.
- zoom.slow — on any of them, ×1.04–1.08 per shot (0.05–0.1 %/frame @25 fps) — slower than in other genres.
- fx.film_overlay — level 2 from the first frame to the end of the video (for social media, grain 2–2.5 px, σ 5–8); switching it on mid-shot is forbidden.

**build (4–14 s)**
- trans.dissolve — the main transition: 1–1.5 s (25–38 frames @25 fps), linear or inOutSine, clip handles ≥ half the dissolve; the sound of the new shot comes in 0.3–0.5 s before its picture.
- zoom.slow — on every static shot: ×1.03–1.10, alternate the direction (in — out) no more often than every other shot.
- time.timelapse — 1 shot of 2–4 s (clouds, light on a wall, shadows): even, no flicker.
- focus.shallow — details with a blurred background; mask-based simulation only on simple shapes (a cup, a hand), not on hair.
- light.haze — a soft veil for an episode: 0.15–0.25, blacks P1 up to 20–30, saturation ×0.8; one strength for the whole scene.
- pan.basic — a slow pan of 2–6 % of the width per second, no jerks; pans in adjacent shots go in the same direction.

**drop (14–24 s)**
- shot.extreme_wide / drone.aerial — the best shot: open space, water, a field, mountains, a city at dawn; 4–6 s.
- time.slow_motion — a gentle slow-down to 0.5–0.7 (water, hair, steps, fabric), ≥ 2 s on screen; from 25/30 fps — no lower than 0.5.
- zoom.slow — ×1.05–1.10 over the whole best shot.
- trans.dissolve — a lyrical 1.5–2.5 s dissolve into the climax; its middle on the first downbeat of the opening-up.
- light.halation — a smooth rise of the highlight glow into the climax: strength 0.15–0.25 → 0.35 over 1–1.5 s, halation 3 % H; only if the shot has the sun, highlights on water or light sources.

**outro (24–30 s)**
- shot.wide — the final wide shot, 4–6 s.
- zoom.out — a slow pull-out ×1.15 → 1.0 over the whole shot, linear.
- trans.dissolve — the last transition into the final shot, 1.5–2 s.
- trans.fade — a 1.5–3 s fade (to black or to a warm white #FFF4E6), the music fades together with the picture down to −60 dB; the grain stays on the black at 30–50 % strength.
- fx.film_overlay — the same level up to the last frame.

**Limits**
| what | limit |
|---|---|
| cuts | ≤ 3 per 10 s (≤ 10 per 30 s) |
| trans.dissolve | on 70–100 % of cuts; length 0.8–2.5 s, never shorter than 0.6 s |
| zoom.slow / zoom.out | ≤ 0.2 %/frame (×1.05 per second), no acceleration |
| time.slow_motion | ≤ 40 % of the running time, rate 0.5–0.7 |
| light.haze, light.halation | one strength per scene, no "switching on" at a cut |
| time.cinemagraph | 1–2 per video |
| flashes, shake, whooshes, impacts | 0 |

**Forbidden and why**
- zoom.crash, zoom.punch — a sharp hit of scale destroys the stillness.
- shake.beat — shaking on the beat is the opposite of calm.
- time.speed_ramp — a jolt of speed, "action".
- trans.whip, trans.flash — an abrupt transition and a flash; here the transition is a dissolve.
- cut.quick, cut.flash — a burst of short shots means energy, not rest.
- fx.glitch, fx.rgb_split — digital breakage of the image.
The cards forbid another 48 moves for this genre (velocity, stutter, datamosh, fisheye, crash transitions, etc.) — we agree with all of them; the list above holds the ones the engine most often reaches for "out of habit".

**Signature moves from the cards.** Of the 11 moves the cards mark as signature, the genre signature holds trans.dissolve, zoom.slow, fx.film_overlay, shot.wide. time.cinemagraph, frame.tableau, time.timelapse, light.haze, shot.extreme_wide, drone.aerial are placed in the parts: each one needs a special shot or works for an episode rather than the whole video, so they do not go into the signature. anim.watercolor is in allowed: a watercolor memory insert fits, but not in every video.

## SFX
| part | sound | placement | level vs. music | limit |
|---|---|---|---|---|
| hook | — | — | ambience from the source (birds, surf, rain, a kitchen) | −18…−24 LU under the music |
| build | — | — | the ambience of the scene comes in under the dissolve 0.3–0.5 s before the picture | −20…−24 LU |
| drop | sfx.riser, only the "swell" variant (a soft rise without an impact) | the peak at the middle of the dissolve into the best shot | −10 LU (−14…−8) | 1 per video; skip it if the track opens up by itself (loudness rises ≥ 3 dB over 2 bars) |
| outro | — | — | the ambience fades out together with the music | — |

- No synthesized impacts, sub drops, whooshes or glitches — the cards forbid them for this genre.
- Ambience comes from the source audio: 1 layer per scene, crossfaded together with the dissolve, noise reduction for wind in the microphone; voices from the source only as an unintelligible background.
- The music is never ducked — neither under the ambience nor under the swell: the ambience is simply quieter than the music.

## Color
Direction: soft, warm, airy — lifted "matte" blacks, creamy highlights, pastel cool colors.

| parameter | value |
|---|---|
| contrast | a soft curve −10…0 %; luminance spread P95 − P5 = 0.50–0.65 |
| black point | P1 = 14–26 of 255 (matte, not below 10) |
| white point | P99 = 228–242; ≥ 250 on no more than 0.2 % of the area |
| saturation | overall ×0.85–0.95; warm tones (orange, yellow, hue 20–60°) ×1.0; blues and cyans ×0.80–0.90 |
| balance | +300…+600 K warmer; tint +2…+4 toward magenta; creamy highlights (hue 40–50°, strength 5–8 %), warm or neutral shadows |
| glow | soft on the highlights: threshold 0.8, radius 2–3 % H, strength 0.1–0.2 |
| grain | fx.film_overlay level 2 (σ 5–8, grain 2–2.5 px) |

- Adjacent shots: ΔE of mean colors ≤ 6, difference of mean brightness ≤ 15 % — otherwise the dissolve looks "muddy".
- Night and overcast sources — a warm shift of no more than +300 K, so that they do not turn yellow.
- Looks on request: look.film (film with soft light leaks at the start and the end), look.dreamcore (the faded pastel of a "waking dream").

## Text
- Minimal text: 0–3 captions per video — a title or the place in the hook, optionally a one-line thought in the build, a caption in the outro. We do not use kinetic typography, beat text or karaoke subtitles.
- Typeface: a thin serif or an italic in lowercase, or a light sans-serif with +5…+10 % tracking; handwritten (type.hand_drawn) optionally for a "diary"; one typeface per video.
- Size (9:16, H = 1920 px): the main line 2.5–3.5 % H (48–67 px), a title up to 4.5 % H, never smaller than 2.5 % H.
- Position: in the "air" of the shot (sky, a wall, water) within y 0.12–0.80 and x 0.06–0.88; most often the upper third, y 0.18–0.32, or the center; not over a face or the main shape.
- Color: cream #F5EEDF or white at 85–90 % opacity, no outline; on a light background — a soft 1 % H shadow at 30 %; contrast ≥ 4.5:1.
- Animation: fade-in 0.8–1.2 s, fade-out 0.8–1.2 s, static or with a drift of ≤ 1 % of the height over the whole display; entry on a downbeat, never at the same time as a dissolve.
- Timing: on screen ≥ 3 s and ≥ 0.4 s per word + 1 s.

## Quality checks
1. Grid: dissolve middles and straight cuts on a downbeat (±1 frame) — share ≥ 0.80; with an unsure grid — on bar starts from `bars` ±2 frames.
2. Shot lengths: no shot shorter than 2 s (between dissolve middles); median ≥ 3 s; none longer than 6 s (in the 60-second version the final shot may run up to 8 s).
3. Dissolves: ≥ 70 % of cuts are trans.dissolve; each one 0.8–2.5 s long; the brightness at the middle of a dissolve does not drop below 0.7 of the brightness of the adjacent shots.
4. Calm: no flashes (brightness changes > 10 % over > 25 % of the area within ≤ 2 frames — 0, except natural light); digital push-ins ≤ 0.2 %/frame; no added shake; camera motion in the source — jitter ≤ 0.5 %.
5. Loudness: −14 ±1 LUFS integrated, true peak ≤ −1.0 dBTP; short-term loudness range (LRA) ≤ 8 LU; ambience ≤ −18 LU relative to the music.
6. Black: only the opening from black ≤ 0.5 s and the final fade to black; not a single black frame inside the video.
7. Frozen frames (freezedetect ≥ 0.5 s): only a tableau and a cinemagraph are allowed (in a cinemagraph a zone of ≥ 3 % of the area must move); no others.
8. Color: P1 14–26 (up to 30 in an episode with light.haze), P99 228–242; mean saturation ×0.85–0.95 of the source; adjacent shots ΔE ≤ 6.
9. Grain: the same level on all shots (σ differs by ≤ 15 %); grain and dust go under the text.
10. Text: 0–3 blocks, all inside the safe zone y 0.12–0.80, x 0.06–0.88; line height ≥ 2.5 % H; on screen ≥ 3 s; contrast ≥ 4.5:1.
11. Horizon: roll ≤ 1° on wide shots and landscapes.
12. Repeats and faces: no source segment is repeated; faces are not cut off by the crop (`face_issues` = 0).
