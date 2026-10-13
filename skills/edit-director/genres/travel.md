---
genre: travel
slug: travel
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–2 s (0–7 %)",   goal: "the 'I want to go there' feeling: the brightest place of the trip and the promise of a journey within 2 seconds"}
  - {part: build, t: "2–12 s (7–40 %)", goal: "the road and arrival: packing, transport, first steps — forward motion, whip transitions on the snare"}
  - {part: drop,  t: "12–24 s (40–80 %)", goal: "a kaleidoscope of places on the beat: cuts matched on motion and shape, a drone reveal, people and the flavor of the place"}
  - {part: outro, t: "24–30 s (80–100 %)", goal: "a warm ending: sunset, departure, a photo dump and the place name — you want to save it and watch it again"}
rhythm:
  shot_len_s: {hook: [0.5, 2.0], build: [1.0, 2.0], drop: [0.5, 1.0], outro: [1.5, 3.0]}
  cut_grid: {hook: "every beat (3–4 places with whip transitions) or one shot per bar; the first cut on the first downbeat", build: "every 2–4 beats; whip transitions on the snare (beats 2 and 4); a hyperlapse holds 2–4 beats", drop: "every beat; runs of motion-matched cuts — 3–6 seams in a row on half-beats or beats; drone reveal — 2–4 beats from the first downbeat", outro: "once per bar; the final shot — 1–2 bars"}
  on_beat_share: 0.85
  max_shot_s: 4
moves:
  hook:  [drone.aerial, pov.first_person, shot.extreme_wide, cut.quick, trans.whip]
  build: [track.follow, rig.mounted, time.hyperlapse, time.fast_motion, cut.match, trans.whip, reflect.window, gfx.route_map]
  drop:  [cut.vector_match, cut.match, trans.whip, trans.zoom, cut.quick, drone.aerial, shot.video_portrait, cut.crash]
  outro: [zoom.out, time.timelapse, fx.light_leak, look.photo_prints, shot.extreme_wide]
  signature: [trans.whip, cut.match, cut.vector_match, drone.aerial, time.hyperlapse]
  allowed: [shot.wide, angle.birds_eye, angle.water_level, drone.fpv, pan.basic, tilt.basic, track.subject, scene.underwater, scene.forced_perspective, focus.tilt_shift, fx.tiny_planet, gfx.touch_gesture, glitch.film_damage, time.time_slice, trans.hidden_cut, trans.portal, type.diegetic, type.hand_drawn, type.intertitle, anim.line_art, gfx.counter, time.speed_ramp, time.slow_motion, loop.end, fx.film_overlay, type.subtitles]
  forbidden: [glitch.pixel_sort, glitch.datamosh, fx.glitch, cut.stutter, look.dystopian, angle.dutch]
sfx: {hook: [sfx.whoosh], build: [sfx.whoosh], drop: [sfx.whoosh, sfx.impact], outro: [sfx.whoosh]}
looks: [look.film, look.vhs]
---

# Travel

## Goal and platform
A travel and lifestyle edit turns a trip, a weekend or a day in the city into a light memory video: in half a minute the viewer "rides" the route and wants to go there too. What matters most is forward motion, changing places without losing pace, and a feeling of sunshine. Material: footage from a phone, an action camera and a drone — the road, stations and transport windows, streets, beaches, food, people, views.

- Platforms: TikTok, Reels, Shorts — 9:16, 15–60 s, typically 30 s; a horizontal 16:9 version for long-form platforms follows the same rules.
- Music: upbeat indie, pop, house, afro, light electronic, 100–125 BPM; it needs a steady beat (`steady` = true) and a clear entry into the chorus or drop (`drops[0]` or the start of the loudest section).
- Neighbors: vs. epic — brighter and lighter, the transitions are visible and playful (whip, zoom), scale is not the main goal; vs. calm — the pace is 3–4 times faster, places and the route matter, not the mood; vs. viral — no meme and no talking to camera, the story is the road itself; vs. fashion — the hero does not pose, they travel.

## Structure by seconds
Typical video: 30 s at 120 BPM — beat 0.5 s, bar 2 s, 15 bars.

| part | time | bars | on screen | in the music | which shot |
|---|---|---|---|---|---|
| hook | 0–2 s (0–7 %) | 1 | option A: the 3–4 best places, one per beat, with whip transitions; option B: one first-person shot (a jump into the water, a window with a view, stepping out onto a viewpoint) or a drone reveal; the place name | the first downbeat of the track, no intro | the brightest place of the trip |
| build | 2–12 s (7–40 %) | 2–6 | the road: packing, the station, a train or plane window, a mount on a car or bike, following the hero, a hyperlapse into the city; shape-matched cuts (door → door, hand → hand); optionally a route map for 2–3 s before a new place | verse, build-up | the camera moving forward, transport, first steps at the destination |
| drop | 12–24 s (40–80 %) | 7–12 | a kaleidoscope: on the first beat — a drone reveal or a "city → nature" crash cut; then places on the beat: runs of motion-matched cuts, whip and zoom transitions, portraits of locals, food and details in a quick burst | chorus or drop | the most beautiful and varied places, people, the flavor of the place |
| outro | 24–30 s (80–100 %) | 13–15 | a sunset timelapse, a light leak, a photo dump of 4–6 photos, a pull-out from the hero to the view; the final caption "place · month, year"; optionally a loop back to the first frame | the last phrase, a fade-out or a hard stop on a downbeat | sunset, blue hour, the hero walking off into the distance |

Track window: the chorus entry (`drops[0].t` or the start of the loudest section) lands at 12 s ± 2 s (35–45 %); the video starts on a downbeat, preferably without a quiet intro; it ends on a downbeat at the end of a phrase. Default order of places: by capture time (metadata): arrival → days → departure; inside the drop we reorder places for continuity of motion. Other lengths: ≈16 s — hook 1 bar, build 2, drop 4, outro 1; 60 s — hook 0–4, build 4–24 (two "roads": into the city and out of town), drop 24–48, outro 48–60.

## Rhythm
| part | shot length | cut grid | transitions |
|---|---|---|---|
| hook | 0.5–2 s | a run on every beat or one shot per bar; the first cut on the first downbeat | a whip on every seam of the run |
| build | 1–2 s | every 2–4 beats; a hyperlapse 2–4 beats | whip on the snare (beats 2 and 4), ≤ 1 per bar |
| drop | 0.5–1 s (in runs 0.25–0.5 s) | every beat; runs of motion-matched cuts — 3–6 seams in a row on half-beats or beats; drone reveal 2–4 beats | whip and zoom ≤ 5 per 10 s, ≥ 0.5 s apart |
| outro | 1.5–3 s | once per bar; the final shot 1–2 bars | photo dump — one photo per beat |

- Pace: hook — a short "trip teaser", build — calmer (the road), drop — the densest, outro — slowing down. A run of transitions (≤ 4–6 in a row) must always be released with a shot ≥ 1.5 s.
- The seam of a whip or zoom transition lands on a beat (the snare or a downbeat); the whoosh peak coincides with the seam.
- A run of motion-matched cuts keeps one direction for 3–6 seams, then a landing of ≥ 1 bar; change direction only through a landing or a whip in the opposite direction.
- No pauses to black. The only "pause" is a 1.5–2 s landing on a view after a run.

## Shot selection
Features: `motion`, `cam` (camera scale, roll and shift per frame), `sharp`, `luma`, saturation, `scale`, `person`, `face_share`, capture time and location from metadata. Thresholds are percentiles P over the user's source footage.

| slot | what goes there | criteria |
|---|---|---|
| hook | the brightest place | an aerial or extreme wide shot with a clear landmark (water, mountains, a city), saturation ≥ P70, `sharp` ≥ P60; or a first-person shot: hands in the lower third (`person` at the bottom edge), `motion` ≥ P70 |
| build | the road and forward motion | the camera moves forward (`cam` scale grows ≥ 0.3 %/frame) or steadily sideways; transport windows, mounts, following the hero; long steady walks ≥ 20 s are hyperlapse candidates |
| drop | places on the beat | a clear motion vector (shift ≥ 0.3 %/frame or push-in ≥ 1 %/frame, one direction for ≥ 0.5 s) for motion-matched cuts; pairs of shots with a matching shape (circle, door, hand, horizon) for cut.match; portraits: face frontal, `face_share` ≥ 0.8, `motion` ≤ P30; details of food and places for a quick burst |
| drop, first beat | the reveal | an aerial shot with a reveal, or the shot with the most contrasting world (city ↔ nature, night ↔ day) for a crash cut |
| outro | sunset and departure | warm low light, `motion` ≤ P40; a sunset or sky timelapse; the hero walking away into depth; the 4–6 best stills of the trip for the photo dump |

- Variety: ≥ 5 different places in the drop (clusters by capture time and location; without metadata — by color and content); one place takes no more than 25 % of the drop and no more than 2 shots in a row.
- Repeats: each source segment is used once; frames for the photo dump come from moments not yet shown as video, or from the climaxes of the drop (as a "souvenir snapshot").
- Reject: jitter > 1 % of the frame (except first-person running), a tilted horizon, blown-out sky (> 5 % of the area ≥ 250), tourists and passers-by in close-up as the main characters, signs and logos in focus, screens.
- Vertical: crop by `track(person)` or by a landmark, horizon on a third; a wide landscape that does not fit 9:16 goes into the outro or becomes an aerial-style slow drift along the view, or use `reframe` (with consent).
- No drone: build a high shot in code — a slow zoom-in ×1.15–1.3 over 3–5 s on a 4K shot from a rooftop or a mountain; no hyperlapse — speed up a steady walk ×10–20 with stabilization on a landmark; otherwise offer a generation with price confirmation.

## Moves by part
**hook (0–2 s)**
- drone.aerial / shot.extreme_wide — option B: one 2 s shot, the view revealed from the first beat.
- pov.first_person — option B: "you are the hero" (a jump, a window, a summit), 1–2 s.
- cut.quick + trans.whip — option A: 3–4 places, one per beat (0.5 s), a whip on every seam: blur window 5 frames, peak 20–36 % of the width per frame, one direction for the whole run.

**build (2–12 s)**
- track.follow — following the hero for 2–4 beats; their back in a dark passage serves as a wipe for the cut.
- rig.mounted — a mount on a vehicle: a run of 2–3 shots of 2 beats each, cuts on the beats.
- time.hyperlapse — 1–2 segments of 2–4 beats: ×10–20, the anchor held at one point of the frame ±5 %, the seam between segments is a 6–10 frame zoom blur on a downbeat.
- time.fast_motion — the road or packing at ×4–8, 1–2 s, a hard stop on a downbeat.
- cut.match — 1 rhyme or a run of 2–3: the key element matches in position ±2–5 % of the frame and in size ±10 %; within one cut the world changes (another city, day, vehicle).
- trans.whip — between locations on the snare, ≤ 1 per bar.
- reflect.window — a train, bus or plane window with reflections: "the road" without extra words, 2–4 beats.

**drop (12–24 s)**
- First beat: drone.aerial with a reveal (2–4 beats) or cut.crash — from the bustle of the city into the quiet of nature (zoom-in ×1.5–2 over 0.3–0.5 s, cut at the peak, B decelerates over 0.25–0.55 s) + sfx.impact. Crash cut — 1 per video.
- cut.vector_match — the main move of the drop: runs of 3–6 seams in one direction (vector cosine ≥ 0.75, speed B/A 0.65–1.5), pieces of 0.25–0.5 s, then a landing of ≥ 1 bar.
- trans.whip — on downbeats and the snare; ≤ 4–6 in a row, then switch the transition type.
- trans.zoom — 1 per 10–20 s: zoom-in ×2–3 into a detail over 0.3–0.5 s, exit from the same blur in a new place; paired with a whip — as a change of the motion axis.
- cut.match — 2–4 shape rhymes in a row on the beats (the same gesture, the same pose in different places).
- cut.quick — a burst of food and details, 4–8 pieces of 0.25 s (half-beat), then a 1–1.5 s landing.
- shot.video_portrait — a run of 2–4 portraits of local people, 2 beats each: the same shot size and centering, looking into the lens.

**outro (24–30 s)**
- time.timelapse — sunset or sky, 2–3 s.
- fx.light_leak — one warm light leak in the outro: either a transition into its first shot (peak on a downbeat) or the last shot fading into the leak over 1–2 s — not both (leak transition ≤ 1 per 8 bars).
- look.photo_prints — a photo dump of 4–6 photos, one per beat: white border 4–6 % of the width, tilt ±3–8°, a shadow; they drop into a stack.
- zoom.out / shot.extreme_wide — the final pull-out ×1.4 → 1.0 over 2–3 s to the view or to the hero walking away.
- Ending: the caption "place · month, year" on the last downbeat; if the video loops (loop.end, allowed), the last 0.5–1 s lead into the first frame and the caption is held on a plate.

**Route map** — gfx.route_map, optionally in the build for 2–3 s when the points are known: the route line is drawn in code over a plain background or a stylized map (the user's own map or one generated with their consent; we do not use base maps, icons or labels from mapping services), each leg 1–2 beats, start on a beat, the place pin lands on the downbeat frame ±1 frame; a flight is a dotted arc with a small plane, an overland route is a solid line. Points come from the user's list of places or the GPS metadata of the footage; no coordinates — a diagram with equal segments and no kilometers. Place labels use the same font as the place name in the hook. Optionally in the outro, an overview of the whole route for 2.5–4 s: pull out to the full path, pins on the beats, gfx.counter rolls up the kilometers or days of travel and lands on a downbeat.

**Limits**
| move | limit |
|---|---|
| trans.whip | a run ≤ 4–6 in a row, ≤ 5 per 10 s, spacing ≥ 0.5 s, ≤ 1 per beat |
| trans.zoom | ≤ 1 per 10 s |
| cut.crash | 1 per video |
| cut.vector_match | runs of 3–6 seams, ≥ 1 bar between runs |
| cut.quick | 1–2 bursts per 30 s, each ≤ 2 s |
| time.hyperlapse / time.fast_motion | ≤ 2 segments of each per 30 s, a segment ≤ 4 s |
| gfx.route_map | ≤ 2 appearances per video (the road in the build + the summary in the outro), ≥ 8 s apart; leg 1–2 beats; ≤ 8 pins on screen |
| fx.light_leak | leak transition ≤ 1 per 8 bars and never on two consecutive cuts; leak flash ≤ 1 per 4 bars; ambient leak ≤ 40 % of the duration; not on faces during a spoken line |
| text | ≤ 1 caption per 4 s |

**Forbidden and why**
- glitch.pixel_sort, glitch.datamosh, fx.glitch — digital "breakage" clashes with the genre's warm film texture (light leaks, burns) and smears the places we need to show.
- cut.stutter — the aggressive phonk-style "stuck" repetition breaks the light pace.
- look.dystopian — a cold, colorless image is the opposite of the sunshine and joy of a trip.
- angle.dutch — a tilted horizon in travel reads as a shooting mistake.

Not forbidden, but not used by default: time.velocity and heavy shake.beat (phonk energy), trans.flash (a light leak instead of a flash), zoom.punch (a whip or a zoom transition works better).

**Signature moves from the cards.** The move cards mark 39 signature moves for travel — the widest vocabulary of all the genres. In the signature: trans.whip, cut.match, cut.vector_match, drone.aerial, time.hyperlapse — they make travel recognizable on any footage. pov.first_person, shot.extreme_wide, cut.quick, track.follow, rig.mounted, time.fast_motion, reflect.window, trans.zoom, shot.video_portrait, cut.crash, time.timelapse, fx.light_leak, look.photo_prints, zoom.out are placed in the parts; gfx.route_map is also in the build but not in the signature: it needs route points from the user or from metadata. The rest (angle.birds_eye, angle.water_level, drone.fpv, pan.basic, tilt.basic, track.subject, scene.underwater, scene.forced_perspective, focus.tilt_shift, fx.tiny_planet, gfx.touch_gesture, glitch.film_damage, time.time_slice, trans.hidden_cut, trans.portal, type.diegetic, type.hand_drawn, shot.wide) are in allowed: they are special shots or "one-insert" techniques, and the video works without them. sfx.whoosh is in the `sfx` field.

## SFX
| part | sound | placement | level vs. music | limit |
|---|---|---|---|---|
| hook | sfx.whoosh "air" | peak on the seam of the first whip | −6 LU | 1–3 (the option A run) |
| build | sfx.whoosh | peak on the whip seam or on the acceleration of a speed-up; a reverse one into the hyperlapse entry | −6 LU (reverse −8 LU) | ≤ 3 per 10 s |
| drop | sfx.impact "punch" | attack on the first beat of the drop (the reveal or the crash cut) | −6 LU | 1 |
| drop | sfx.whoosh | peak on the seam of every whip and zoom transition | −6 LU, a heavy one on a zoom −4 LU | a run ≤ 5 per 10 s, no more than 1 per beat, spacing ≥ 0.5 s |
| outro | sfx.whoosh, reverse | cut off on the final caption or at the loop point | −8 LU | 1 |

- A whoosh only where the picture really moves fast (shift ≥ 8 %/frame, scale ≥ ×1.1/frame); shape-matched cuts and static shots get no sound. Never repeat the same buffer back to back.
- The "sound of the place" from the source footage is the key trick: a splash, a wave, a tram bell, a sizzling pan — short pieces of 0.3–0.8 s on a cut in the hook, on the first beat of the drop and in the outro, −12…−18 LU, the music is not ducked.
- Under a voice-over (vlog): music −10 dB, whooshes only in pauses ≥ 150 ms.
- Per 30 s video: whooshes ≤ 10, impacts ≤ 2, no riser (the track itself leads into the chorus), no glitch sounds.

## Color
Direction: sunny and natural — a vivid but not garish image, warm sun, blue sky, turquoise water, natural skin.

| parameter | value |
|---|---|
| contrast | S-curve +5…+12 %; luminance spread P95 − P5 = 0.65–0.75 |
| black point | P1 = 6–12 of 255 |
| white point | P99 = 238–250; sky ≥ 250 on no more than 0.5 % of the area (recover the highlights) |
| saturation | vibrance +15…+25 % (weak colors grow more), overall ×1.05–1.15; greenery and water no higher than saturation 0.75; skin — hue 18–28°, saturation 0.25–0.5 |
| place colors | sky hue 200–215°, sea and pools 170–195°, greenery 80–120° — pull them toward these ranges by ±5–8° |
| balance | neutral by day (±150 K); golden hour and sunset stay warm (+300…+500 K); night — cool shadows (hue 210–225°, 8–10 %) and warm lights |
| grain | fx.film_overlay level 1 only for look.film |

- Adjacent shots of the same place: ΔE of mean colors ≤ 6, brightness difference ≤ 15 %; color may change between places, but a temperature jump of more than 1500 K only through a transition (whip, light leak, crash cut), not a straight cut.
- Looks on request: look.film (film with light leaks and burns — "a vacation on film"), look.vhs (a home tape camcorder, 4:3 and a date in the corner — "a family video").

## Text
- Needed: the place name in the hook, optionally "day 2" or city labels when the location changes, a caption in the outro. Subtitles if there is a voice-over.
- Typeface: a clean bold sans-serif in caps with 10–20 % tracking, or handwritten (type.hand_drawn — "diary"); text inside the world of the shot (type.diegetic) — the name on the sky, a wall or sand, 1–2 times per video. No more than 2 typefaces.
- Size (9:16, H = 1920 px): the place name — a line ≤ 76 % of the width (≤ 820 px), cap height 6–9 % H for short names (up to 6 letters), smaller for long ones but not below 4 % H, otherwise break into 2 lines; date, coordinates, "day 2" — 2.2–3 % H; handwritten — not smaller than 3.5 % H.
- Position: above the horizon in the sky, y 0.18–0.35, or centered, y 0.42–0.50; everything within y 0.12–0.80, x 0.06–0.88; not on a face and not on the landmark of the place.
- Color: white or cream; on a bright sky — a 1–2 % H shadow at 40 % or dark text #1A1A1A; one accent from the palette of the place (the color of the sea, of the sunset); contrast ≥ 4.5:1.
- Animation: entry on a downbeat — a write-on of 0.6–1 s (handwritten), a rise with a fade-in of 0.3 s, or tracking to a landmark (the text "stuck" to the view, jitter ≤ 0.3 % of the frame); exit together with the shot or with a whip transition.
- Timing: ≥ 0.3 s per word + 0.5 s; the place name 1.5–2.5 s; labels 1.3–2 s; ≤ 1 caption per 4 s.
- Vlog subtitles: type.subtitles 3.5–4.5 % H, a semibold sans-serif, block at y 0.62–0.78.

## Quality checks
1. Grid: share of cuts on a beat or half-beat (±1 frame) ≥ 0.85; the first cut of the drop on `drops[0].t` ±1 frame; the seams of whip and zoom transitions on beats ±1 frame, the whoosh peak on the seam ±1 frame.
2. Shot lengths: part medians within `shot_len_s` (±20 %); no shot longer than 4 s; after a run of 4+ short shots — a landing ≥ 1.5 s.
3. Whip transitions: the blur direction and axis match on both sides of the seam (vector cosine ≥ 0.75); ≤ 5 per 10 s; spacing ≥ 0.5 s; no more than 6 in a row.
4. Shape- and motion-matched cuts: the key element at the seam matches in position within ≤ 5 % of the frame and in size within ±15 %; in cut.vector_match runs the direction stays the same for 3–6 seams.
5. Variety: ≥ 5 different places in the drop; one place ≤ 25 % of the drop and ≤ 2 shots in a row.
6. Horizon: roll ≤ 1° on all shots except intentional rotations and first-person shots.
7. Loudness: −14 ±1 LUFS integrated; true peak ≤ −1.0 dBTP; the "sound of the place" ≤ −12 LU relative to the music.
8. Black and frozen frames: no black frames (except the final fade-out ≤ 1 s); frozen frames only for the photo dump stills.
9. Color: P1 6–12, P99 238–250; blown-out sky ≤ 0.5 % of the area; skin hue 18–28°; adjacent shots of the same place ΔE ≤ 6.
10. Effects: leak transitions ≤ 1 per 8 bars, ambient leaks ≤ 40 % of the duration; flashes ≤ 2 per 10 s; brightness changes > 10 % over > 25 % of the area — no more than 3 per second.
11. Text: all blocks within y 0.12–0.80 and x 0.06–0.88; contrast ≥ 4.5:1; on screen ≥ 0.3 s/word + 0.5 s; ≤ 1 caption per 4 s.
12. Repeats and faces: no source segment is repeated; faces are not cut off by the crop (`face_issues` = 0).
13. Route (if gfx.route_map is used): every point, label and route number comes from the user's data or metadata (`qa_route_data`); pins land on downbeats ±1 frame; all map graphics are inside the safe zone; no third-party base map or labels.
