---
genre: motivation
slug: motivation
kind: speech
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–4 s (0–13 %)",    goal: "the challenge: the voice's first phrase hits a sore spot or throws down a challenge, the words big on screen; the viewer recognizes themselves"}
  - {part: build, t: "4–16 s (13–53 %)",  goal: "the struggle: doubt, fatigue, the loneliness of the work; the voice builds pressure, the picture is dark and slow, the music grows"}
  - {part: drop,  t: "16–24 s (53–80 %)", goal: "the turning point: the track's drop hits in a pause in the voice, followed by the key phrase: decision, strength, movement; the most powerful shots"}
  - {part: outro, t: "24–30 s (80–100 %)", goal: "the call to action: a short final mantra, the hero small in a big world or at sunrise, a full stop"}
rhythm:
  shot_len_s: {hook: [1.5, 4.0], build: [1.5, 3.0], drop: [0.5, 2.0], outro: [2.0, 4.0]}
  cut_grid: {hook: "1–2 shots: the first cut on the downbeat of bar 2, or on the end of the voice's first phrase if it is within 0.25 s of the beat", build: "cutaways once per bar or every 2 beats (1–2 s), on beats; a cut within 0.25 s of the start of a key word is moved onto that word", drop: "the first downbeat of the drop: cut to the best shot (1–2 s, 2–4 beats); then every beat (0.5 s), at the peak half-beats for no longer than 1 bar, then a landing on a 1–1.5 s shot", outro: "1–2 shots of 2–4 s; the last one holds until the end of the final phrase + 1–2 bars and fades to black on the last note"}
  on_beat_share: 0.75    # cutaways are cut on music beats; the other cuts on the ends of voice phrases
  max_shot_s: 4
moves:
  hook:  [type.kinetic, light.silhouette, zoom.slow, shot.extreme_close_up]
  build: [type.karaoke, time.slow_motion, zoom.slow, shot.close_up, shot.extreme_close_up, cut.match]
  drop:  [type.kinetic, type.karaoke, angle.low, time.slow_motion, shot.realization, cut.quick, zoom.punch, trans.flash]
  outro: [type.karaoke, light.silhouette, shot.extreme_wide, type.title_card, trans.fade]
  signature: [type.kinetic, type.karaoke, time.slow_motion, angle.low, light.silhouette, zoom.slow]
  allowed: [drone.aerial, shot.wide, time.timelapse, time.speed_ramp, time.freeze, fx.color_shift, fx.letterbox, fx.film_overlay, look.film, light.haze, light.hard, light.spotlight, mask.double_exposure, trans.double_exposure, trans.dissolve, track.lead, dolly.in, address.direct, cut.jump, gfx.counter]
  forbidden: [fx.bobblehead, look.cheesy, anim.doodle_overlay, time.boomerang, trans.iris, trans.page, fx.talking_animal, look.weirdcore]
sfx: {hook: [sfx.impact], build: [sfx.riser], drop: [sfx.impact, sfx.sub_drop, sfx.whoosh], outro: [sfx.impact]}
looks: [look.film]
---

# Motivation

## Goal and platform
A 15–60 s video (typically 30 s) that charges the viewer up: a voiceover speaks in short, strong phrases about struggle
and decision, the music grows from a quiet intro to the drop, the picture moves from darkness and effort to motion and
light, and key words appear big on screen. Viewers should recognize themselves in the "struggle" and feel the push in
the "turning point". Platforms: TikTok, Reels, Shorts, 9:16 only. The voice is the user's recording or voice synthesis
and cloning (edit-voice); the cutaways are the user's footage (training, running, working at night, the city, nature);
missing wide shots are generated with consent.

How it differs from neighboring genres: from epic, the voice and the meaning of the phrases lead, not just the music;
from clips and UGC, the voice is off-screen, the hero's face is almost absent (viewers put themselves in the hero's
place), and cutaways are cut on beats; from dramatic, the ending is always bright, a call to action rather than silence
and a question; from phonk, there is no shake and no pulse on every beat: weight comes from slow motion and the angle.

## Structure by seconds
The part keys are kept, but in a speech genre they mean: **hook**: the challenge (the voice's first phrase and the words
on screen), **build**: the struggle, **drop**: the turning point (the track's drop + the key phrase + the most powerful
shots), **outro**: the call to action and the mantra. This is the only speech genre where the music sets the picture
grid: cutaways are cut on beats, text and voice on words. The voice is shifted to fit the music: the pauses between
phrases are stretched or squeezed by ±0.6 s (`vo_align` is a new primitive) so that the drop falls into a 0.4–1.0 s
pause in the voice and the key phrase starts 1–2 beats after the first beat of the drop.

| part | time (30 s, 120 BPM) | music and voice | on screen | which shot to use |
|---|---|---|---|---|
| hook | 0–4 s, bars 1–2 | a quiet intro (pad, piano, no drums); the first phrase starts ≤ 0.5 s in | 1–3 words big in the center, a dark silhouette or the eyes in extreme close-up, slow zoom-in | a silhouette in a doorway, the hero's back or the eyes; no full face |
| build | 4–16 s, bars 3–8 | the drums come in, tension grows; the voice talks about doubt and effort; the last bar builds up | effort in slow motion: hands, sweat, breathing, running in the dark, failing and getting back up; rhymes of one gesture on different days | low key, little color, close-ups and extreme close-ups of the details of effort |
| drop | 16–24 s, bars 9–12 | the drop in a pause in the voice, then the key phrase over the drop | the hero from below against the sky, the action peak in slow motion, the face at the moment of decision, a burst of peaks on beats, key words big | the best and most dynamic shot goes on the first beat of the drop; motion peaks on beats |
| outro | 24–30 s, bars 13–15 | the music resolves or fades out on the bar; the final mantra of 3–6 words | a small figure in a huge world, a silhouette at sunrise, a final word card, fade to black | an extreme wide shot or a silhouette against a bright sky |

Other lengths: 15 s: hook 0–2, build 2–7, drop 7–12, outro 12–15 s; 60 s: hook 0–4, build 4–32 (two waves of
"struggle" with a mini-rise), drop 32–48, outro 48–60 s. The drop always sits at 45–60 % of the length.

## Rhythm
- Cutaways: build: 1 shot per bar or per 2 beats (1–2 s), slow-motion shots up to 3 s; drop: the first shot 1–2 s (the
  hero from below or a peak in slow motion), then every beat (0.5 s), at the peak a burst on half-beats for no longer
  than 1 bar, then a 1–1.5 s landing; outro: 2–4 s per shot. At least 75 % of cuts land on a beat or half-beat
  ±1 frame.
- Voice and picture: cutaways do not interrupt the voice; a cut that falls within 0.25 s of the start of a key word is
  moved exactly onto that word, so a strong word gets a new picture. An on-camera speaker (if there is one) is cut on
  words, as in the speech genres.
- Voice: pauses > 0.6 s are shortened to 0.3–0.5 s (the voice needs air, so more pause remains than in clips), pace
  2–3 words/s; before the key phrase, a 0.4–1.0 s pause into which the drop hits.
- Curve: average shot 3 s in the hook → 2 s in the build → 0.8 s in the drop → 3 s in the outro; the motion energy in
  the frame grows toward the drop, and so does the brightness (see "Color").
- After the key phrase in the drop: 1–2 bars of music without the voice, where the montage of peaks does the work.

## Shot selection
1. Cutaway classes (VLM tags + ed_motion): "effort" (training, hands, sweat, breathing, working at night), "solitude"
   (an empty street, rain, an early wake-up), "failure" (a fall, a miss, fatigue), "peak" (a jump, a burst, lifting a
   weight, a finish, a strike), "open space" (wide and extreme wide shots, drone, horizon, sunrise), "face"
   (determination, realization).
2. Where things go: hook: a silhouette or a back (light.silhouette: the figure ≤ 20 of 255 on a bright background), the
   eyes in extreme close-up; build: "effort", "solitude", "failure": medium motion energy, low key (average brightness
   50–80 of 255); drop: "peak" with the highest motion energy (top 20 % by flow magnitude) and angle.low (sky or ceiling
   in the top 35 % of the frame, the hero's eyes ≤ 0.33 of the height), "face" with a break in expression, exactly
   once; outro: "open space", a silhouette at sunrise.
3. The best shot of the video (energy × sharpness × "heroism": low angle, backlight) goes on the first beat of the drop;
   the second strongest on the last beat before the mantra.
4. Few shots of the hero's face: viewers put themselves in the hero's place; a close-up of the face only at the moment
   of decision (shot.realization) and, if there is an on-camera speaker, on 1–2 phrases.
5. Slow motion: from 50–60 fps (×2–2.5 without synthesis), any peaks; from 25–30 fps, no deeper than ×2 via optical
   flow and not on complex occlusions (a crowd, a mesh, hair against a busy background).
6. Avoid: smiles and everyday humor in the build, third-party logos and brands on clothing and in gyms in close-up,
   shots with recognizable bystanders, bright, busy daytime shots in the build, repeats of one shot (each one used once,
   except a cut.match rhyme), three extreme wide shots in a row.
7. A class is missing (for example, a sunrise for the ending): find it in the sources by tags, otherwise generation with
   consent.

## Moves by part
**Hook.** type.kinetic — the first phrase, one to three words per screen, narrow uppercase sans-serif, pop ×0.9 → 1.07
→ 1.0 over 7 frames, a word 0.4–0.5 s, in the center; light.silhouette — a figure in a doorway or against a bright sky,
pushed further with the grade (exposure −1…−1.5 stops, black point +20…+30), 2–4 s; zoom.slow — a zoom-in ×1.08–1.2
over the whole shot, linear; shot.extreme_close_up — the eyes or the hands for 1–2 s with a zoom-in ×1.04–1.12. The
opening from black lasts no longer than 0.3 s.

**Build.** type.karaoke — the voice from the first phrase of the build: uppercase, narrow sans-serif 800, color change
only; time.slow_motion — ×0.4–0.5 on effort and failure, 1.5–3 s on screen, the motion peak at 40–70 % of the shot and
on a beat; zoom.slow — on every static shot longer than 2 s, ×1.08–1.15; shot.close_up and shot.extreme_close_up —
details of effort (hands, sweat, breathing, laces), a series of 3–4 at 0.5–1 s before the last bar of the build;
cut.match — one gesture or pose of the hero on different days and in different places, joined by match cuts on shape
(a series of 3–5 on beats): "I do this every day".

**Drop.** type.kinetic — 1–3 key words of the key phrase slammed in on the syllables, 0.4–0.5 s per word (the captions
are hidden for that time); type.karaoke — the rest of the voice's words; angle.low — the hero from below against the sky
on the first beat of the drop, 1–2 s; time.slow_motion — the action peak at ×0.4–0.5 as the first or second shot of the
drop, 1–2 s (in motivation, slow motion right on the drop is the norm), the peak on a beat; shot.realization — the face
at the moment of decision: a push-in ×1.2–1.4 toward the eyes, the light on the face ×1.3–1.6 toward the turning point,
once; cut.quick — a burst of peaks, 4–8 pieces on beats or half-beats for no longer than 1 bar, a 1–1.5 s landing;
zoom.punch — ×1.15–1.25 on the stressed words of the mantra, without motion blur, ≤ 1 per bar; trans.flash — one flash
with a tail (2-frame peak, τ 60 ms) on the cut into the drop, only if the cut falls into a pause in the voice.

**Outro.** type.karaoke — the final phrase; light.silhouette — a figure at sunrise or in a doorway of light;
shot.extreme_wide — the hero as a dot in a huge world, 3–4 s, a zoom-in or zoom-out ×1.05–1.1; type.title_card — the
final mantra word or a phrase of 1–3 words across 70–86 % of the width over the last shot or on black, fade-in 0.4–0.6 s,
1.5–3 s; trans.fade — fade to black over 1–2 s on the last note.

**Situational (allowed).** drone.aerial and shot.wide — open space in the hook and outro (no more than 2 aerial shots
in a row). time.timelapse — a sunrise, a city, "months went by", 2–4 s in the build. time.speed_ramp — one ramp on an
action peak (the slowdown on a beat of the drop). time.freeze — a freeze at the peak with one word. fx.color_shift — the
build in B&W, the color returns on the first beat of the drop over 1–1.5 s ("from darkness to light"). fx.letterbox —
2.35:1 bars slide in during the hook and leave on the drop; captions and text only inside the picture, the bars do not
cover the safe zone. fx.film_overlay and look.film — level 1–2 grain over the whole video, no dust over text.
light.haze, light.hard, light.spotlight — light from the sources (beams in a gym, a hard backlight, a spot on one
hero). mask.double_exposure and trans.double_exposure — the "inner world" in the build, once, 2–4 s. trans.dissolve —
a lyrical transition in the build, 0.8–1.5 s, not on a beat of the drop. track.lead — the hero walks toward the camera,
2.5–4 s (hook or outro). dolly.in — a real push-in from the sources instead of a digital one. address.direct and
cut.jump — if the speaker is filmed on camera: addressing the lens, pauses removed with jump cuts. gfx.counter — "365
days", "1% a day", landing on the end of the number word, once. Every move the cards mark as signature for motivation
is used in the parts.

**Limits.** Per 10 s: punches ≤ 3, cut.quick bursts ≤ 1. Per video: kinetic text ≤ 40 % of the running time (usually
the hook, the key phrase and the mantra), only one text layer at a time (kinetic text or captions); slow motion of all
kinds ≤ 50 % of the running time and no more than 2 slow-motion shots in a row without a change of shot size; flash: 1
(the entry into the drop), no strobe; shot.realization: 1.

**Forbidden.** fx.bobblehead, look.cheesy, anim.doodle_overlay, fx.talking_animal — comedic devices kill the pathos and
turn the call to action into a joke; time.boomerang — a "bounce" of a gesture reads as a meme; trans.iris and trans.page
— playful graphic transitions break the serious tone; look.weirdcore — deliberately creepy absurdity works against the
"light" of the ending.

## SFX
- hook: sfx.impact — a deep "boom" when the first big word appears (the boom variant, −8…−10 LU relative to the music):
  in the first frame before the speech starts or in a voice pause ≥ 150 ms, not over a word.
- build: sfx.riser — the last 1–2 bars before the drop, if the track itself does not build; cut off exactly on the first
  beat of the drop, −6 dB relative to the music by the end, under the voice no louder than −6 dB relative to its level.
- drop: on the first beat of the drop (in a pause in the voice), sfx.sub_drop (the classic 110 → 32 Hz, −6 LU relative
  to the music) or sfx.impact, not both at full level; sfx.whoosh on a ramp, a whip transition or a camera rush,
  −10…−14 dB.
- outro: sfx.impact — a final "boom" or a stretched hit on the mantra word at −8 LU, then the music tail and silence on
  black.
- The main hit: 1 per video (≤ 1 per 15 s); ≤ 6 synthesized sounds per 30 s in total.
- The music under the voice sits 8–12 dB below the voice (`duck(music, under=voice)`, attack 80 ms, release 400 ms);
  in voice pauses the music comes up by +6 dB; on the drop without the voice, full level.
- Voice: warm and close: HPF at 70 Hz, a slight +2 dB lift at 100–200 Hz, 3:1 compression, a de-esser, an optional
  short reverb (RT60 0.6–0.8 s, wet −18 dB); master −14 LUFS integrated, true peak ≤ −1 dBTP.

## Color
- Cinematic and dark in the build, brighter and warmer at the turning point: "from darkness to light".
- Build: contrast +15…+25 %, saturation −20…−35 % (or B&W via fx.color_shift), shadows toward teal (hue 180–200°,
  +4…+6 % saturation), average frame brightness 50–80 of 255.
- Drop and outro: saturation comes back to −5…−10 %, highlights warmer by +300…+500 K, average brightness 90–120 of
  255.
- Black point 2–6 of 255 (deep shadows, but no more than 1 % of pixels at 0), white point 235–245 with a soft shoulder;
  vignette 0.2–0.3; level 1–2 fx.film_overlay grain over the whole video.
- Silhouettes: the figure ≤ 20 of 255, the background 100–235, a separation of ≥ 2.5 stops; skin in the "face of
  decision" does not go gray (skin saturation no lower than −10 %).
- Consistency: neighboring shots of one part: average brightness ±10 %, ΔE ≤ 6; the grade changes only at a part
  boundary, on a downbeat.

## Text
- Font: a narrow extra-bold sans-serif 800–900, uppercase (covering the caption language, OFL); one typeface per video; color white
  #FFFFFF, one accent for the key word (#FFE14A or warm amber #FFB02E); a shadow instead of an outline on dark shots.
- Kinetic text (hook, drop, mantra): 1–3 words per screen, a word across 70–86 % of the width (≈10–14 % H), a two-line
  block 18–24 % H; center x 0.5, y 0.46–0.50; enters on the syllable 0–2 frames before the sound, pop over 7 frames; a
  word 0.4–0.5 s (no less than 0.3 s); exits with a cut to the next word.
- Captions (the build and the rest of the speech): uppercase karaoke, font size 4.6–5 % H, chunks of 1–3 words
  (uppercase is 15–20 % wider), center x 0.47, y 0.67 (block 0.58–0.78); the active word in the accent color; no
  bounce.
- Final card: 1–3 words across 70–86 % of the width over the last shot or on black, fade-in 0.4–0.6 s, 1.5–3 s, leaves
  together with the fade to black.
- 9:16 safe zone: top 12 %, bottom 20 %, right 12 %; all text in x 0.06–0.88 and y 0.12–0.80; with fx.letterbox,
  inside the picture.
- Sync: kinetic text follows the voice's word-level timestamps ±1 frame; kinetic text and captions never appear at the
  same time.

## Quality checks
| check | threshold |
|---|---|
| drop in a voice pause, `qa_drop_landing(event='voice_gap')` (new) | the first beat of the drop inside a voice pause ≥ 0.4 s; the key phrase starts 1–2 beats later ±2 frames |
| cutaways on a beat or half-beat (±1 frame), `cuts_on_grid_share` | ≥ 0.75 |
| best shot on the drop | the first shot of the drop is in the top 20 % by motion energy, a low angle or an action peak |
| kinetic text sync, `qa_sync(tol=1fr)` | ≥ 95 % of words within ±1 frame; a word ≥ 0.3 s |
| share of kinetic text | ≤ 40 % of the running time; one text layer at a time |
| text, `qa_text_safe_zone(layout='tiktok')`, `qa_reading_speed(max_cps=20)` | 100 % in the zone; ≤ 20 chars/s |
| slow motion | ≤ 50 % of the running time; from 25–30 fps no deeper than ×2, from 50–60 fps ×2–2.5 without synthesis |
| loudness | −14 LUFS ±1, true peak ≤ −1 dBTP; the voice ≥ 8 dB above the music during speech |
| brightness curve | the average brightness of the drop is higher than the build by at least 15 of 255 |
| flashes, `flash_guard` | ≤ 3 per second, no strobe |
| black frames | only the opening ≤ 0.3 s and the final fade to black; freezes > 0.5 s only for the planned freeze |
| length | 15–60 s; the ending fades to black on the last note |
