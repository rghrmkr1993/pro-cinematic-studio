---
genre: drama
slug: drama
kind: music
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–4 s (0–13 %)",   goal: "hook with emotion: a face in close-up and a line that asks a question; the viewer wants to know what happened"}
  - {part: build, t: "4–16 s (13–53 %)", goal: "story and tension: glances, details, a memory, a line of text; the music cuts out: silence before the hit"}
  - {part: drop,  t: "16–26 s (53–87 %)", goal: "climax: the hit after the silence, a speed ramp into slow motion on the key moment, realization on the face"}
  - {part: outro, t: "26–30 s (87–100 %)", goal: "aftermath and a full stop: a long shot, the bars close toward the eyes, the final line on black"}
rhythm:
  shot_len_s: {hook: [2.0, 4.0], build: [2.0, 4.0], drop: [0.5, 2.0], outro: [2.0, 4.0]}
  cut_grid: {hook: "the first shot runs until the downbeat of bar 2; cut on a downbeat", build: "once per bar or per 2 bars; cut on a downbeat or in a vocal pause; a line card on the last beat of a phrase; the last 1–2 beats: silence and black", drop: "the hit on the first beat after the silence; then every 2 beats, at the very peak every beat for no longer than a bar; the realization shot holds 1–1.5 bars", outro: "one shot per 1–2 bars; close to black on the last note, a line on black"}
  on_beat_share: 0.8
  max_shot_s: 5
moves:
  hook:  [shot.close_up, shot.extreme_close_up, zoom.slow, type.intertitle, trans.fade]
  build: [zoom.slow, cut.insert, focus.rack, frame.over_shoulder, trans.double_exposure, type.intertitle, trans.fade]
  drop:  [time.speed_ramp, time.slow_motion, shot.realization, shot.close_up, zoom.in, cut.insert, dolly.zoom]
  outro: [shot.wide, zoom.slow, fx.letterbox, trans.fade, type.intertitle]
  signature: [type.intertitle, trans.fade, time.speed_ramp, zoom.slow, shot.close_up]
  allowed: [angle.high, angle.overhead, angle.profile, anim.charcoal, dolly.in, dolly.double, dolly.float, rig.body_mount, focus.shallow, focus.split_diopter, focus.attention_shift, frame.two_shot, frame.voyeur, light.hard, light.spotlight, light.silhouette, reflect.mirror, time.freeze, trans.dissolve, fx.color_shift, fx.film_overlay, type.subtitles, type.credits]
  forbidden: [time.velocity, zoom.in_out, zoom.punch, time.boomerang, trans.lens_distort, trans.iris, trans.page, gfx.callout, look.cheesy, fx.bobblehead]
sfx: {hook: [], build: [sfx.impact], drop: [sfx.impact], outro: [sfx.sub_drop]}
looks: [look.film]
---

# Dramatic

## Goal and platform
A dramatic edit tells a moment from the hero's life like a scene from a film: a glance, doubt, a turning point, the aftermath. It rests on faces, pauses and silence, not on the number of cuts. Material: staged scenes, short films, music videos, relationships and breakups, loss, overcoming, the user's personal stories with close-ups.

- Platforms: TikTok, Reels, Shorts: 9:16, 15–60 s, typically 30 s; a horizontal 16:9 version follows the same rules with 2.39:1 bars.
- Music: slow piano and strings, ambient with a build, slowed-down lyrical songs; 60–100 BPM (the tables give seconds for 120 BPM). The track needs a climax: `drops[0]` or the transition into the section with the highest `energy`. A vocal line the viewer must hear is a reason for a pause in the edit, not for a cut.
- Neighbors: from epic, the world is small and the hero is big: close-ups instead of landscapes, silence instead of an orchestral hit; from calm, there is conflict, a turning point and dark, contrasty color; from teaser, the story is told to the end and nothing is held back; from motivation, there is no narrator voice: lines come as text or in the characters' own voices.

## Structure by seconds
A typical 30 s video at 120 BPM: beat 0.5 s, bar 2 s, 15 bars in total.

| part | time | bars | on screen | in the music | which shot |
|---|---|---|---|---|---|
| hook | 0–4 s (0–13 %) | 1–2 | a face in close-up or the eyes in extreme close-up, slow zoom-in; from 0.3–0.5 s, a line of text (a question or a confession); in bar 2, the second shot (a detail or the other person) | a quiet intro, a single piano line or a pad | the most emotional face in the video |
| build | 4–16 s (13–53 %) | 3–8 | the story: close-ups, over-the-shoulder shots, details of hands and objects, rack focus; one memory as a double exposure; one line card on black; at the end of bar 8, a cutoff: 1–2 beats of silence and black (or a freeze frame of the face) | the build-up; on the last 1–2 beats before the climax the music cuts out | glances, hands, objects, places of memory |
| drop | 16–26 s (53–87 %) | 9–13 | the hit on the first beat: a cut from black into the main action, a speed ramp into slow motion at the peak; the face at the moment of realization; details on beats | the climax, the music returns without a fade | the key moment of the story, then reactions in close-up |
| outro | 26–30 s (87–100 %) | 14–15 | aftermath: the hero alone in the space or a long close-up; the bars close toward the eyes; the final line on black | fade-out, the last note | the quietest shot: a wide with a lone figure or a still face |

Track window: the climax (`drops[0].t` or the start of the loudest section) goes at 16 s ± 2 s (50–60 %); the start is a downbeat 8 bars earlier, the end is the natural end of a phrase 5–7 bars later. If the track has no clear climax, take the transition "quiet section → loudest section" (`sections[].label` low → high).

Other lengths: ≈16 s (8 bars): hook 1, build 3, drop 3, outro 1 (a line card only in the hook and outro); 60 s: hook 0–8 s, build 8–32 s (two scenes with a chapter card on black between them), drop 32–52 s, outro 52–60 s.

## Rhythm
| part | shot length | cut grid | shots per bar |
|---|---|---|---|
| hook | 2–4 s | the first shot runs until the downbeat of bar 2 | 0.5–1 |
| build | 2–4 s (details 1–1.5 s) | every 1–2 bars, on a downbeat or in a vocal pause; a card on the last beat of a phrase | 0.5–1 |
| drop | 0.5–2 s | the hit on the first beat after the silence; then every 2 beats; at the peak every beat for no longer than a bar; the realization 1–1.5 bars | 1–4 |
| outro | 2–4 s | 1 shot per 1–2 bars, black on the last note | 0.5 |

- The editing pace stays slow for almost the whole video; it speeds up only at the peak of the drop (down to one beat per shot for 1 bar) and goes straight back to long shots. The sharp "long – short – long" contrast is the drama itself.
- Pauses: the "silence before the hit" lasts 1–2 beats (0.5–1 s) at the end of the build: music at −60 dB, black on screen (≤ 12 of 255) or a freeze frame of the face; the hit and the return of the music land exactly on the first beat of the drop. A line card on black: 1.5–2.5 s, in a pause in the music or on the last beat of a phrase.
- Cuts never split a vocal line in the middle and never fall on the stressed syllable of a character's line.
- Other tempos: on 60–80 BPM tracks, build shots last 1 bar (3–4 s) and the drop goes by the beat; at 100+ BPM, build shots last 2 bars.

## Shot selection
Features: `scale`, `face_share`, `face_h`, `motion`, `sharp`, `luma`, `cam`, `person`; facial expression: mediapipe face blendshapes (smile, wide-open eyes, raised brows). Thresholds are percentiles P over the user's sources.

| slot | what to place | criteria |
|---|---|---|
| hook | the most emotional face | `scale` close / extreme-close, `face_share` ≥ 0.8; eyes open, gaze past the camera or to the side; `motion` ≤ P50; the face is sharp (`sharp` over the face area ≥ P50); side light or low key (`luma` 40–110) |
| build | glances, details, relationships | alternate: close-up → detail (hands, an object) → over-the-shoulder or a two-shot → close-up; `motion` P20–P60; shots with a focus pull (sharpness moves between zones) get priority; for a memory, a bright, warm shot of a place or a person |
| build, end | the face before the hit | a close-up with minimal motion (`motion` ≤ P30), for the freeze frame in the silence |
| drop, first beat | the main action | a clear motion peak (`motion` ≥ P80 within a narrow window ≤ 0.5 s): a fall, a blow, a turn, a hug, a run, a door slam; ideally a source of ≥ 50 fps |
| drop, after that | realization and reactions | a close-up with a change of expression (the "wide-open eyes" score rises by ≥ 0.2 within the shot, or a shift from neutral to tense); details of the action |
| outro | aftermath | a wide with one figure (`person` ≤ 5 % of the area) or a still close-up (`motion` ≤ P30); dark (`luma` ≤ P40) |

- Repeats: the same close-up of the hero no more than 3 times and always at different moments; two shots of the same hero in a row only with a size jump of ≥ ×1.5 (otherwise it reads as a jump cut); each source segment is used once.
- Speech from the sources: 1–2 character lines, each ≤ 3 s, in music pauses or under ducking; a line with a clearly stressed word is placed with its stressed syllable on a downbeat.
- Do not use: laughing faces (except an intentional "before" ahead of the turning point), selfies and talking to the camera, flat daylight without shadows, shaky handheld footage without intent, shots with third-party logos and screens.
- Vertical: crop by `track(face)`, eyes at 0.33–0.40 of the height, look room in the direction of the gaze; a close-up from 1080p takes no more than a ×1.3 crop, beyond that upscale the fragment or use another shot.
- No suitable shot: the freeze frame in the silence can be made from any close-up; the realization shot can be enhanced in code (a push-in ×1.2–1.4 toward the eyes, face brightness raised ×1.3–1.6 through a mask, the background darkened); otherwise, offer to generate a close-up with consent.

## Moves by part
**hook (0–4 s)**
- shot.close_up / shot.extreme_close_up — the first frame: a face in close-up or the eyes; hold until the downbeat of bar 2.
- zoom.slow — ×1.05–1.15 over a 2–4 s shot (no faster than 0.3 %/frame @25 fps), centered on the eyes.
- type.intertitle — the first line over the face from 0.3–0.5 s: 3–7 words, a question or a confession; it runs across both hook shots until 3.5–4 s (≥ 0.3 s per word + 0.5 s) and does not cover the face on the second shot.
- trans.fade — open from black in ≤ 8 frames @25 fps / 9 @30 fps (or a hard entry).

**build (4–16 s)**
- zoom.slow — on all static shots ≥ 2 s, except details.
- cut.insert — a detail (hands, an object, the eyes) for 0.8–1.5 s: an axial insert ×1.3–2 (up to ×2.7 from 4K), the action phase matches across the cut; ≤ 1 per 4 s, then back to the face.
- focus.rack — shots with a focus pull: the focus snaps on a downbeat; 1–2 per build.
- frame.over_shoulder — confrontation and conversation: alternate over-the-shoulder shots of the two characters by phrase.
- trans.double_exposure — one memory, 2–4 s: a face + a place or a person; layer B at 35–60 % (lighten blend), the dark areas of the face are the window for the second shot; not on a downbeat.
- type.intertitle — one card on black, 1.5–2.5 s, in a pause in the music (≤ 1 per 8 s).
- trans.fade — fading into the card and out of it (0.3–0.5 s), and above all the silence before the hit: fade to black 4 frames before the pause, black for 1–2 beats, out with a hard cut on the first beat of the drop. Variant: instead of black, a time.freeze of the face for the same 1–2 beats.

**drop (16–26 s)**
- time.speed_ramp — on the main action from the first beat: fast ×1.5–2 → slow 0.3–0.4 at the peak (from 25/30 fps no lower than 0.4), hold 0.8–1.5 s, slowdown over 4–8 frames inOutCubic; ≤ 2 ramps per video, both only in the drop.
- time.slow_motion — emotional peaks (a tear, a hug, a glance) at 0.4–0.5, 1.5–3 s on screen.
- shot.realization — 2–3 s: a push-in ×1.1–1.3 toward the eyes, the expression breaks on a downbeat, face brightness ×1.3–1.6 by the end through a mask.
- shot.close_up — reactions of 1–2 s on a beat; no more than 3 close-ups in a row without a detail or a wide.
- zoom.in — a noticeable zoom-in ×1.3–1.6 over 1–1.5 s on a key face or object; ≤ 1 per 10 s.
- cut.insert — a detail of the action on a beat (a hand lets go, an object falls), 0.5–1 s.
- dolly.zoom — once per video, if the sources contain such a shot (or a "2.5D" imitation with a mask on the realization shot): 1.5–2.5 s, background ×1.3 or ×0.75.

**outro (26–30 s)**
- shot.wide — the hero alone in the space, 2–3 s (or a still close-up).
- zoom.slow — a slow zoom-out ×1.05 or a zoom-in toward the eyes as the bars close.
- fx.letterbox — closing on the eyes: the bars go from 9:16 to a slit over 2.6 s, anchored to the eye line `track(eyes)`, the bottom bar moves twice as fast as the top one; the slit closes into black.
- trans.fade — black holds to the end; the music fades to −60 dB over 1.5–2 s.
- type.intertitle — the final line on black, 1.5–2.5 s (a conclusion, an unanswered question, "a year later").

**Limits**
| move | limit |
|---|---|
| type.intertitle | ≤ 1 per 8 s (≤ 3 per 30 s, including the hook and outro); 0 in the drop |
| trans.fade | only for cards, the silence before the hit and the ending; ≤ 1 dip per 4 bars |
| time.speed_ramp | ≤ 2 per video, only in the drop |
| time.slow_motion | ≤ 35 % of the running time |
| trans.double_exposure | 1 per video (2 in 60 s) |
| zoom.in | ≤ 1 per 10 s; zoom.slow on every static shot ≥ 2 s |
| cut.insert | ≤ 1 per 4 s |
| dolly.zoom | ≤ 1 per video |
| flashes, shake | 0 (the hit after the silence works on its own) |

**Forbidden and why**
- time.velocity, zoom.in_out, zoom.punch — the on-beat pulse of viral and phonk: drama holds tension through stillness; an accent inside a scene is made with cut.insert or zoom.in.
- time.boomerang — a comedic "rubber band" that destroys the seriousness.
- trans.lens_distort, trans.iris, trans.page — graphic transitions; in drama, scenes change with a cut, a fade to black or a dissolve.
- gfx.callout — pointers and labels pull the viewer out of the story.
- look.cheesy, fx.bobblehead — irony and comedy.

**Signature moves from the cards.** The cards mark 29 signature moves for drama. The signature list holds type.intertitle, trans.fade, zoom.slow, shot.close_up and time.speed_ramp (its card lists it as "allowed", but a speed ramp at the climax is a declared trait of the genre, so we promote it). cut.insert, focus.rack, frame.over_shoulder, trans.double_exposure, shot.realization, zoom.in, dolly.zoom are placed in the parts. The camera and lighting moves (angle.high, angle.overhead, angle.profile, dolly.in, dolly.double, dolly.float, rig.body_mount, focus.shallow, focus.split_diopter, focus.attention_shift, frame.two_shot, frame.voyeur, light.hard, light.spotlight, reflect.mirror) are properties of the shot footage: the engine does not create them but uses them when they exist, so they are in allowed. anim.charcoal (a memory in charcoal) and type.credits (one card of 1–2 s at the end) are in allowed: they fit, but not in every video. sfx.impact is in the `sfx` field.

## SFX
| part | sound | point | level vs. music | limit |
|---|---|---|---|---|
| hook | — | — | — | ambience from the source (room, street, breathing) at −18…−24 LU |
| build | sfx.impact, "soft" variant | the first frame of a line card on black | −10 LU (−14…−8), only where the music is quiet | ≤ 1 per 8 s |
| drop | sfx.impact, "boom" or "stretched boom" | attack on the first beat after the silence, together with the return of the music | −2 LU (−4…0) | 1 |
| outro | sfx.sub_drop | the first black frame of the bars closing | −6 LU | 1 |

- Silence before the hit: `duck(music, to=−60 dB, t=[drop − 1…2 beats, drop])`, attack 10 ms; the music returns on the first beat without a fade, from the same point in the track (the grid does not shift). One sound from the source (a breath, a footstep, ticking) may stay in the pause at −20 LU.
- Ducking under the boom: music −3…−6 dB in 30–150 Hz, release 400 ms. Character lines: music −10…−12 dB under the voice (attack 50 ms, release 300 ms), the voice at −16…−18 LUFS short-term.
- Per video: hits ≤ 4, sub drop 1, no riser (the climax is built with silence, not with a rise), no whooshes or glitch sounds.

## Color
Direction: a muted, contrasty "film tone": cool shadows, warm skin, deep blacks, restrained highlights.

| parameter | value |
|---|---|
| contrast | S-curve +10…+20 %; brightness spread P95 − P5 = 0.60–0.75; in low key, up to 40 % of the area darker than 30 of 255 |
| black point | P1 = 2–8 of 255 |
| white point | P99 = 215–235, no clipping (≥ 250 on no more than 0.2 % of the area) |
| saturation | ×0.70–0.85 of the source; skin hue 18–28°, saturation no lower than 0.25 (the face stays alive) |
| balance | overall temperature −200…−400 K (cooler); shadows hue 200–215°, strength 6–10 %; highlights 35–45°, 3–5 % |
| memory | +300 K, saturation ×0.6, lifted blacks P1 = 18–25, level-2 grain (fx.film_overlay) |
| vignette | 20–30 % |

- The climax may go B&W (fx.color_shift: saturation → 0 over 0.5 s on a downbeat) and get its color back in the outro: "loss and hope"; no longer than 4 s on a face.
- Neighboring shots of one scene: ΔE of the mean colors ≤ 5, brightness difference ≤ 12 %.
- Look on request: look.film for a story that is entirely a memory.

## Text
Text lines are the main voice of the genre.
- A line (type.intertitle): up to 8 words (12 at most), up to 2 lines, a line ≤ 76 % of the width (≤ 820 px). Typeface: a serif or a thin sans-serif in lowercase; monospace for a message-style line. One typeface per video.
- Size (9:16, H = 1920 px): line height 3.5–4.5 % H (67–86 px); the final line up to 5 % H.
- Position: on black, center x 0.47–0.50, y 0.45–0.50; over a face, y 0.62–0.72 or 0.20–0.30, away from the face per its mask; everything inside y 0.12–0.80, x 0.06–0.88.
- Color: white or warm white #F4EFE6 on black without a shadow; over a shot, a shadow of 1–2 % H at 40–60 % or a 25–35 % darkening under the line; contrast ≥ 4.5:1.
- Animation: enters with a cut to the card, a 0.3–0.5 s fade-in over a shot, or letter-by-letter typing at 12–16 characters per second (a message-style line); exits in 1 frame or together with the scene. No bounces and no scaling.
- Sync: enters on a downbeat or on the last beat of a phrase; shown for ≥ 0.3 s per word + 0.5 s (typically 1.5–3 s); no text in the drop.
- Characters' speech: type.subtitles at 3.5–4.5 % H, semibold sans-serif, white with a 0.3 % H shadow, the block in y 0.62–0.78, up to 2 lines of 22–26 characters.
- Credits (type.credits, optional): one card of 1–2 s after the final line, 1–3 roles, 2–2.5 % H.

## Quality checks
1. Grid: share of cuts on a beat or half-beat (±1 frame) ≥ 0.80; the first cut of the drop on `drops[0].t` ±1 frame.
2. Silence before the hit: 0.5–1.0 s, mix loudness in the pause ≤ −50 dBFS (RMS), except one sound from the source at ≤ −20 LU; the picture in the pause is black (≤ 12 of 255) or a freeze frame; the end of the pause = the first beat of the drop ±1 frame.
3. Shot lengths: build median ≥ 2.5 s; outside the drop, no shots shorter than 1 s (except cut.insert details ≥ 0.8 s); no shot longer than 5 s.
4. Faces: the first hook shot has `scale` close or extreme-close; share of shots with close-up faces ≥ 40 %; faces not cut off by the crop (`face_issues` = 0).
5. Lines: ≤ 1 per 8 s; display time ≥ 0.3 s/word + 0.5 s; line height ≥ 3.5 % H; contrast ≥ 4.5:1; none in the drop.
6. Black (blackdetect d = 0.06 s, threshold 0.08): only the planned black (cards, the silence before the hit, the closing and the ending); ≤ 15 % of the duration in total.
7. Frozen frames (freezedetect ≥ 0.5 s): only the planned freeze frame in the silence and the final card.
8. Ramps and slow motion: ≤ 2 ramps, slow motion starts on a beat ±1 frame; from 25/30 fps, rate ≥ 0.4; slow motion ≤ 35 % of the running time.
9. Loudness: −14 ±1 LUFS integrated, true peak ≤ −1.0 dBTP; the short-term loudness of the first 2 s of the drop ≥ the build median + 4 LU.
10. Effects: no flashes or shake; brightness jumps of > 10 % over > 25 % of the area no more than 1 per second outside cuts.
11. Color: mean saturation ×0.70–0.85 of the sources; P1 2–8 (except the memory), P99 215–235.
12. Text in the safe zone: all blocks within y 0.12–0.80 and x 0.06–0.88; no block covers a face for longer than 0.5 s.
