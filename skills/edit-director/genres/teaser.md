---
genre: teaser
slug: teaser
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [10, 30], typical_s: 20}
structure:
  - {part: hook,  t: "0–2 s (0–10 %)",   goal: "intrigue from the first frame: a fragment instead of the whole and a question — 'what is this?'"}
  - {part: build, t: "2–12 s (10–60 %)", goal: "rising tension: scraps, shadows and details between dips to black, phrase cards, a countdown — nothing is shown in full"}
  - {part: drop,  t: "12–16 s (60–80 %)", goal: "explosion: a stream of flashes and short shots on the beat — energy and a promise, but the main thing is still not visible"}
  - {part: outro, t: "16–20 s (80–100 %)", goal: "reveal: the hero or the product in full, the name and the date on the last hit — remember it and wait"}
rhythm:
  shot_len_s: {hook: [1.0, 2.0], build: [0.5, 2.0], drop: [0.25, 1.0], outro: [1.5, 4.0]}
  cut_grid: {hook: "fragment from the first downbeat for the whole bar; card from beat 2, on top of it", build: "bars 2–3 — a 2–3-beat fragment + a dip to black with a card on the downbeat; bars 4–5 — every 2 beats; bar 6 — every beat, a countdown or words on the beat, 1/16 of silence before the drop", drop: "first beat — a hit and a flash stream of 1–2 s (frame-by-frame changes, in and out on downbeats); then every beat, half-beats on accents; last beat — black", outro: "the reveal on a downbeat; the title lands on the last hit and stays until the end, at least 2 s"}
  on_beat_share: 0.9
  max_shot_s: 5
moves:
  hook:  [shot.extreme_close_up, light.silhouette, light.shadow_play, type.intertitle, fx.letterbox]
  build: [trans.fade, type.intertitle, shot.extreme_close_up, cut.insert, frame.voyeur, light.flash, type.beat_text, type.kinetic]
  drop:  [cut.flash, cut.quick, trans.flash, cut.match, cut.crash, zoom.crash]
  outro: [zoom.out, time.freeze, type.title_card, gfx.counter, fx.letterbox, trans.fade]
  signature: [type.intertitle, trans.fade, shot.extreme_close_up, light.silhouette, cut.flash, type.title_card]
  allowed: [dolly.zoom, dolly.infinite, pass.through, zoom.infinite, zoom.extreme, scene.giant, time.bullet_time, anim.ai_video, type.vintage_title, time.slow_motion, time.speed_ramp, shake.beat, focus.rack, light.hard, light.spotlight, scene.void, frame.central, fx.rgb_split, glitch.tv_noise, type.subtitles]
  forbidden: [gfx.callout, look.cheesy, fx.bobblehead, time.boomerang, trans.page, trans.iris]
sfx: {hook: [sfx.impact], build: [sfx.impact, sfx.riser, sfx.glitch], drop: [sfx.impact, sfx.whoosh], outro: [sfx.sub_drop, sfx.impact]}
looks: [look.dystopian, look.vhs, look.film]
---

# Teaser

## Goal and platform
A teaser announces something the viewer has not seen yet: a product, a collection, a video, a music video, an event, a channel. Its job is not to show but to make people wait: fragments instead of the whole, questions instead of answers, a build-up and a single reveal at the very end — the name, the date, "soon". Material: footage of the product or the hero, behind the scenes, details, plus generated shots if there is nothing to show yet.

- Platforms: TikTok, Reels, Shorts — 9:16, 10–30 s, typically 20 s (a series of teasers before a launch — 10–15 s each); a horizontal 16:9 version follows the same rules, bars 2.39:1.
- Music: a dark cinematic pulse, trailer hits, minimal electronica, a bass drone with a swell; 90–140 BPM; a rise and a hit are required (`drops[0]`), and at the end a final hit or a hard stop on a downbeat.
- Neighbors: vs epic — we hide rather than show, scale here is a tool for intrigue; vs product — no callouts, specs or price, only a promise; vs drama — the story is left untold; vs viral — the ending is not a loop but a full stop with a date.

## Structure by seconds
A typical 20 s video at 120 BPM: beat 0.5 s, bar 2 s, 10 bars.

| part | time | bars | on screen | in the music | which shot |
|---|---|---|---|---|---|
| hook | 0–2 s (0–10 %) | 1 | a fragment from the first beat: an eye, a detail, a backlit silhouette, a shadow on a wall; the frame is squeezed by bars; from beat 2 — a question card on top | a quiet drone and a low hit on the first beat | the most mysterious fragment: impossible to recognize as a whole |
| build | 2–12 s (10–60 %) | 2–6 | scraps of 0.5–1.5 s between dips to black and phrase cards; details, a view "through a gap", flickering light; speeding up toward bar 6; in bar 6 — a 3-2-1 countdown or words on the beat; 1/16 of silence before the drop | pulse and rise; a riser in bar 6 | details, parts, silhouettes, shadows — everything incomplete |
| drop | 12–16 s (60–80 %) | 7–8 | a hit; a stream of 12–25 images of 1–2 frames each; short shots on the beat, white flashes, a crash zoom into a detail, shape rhymes; last beat — black | the drop, the full beat | the most energetic fragments, the main thing still in shadow or in motion |
| outro | 16–20 s (80–100 %) | 9–10 | the reveal on a downbeat: a pull-out from a familiar detail to the whole, the bars open up; a freeze frame; the name and the date on the last hit; optionally a countdown timer to the date | the final hit and a sub drop, then silence or the tail | the best full shot of the hero or the product |

Track window: the drop (`drops[0].t`) at 12 s ± 1 s (55–65 %); the reveal on a downbeat 2 bars after the drop; the video ends 1–2 bars after the reveal, on the final hit or where the music cuts off. Other lengths: 12 s (6 bars) — hook 1, build 3, drop 1, outro 1; 30 s (15 bars) — hook 1, build 8 (two waves: cards and fragments, then acceleration), drop 3, outro 3.

## Rhythm
| part | shot length | cut grid | notes |
|---|---|---|---|
| hook | 1–2 s | a fragment for the whole bar | a card on top from beat 2 |
| build | 0.5–2 s | bars 2–3 — 2–3 beats + a dip with a card; bars 4–5 — 2 beats; bar 6 — 1 beat | dips to black on downbeats |
| drop | 0.25–0.5 s; a crash-zoom shot up to 1 s (flash stream — 1–2 frames per image) | a 1–2 s stream from the first beat; then every beat, half-beats on accents | the last beat of the drop is black |
| outro | 1.5–4 s | the reveal on a downbeat, the title on the last hit | the title stays ≥ 2 s, until the end of the video |

- Cutting pace: slow → faster → explosion → stop. Build steps: 1 shot per bar → 2 → 4; drop — maximum density; outro — one or two long shots. The contrast between the explosion and the still reveal is the genre's main effect.
- Pauses: dips to black between fragments in bars 2–5 (black 2–6 frames, with a card 1.3–1.9 s); 1/16 of silence (125 ms) before the drop; a black beat before the reveal.
- Inside a cut.flash stream the cuts follow frames, not beats — they do not count toward the share of cuts on the beat; the stream enters and exits on downbeats.

## Shot selection
Features: `scale`, `motion`, `sharp`, `luma`, `person` (person mask), object mask (`mask(...)` or `remove_background`), `face_share`. The main subject of the teaser (product, hero, event logo) is set by the user; if it is not set, take the most frequent person or object in the sources. Thresholds are percentiles P over the sources.

| slot | what goes there | criteria |
|---|---|---|
| hook | a mysterious fragment | `scale` extreme-close or a macro of the object; or a silhouette (figure ≤ 20 of 255 against a background ≥ 100); or a shadow; overall `luma` ≤ P40; the main subject cannot be recognized as a whole |
| build | parts and hints | the main subject's mask is cut by the frame edge by ≥ 30 % or hidden by shadow, an obstacle (dark foreground ≥ 40 % of the frame — frame.voyeur) or defocus; details of texture, hands, mechanism; shots with flickering light; `sharp` ≥ P50 on the detail |
| drop | energy without the reveal | `motion` ≥ P75; for the stream — 12–25 different images, where possible with an anchor (eyes, the object's center) at the same point of the frame ±5 %; the main subject only in motion or motion blur, never whole for longer than 2 frames |
| outro | the reveal | the main subject in full (mask inside the frame ≥ 95 %), lit (mask `luma` ≥ 100), `sharp` ≥ P70, centered (frame.central); best of all — a shot that contains the detail from the hook: then the pull-out links the beginning and the end |

- Hide until the outro: in hook, build and drop the main subject never appears in full and in full light (mask inside the frame ≥ 95 % and mask `luma` ≥ 100) for longer than 2 frames.
- Repeats: each segment once, except for a deliberate return: the fragment from the hook may come back in full in the reveal.
- Do not use: shots where the main subject is immediately and clearly visible (save them for the outro), funny moments, talking to the camera, third-party logos and screens, bright flat shots without shadows (intrigue lives in the dark).
- Vertical: crop to the detail, not to the whole — a tight frame works in a teaser's favor; the hook bars (4:5) hide the extras at the edges.
- No shot for the reveal (the product does not exist yet, the event is still ahead) — offer to generate a full shot of the hero or the product (edit-gen, with price confirmation) or reveal the name on black without a picture: type.title_card + a hit.

## Moves by part
**hook (0–2 s)**
- shot.extreme_close_up — a fragment of 1–2 s: the detail fills 50–100 % of the frame, static or a slow zoom-in ×1.04–1.12.
- light.silhouette — a backlit silhouette: figure ≤ 20 of 255, background 100–235; in code — a person mask, exposure −1…−1.5 stops, the figure pushed to almost black.
- light.shadow_play — a shadow instead of the hero, on a wall or on the ground.
- type.intertitle — a question card on top of the fragment from beat 2 (up to 4 words).
- fx.letterbox — the frame sits in a 4:5 band from the first beat (bars 14.8 % of the height each), optionally the bars slowly "creep in" at 0.03 of the height per second.

**build (2–12 s)**
- trans.fade — dips between fragments: fade out 2–4 frames, black 2–6 frames (with a card 1.3–1.9 s), fade in 4–6 frames; the darkest frame on the beat; ≤ 1 dip per bar.
- type.intertitle — 2–3 phrase cards on black on the downbeats of bars 2–5, the phrases escalate ("Did you see this?" → "Not quite." → "Soon.").
- shot.extreme_close_up, cut.insert — a series of 3–4 details of 2 beats each: texture, mechanism, eyes; an insert at ×2–4 from the previous shot.
- frame.voyeur — 1 shot "through a gap, a window or a fence", 1–2 s: a dark obstacle ≥ 40 % of the frame.
- light.flash — nervous flicker in bars 5–6: 2–4 light flashes in frame on the beats, no more than 3 per second.
- type.beat_text or type.kinetic (not both) — bar 6: 2–4 words on the beats or a 3-2-1 countdown, one digit per beat (≥ 0.35 s per digit), the digits shrink from 60 % of the width to 35 %.

**drop (12–16 s)**
- cut.flash — a stream from the first beat: 1–2 s, 12–25 different images of 2 frames each (12–15 changes per second), anchor at one point ±5 %, adjacent images matched in brightness (difference ≤ 0.1), no more than 3 large brightness changes per second; exit on a downbeat.
- trans.flash — white on the first beat (peak 2 frames, τ 60 ms), then 1 frame on hits: ≤ 3 per 10 s and no more than 1 per beat.
- cut.quick — after the stream: 4–8 pieces of a beat or a half-beat (0.25–0.5 s), close-up fragments of action.
- zoom.crash — once: a zoom-in ×3–4 over 8–12 frames into a detail, landing on the beat (in the "through the target" variant — a cut or a flash at the peak).
- cut.crash — once, optional: from silence into an explosion or from darkness into color, on a downbeat.
- cut.match — 2–3 shape rhymes on the beats: one shape (a circle, a silhouette, a line) in different shots — a hint at the whole.
- The last beat of the drop is black (a hard cut-off, 1 beat); the reveal comes out of it on a cut.

**outro (16–20 s)**
- zoom.out — the reveal: from the detail familiar from the hook to the whole: crop ×2–3 (4K) or ×1.5 (1080p) → ×1.0 over 2–3 beats (1–1.5 s), ease inQuad (accelerating toward the end): start on a downbeat, land on a beat.
- fx.letterbox — the bars open 4:5 → 9:16 over 1.3–1.5 s together with the pull-out: the frame literally "opens up".
- time.freeze — a freeze frame of the reveal under the title, 2–3 s (grain and light stay alive).
- type.title_card — the name on the last hit: a "slam" entrance ×1.5 → ×1.0 over 4–6 frames (outExpo) or a 0.15 s flash-in; the date and "soon" below it.
- gfx.counter — optionally a countdown timer to the date (tabular figures, linear), landing on a downbeat.
- trans.fade — black at the very end ≤ 0.3 s or a hard cut-off; the title stays visible until the last 0.3 s.

**Limits**
| move | limit |
|---|---|
| type.intertitle | ≤ 4 cards per 20 s; ≤ 1 per 2 bars; 0 in the drop |
| trans.fade | ≤ 1 dip per bar; total black ≤ 25 % of the video |
| cut.flash | 1 stream per video (2 in a 30 s video), ≤ 2 s |
| trans.flash + light.flash | together ≤ 3 per second and ≤ 6 per 10 s; red ones never in series |
| zoom.crash, cut.crash | 1 each per video |
| shot.extreme_close_up | a series of ≤ 4 details in a row, then a card, a dip or a different scale |

**Forbidden and why**
- gfx.callout — callouts and labels explain and reveal; a teaser must only promise.
- look.cheesy, fx.bobblehead, time.boomerang — comedy and irony break the tension of anticipation.
- trans.page, trans.iris — "childish" graphic wipes that cheapen the announcement.

Not forbidden, but not used: loop.end — a loop erases the final full stop with the name and the date; if an addictive looping cover is needed, that is a separate format, not a teaser of this genre.

**Signature moves from the cards.** The cards mark 29 signature moves for teaser. The signature has six: type.intertitle, trans.fade, shot.extreme_close_up, light.silhouette, cut.flash, type.title_card — the "hide → build tension → reveal" mechanics on any material. cut.insert, frame.voyeur, light.flash, type.beat_text, light.shadow_play, fx.letterbox, cut.quick, trans.flash, cut.match, cut.crash, zoom.out are in the parts. dolly.zoom, dolly.infinite, pass.through, zoom.infinite, zoom.extreme, scene.giant, time.bullet_time, anim.ai_video, type.vintage_title are in allowed: strong, but they require a special shot or a generation (time.bullet_time, anim.ai_video — only with the user's consent). sfx.impact, sfx.riser, sfx.sub_drop are in the `sfx` field.

## SFX
| part | sound | sync point | level vs music | limit |
|---|---|---|---|---|
| hook | sfx.impact "soft" or "punch" | attack on the first beat together with the fragment | −6…−10 LU | 1 |
| build | sfx.impact "soft" | the first frame of a card on black | −10 LU | together with the hook hit ≤ 3 per 10 s — no more than 2 cards get a sound |
| build | sfx.glitch, "click" variant | every countdown digit or every word on the beat | −14 LU | only within the visible series, ≤ 8 per second |
| build | sfx.riser | bar 6 (2 s), end = first beat of the drop with a 1/16 gap (125 ms) | −6 LU in the last 400 ms | 1 |
| drop | sfx.impact "punch" | attack on the first beat of the drop | −6 LU | 1 + 1 on the crash-zoom landing |
| drop | sfx.whoosh | the acceleration of a crash zoom or a crash transition, peak on the landing | −6 LU | ≤ 2 |
| outro | sfx.sub_drop + sfx.impact "boom" | attack on the last hit — the title appears | each 3 dB below its normal level: sub −9 LU, boom −5 LU | 1 pair |

- The video has a single main boom, on the reveal; the drop hit is a "punch" so that the reveal stays the strongest.
- Silence before the drop: the 1/16 gap after the riser — the music is muted for those 125 ms too (−60 dB), the hit and the music come back together.
- After the title: the music cuts off on the hit or tails off in ≤ 1.5 s; nothing new is heard.
- Ducking: under the boom and the sub drop the music goes −4…−8 dB in 25–150 Hz; glitch clicks sit on top of the music without ducking.
- Per 20 s video: hits ≤ 6, 1 sub drop, 1 riser, whooshes ≤ 2.

## Color
Direction: low key and cold — most of the frame in shadow, one accent color (the hero's or the product's color); in the reveal the light "switches on".

| parameter | hook, build, drop | outro (reveal) |
|---|---|---|
| mean frame brightness | 35–70 of 255 | +20…+40 % vs build |
| black point | P1 = 0–4 (deep crush) | P1 = 4–8 |
| white point | P99 = 200–240 (backlight highlights only) | P99 = 235–248 |
| contrast | spread P95 − P5 ≥ 0.65 | ≥ 0.70 |
| saturation | ×0.60–0.85, except one accent hue ×1.10–1.20 (selective by hue ±15°) | ×1.0–1.05, full color |
| balance | cold −400…−800 K or a monochrome tint (shadows 200–220°, 10–15 %) | neutral or the brand tint |
| vignette | 25–35 % | 10–15 % |

- The flash stream gets one tone for all images (a shared tint or monochrome), otherwise it strains the eye.
- Looks on request: look.dystopian (a concrete-gray world with one warm accent), look.vhs (a "found footage" teaser), look.film (an "old film" teaser, together with type.vintage_title).

## Text
Text cards are the teaser's second voice: a question, a hint, a time.
- Card (type.intertitle): up to 4 words, uppercase; a bold condensed or wide sans-serif; on black or over a dark fragment; one typeface per video.
- Size (9:16, H = 1920 px): a card line ≤ 76 % of the width (≤ 820 px); cap height 5–8 % H (96–154 px) for 1–2 words and 3.5–5 % H for 3–4 words in 1–2 lines; the question in the hook — 3.5–5 % H.
- Countdown (type.kinetic) and words on the beat (type.beat_text): one word or digit at 60–80 % of the width (no more than 16 % H), a stack — 7–10 % H per line.
- Title (type.title_card): the name at 70–76 % of the width (≈ 8–14 % H), the date and "soon" 3–4 % H, spacing 1.5 line heights; optionally a gfx.counter timer at 9–13 % H.
- Position: center x 0.47–0.50; cards and the title — block center y 0.42–0.50; everything within y 0.12–0.80, x 0.06–0.88; over a fragment — not on the detail being shown.
- Color: white #FFFFFF on black; an accent word or the date in the video's accent color; contrast ≥ 4.5:1.
- Animation: cards appear on a cut or over 4–6 frames and leave on a cut; words on the beat — a "slap" on the beat; the title — a slam ×1.5 → ×1.0 (outExpo) or a flash-in; nothing bounces or springs.
- Timing: a card 1.3–1.9 s (≥ 0.3 s/word + 0.5 s); a word on the beat ≥ 6 frames @25 fps / 8 @30 fps; a countdown digit ≥ 0.35 s; the title ≥ 2 s.
- Subtitles only if a spoken line is heard in the teaser: type.subtitles 3.5–4.5 % H, block at y 0.62–0.78.

## Quality checks
1. Grid: share of cuts on a beat or half-beat (±1 frame) ≥ 0.90, not counting the cuts inside the cut.flash stream; the first beat of the drop on `drops[0].t` ±1 frame; the reveal on a downbeat, the title on the beat of the last hit (±1 frame).
2. Concealment: in hook, build and drop the main subject is never visible in full and in full light (mask inside the frame ≥ 95 % and mask brightness ≥ 100) for longer than 2 frames.
3. Reveal: the first shot of the outro shows the main subject in full; the title is visible ≥ 2 s; the last frame is the title, the date or black after them (not a loop).
4. Cards: ≤ 4 words; ≤ 4 cards per 20 s; on screen ≥ 0.3 s/word + 0.5 s; cap height ≥ 3.5 % H, line ≤ 76 % of the width; contrast ≥ 4.5:1; no cards in the drop.
5. Flash stream: 1–2 s, ≥ 12 different images, repeats ≤ 15 %; adjacent images differ in brightness by ≤ 0.1; large brightness changes ≤ 3 per second.
6. Photosensitivity: brightness changes > 10 % over > 25 % of the area — no more than 3 per second across the whole video; red flashes no more than 1 per second.
7. Black (blackdetect d = 0.06 s, threshold 0.08): only the planned dips, cards, the beat before the reveal and the ending; ≤ 25 % of the duration in total.
8. Sound: −14 ±1 LUFS integrated, true peak ≤ −1.0 dBTP; the riser ends at the first beat of the drop minus 125 ms ±10 ms; short-term loudness at the reveal ≥ the build median + 4 LU.
9. Light: mean frame brightness in hook and build — 35–70 of 255; in the outro — 20–40 % higher.
10. Lengths: per-part medians within `shot_len_s` (±20 %); no shot longer than 5 s (the reveal with the freeze frame); build fragments ≤ 2 s.
11. Text: all blocks within y 0.12–0.80 and x 0.06–0.88; the title does not cover the main subject.
12. Repeats and faces: segments do not repeat (except the deliberate return of the fragment in the reveal); faces are not cut off by the crop (`face_issues` = 0).
