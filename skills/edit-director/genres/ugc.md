---
genre: ugc
slug: ugc
kind: speech
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 30}
structure:
  - {part: hook,  t: "0–3 s (0–10 %)",    goal: "the hook: a person talking to the camera names a pain point or a surprising result from the very first word; the product is in frame by second 3"}
  - {part: build, t: "3–10 s (10–33 %)",  goal: "the problem: a situation the viewer recognizes: what was annoying, what they tried, why it did not work"}
  - {part: drop,  t: "10–24 s (33–80 %)", goal: "solution and demo: the product in action, the result in close-up, before / after, the creator's genuine reaction"}
  - {part: outro, t: "24–30 s (80–100 %)", goal: "the call to action: what to do now and what the benefit is; the product in hand in frame, the call to action by voice and in text"}
rhythm:
  shot_len_s: {hook: [0.6, 2.0], build: [1.2, 3.0], drop: [1.0, 3.0], outro: [1.5, 4.0]}
  cut_grid: {hook: "the first word no later than 0.3 s; 2–4 jump cuts by phrase, pauses > 0.2 s removed; a punch on the first stressed word", build: "a cut at every removed pause > 0.25 s; a change of shot size or a cutaway of the problem every 1.5–3 s", drop: "cuts on words and on the actions of the demo; the result is one 1.5–3 s shot with no cuts inside; whip transitions in the pauses between phrases", outro: "the call to action in one or two shots of 1.5–4 s; the last frame: the product in hand and the call-to-action text, held ≥ 1.5 s after the last word"}
  on_beat_share: 0       # speech genre: cuts on words; the beats of the music bed are not used
  on_word_share: 0.95    # share of cuts in speech pauses, ±1 frame from the word boundary; none inside a word
  max_shot_s: 4
moves:
  hook:  [address.direct, type.karaoke, zoom.punch, cut.jump, lens.ultra_wide, gfx.callout]
  build: [type.karaoke, cut.jump, handheld.shaky, shot.medium_close_up, shot.close_up]
  drop:  [type.karaoke, cut.insert, pov.first_person, layout.split_screen, time.freeze, trans.whip, address.aside, zoom.punch]
  outro: [type.karaoke, address.direct, gfx.callout, gfx.counter]
  signature: [address.direct, cut.jump, type.karaoke, zoom.punch, handheld.shaky]
  allowed: [type.subtitles, address.lens_touch, angle.overhead_close, pov.object, pov.screen, pov.mirror, pov.dialogue, pov.animal, gfx.floating_ui, gfx.touch_gesture, layout.screen_life, trans.screen, trans.wipe, track.lead, time.fast_motion, time.boomerang, time.slow_motion, cut.quick, trans.flash, look.photo_prints, mask.bg_replace, scene.forced_perspective, anim.doodle_overlay, fx.talking_animal, loop.end]
  forbidden: [type.title_card, type.beat_text, sfx.riser, sfx.sub_drop, time.velocity, crane.telescopic, rig.robot_arm, fx.letterbox, fx.light_leak, glitch.pixel_sort]
sfx: {hook: [sfx.glitch], build: [], drop: [sfx.whoosh, sfx.glitch, sfx.impact], outro: [sfx.glitch]}
looks: []
---

# UGC

## Goal and platform
An ad that looks like a video made by an ordinary person: the creator talks into the phone about their problem and the
product that solved it, shows it in action and invites the viewer to do the same. Length 15–60 s, typically 30 s;
platforms TikTok, Reels, Shorts, 9:16 only. The main value is nativeness: the video must not look like an ad until the
viewer has watched through to the demo. The sound is on more often than in other genres, but captions are mandatory.

How it differs from neighboring genres: from product, there is no studio packshot, no sculpting light and no robot arm;
the product is in the hands of a real person in a real apartment; from clips, the video is shot as an ad and has a rigid
hook → problem → solution → call to action structure; from explainer, trust is built on a personal story and a reaction,
not on graphics; from viral, the hook is made with words, not with a trending visual trick.

## Structure by seconds
The part keys are kept, but in a speech genre they mean: **hook**: the hook line (a pain point, a result or a
controversial claim in the first phrase), **build**: the problem, **drop**: the solution and the product demo,
**outro**: the call to action. Part boundaries are the ends of phrases from the word-level timestamps of speech
recognition; the music is only a bed.

| part | time (30 s) | speech | on screen | which shot to use |
|---|---|---|---|---|
| hook | 0–3 s | "If you have…, watch this" / "Here's what happened after 2 weeks" / "Stop buying…"; the first word ≤ 0.3 s | the creator speaking into the lens, the product in hand next to the face or held out to the camera, hook text at the top, large captions, a punch on the stressed word | the best take of the first phrase with the gaze into the lens; a wide-angle selfie with the product close to the camera |
| build | 3–10 s | the problem in 1–3 phrases: what drove them crazy, what they tried, why it did not help | the creator in medium close-up and close-up, handheld cutaways of the problem (mess, failure, irritation) | honest everyday shots of the problem; the face on the emotions |
| drop | 10–24 s | "and then I found…", how to use it, what changed | a look into the camera after the result, before / after stacked top and bottom, a labeled freeze of the result, detail inserts, the product in action filmed first-person | the demo in action; the result large and sharp; a before / after pair from the same spot |
| outro | 24–30 s | the call to action: where to buy, a promo code or a benefit, "try it yourself" | the creator speaking into the lens with the product, a price sticker or "was → now", the call to action in words on screen | the call-to-action take with the liveliest intonation; the product in frame until the last frame |

Other lengths: 15 s: hook 0–2, build 2–5, drop 5–12, outro 12–15 s; 60 s: hook 0–3, build 3–15, drop 15–50 (2–3
demos, or a review + a demo), outro 50–60 s. The product appears in frame no later than second 3 at any length.

## Rhythm
- Speech: pauses > 0.25 s are shortened to 0.06–0.1 s, filler words and slips are cut; the pace after cleanup is 3–4
  words/s (a lively conversation, not a rattle), no higher than 4.5 words/s; keep some of the breaths between phrases:
  without them the creator sounds like an announcer.
- Cuts: in pauses, 2 frames after the end of a word, with a 10–20 ms audio crossfade; every second talking-head piece is
  ×1.15–1.2 on the face (a jump with a punch), no more than 6–8 alternations in a row.
- Density: a visual change every 1.5–3 s, never longer than 4 s without one; the hook is the densest (pieces of 0.6–2 s),
  in the drop the pace is steadier: the demo must read (an action shot of 1–3 s, not split up).
- Cutaways over the voice (B-roll of the problem and the demo) are J/L cuts: the voice is not interrupted, the picture
  changes at a word boundary.
- Before the result: a 0.3–0.5 s pause (do not cut it); the result is shown on the next word.
- Bed: a quiet rhythmic track without vocals; on the result it can be raised by +4 dB for 1–2 s, on the call to action
  brought back under the voice.

## Shot selection
1. Choosing takes: a phrase often has several takes; take the one with fewer slips and fillers (per the transcript),
   the gaze into the lens ≥ 80 % of the phrase time, livelier intonation (pitch and loudness spread above the median of
   the takes) and better sound (less echo and noise).
2. Talking head: front camera, the face 0.28–0.60 of the height (medium close-up) and 0.6–0.9 (close-up), the eyes at
   0.33–0.40; natural light on the face (skin 140–180 of 255); the background is real life (a room, a bathroom, a car),
   with no studio look.
3. Product: visible in the hook (≥ 3 % of the area in at least one frame of the first 3 s), in action and in hand in the
   demo, in hand next to the face in the call to action; the label turned to the camera in at least one shot.
4. Demo: first-person (hands entering from the bottom of the frame) or from the side; one action per shot; the result
   sharp, large and in good light.
5. Before / after: only a pair from the same spot with the same light (`find_same_setup`: scale 1.00 ± 0.03, offset
   ≤ 3 %); both pieces with identical color correction: pushing the "after" with the grade is forbidden, it fakes the
   result.
6. Problem cutaways: handheld, short (1–2 s), recognizable; no third-party brands and no faces of bystanders without
   their consent.
7. Avoid: studio-looking, overly "commercial" shots; shots where the creator reads from a screen (the gaze drifts to
   the side); a cropped product; third-party logos; echo and noise in the sound: such a take is worse even if the
   picture is better.
8. Repeats: each take is used once; the same shot size twice in a row only through a jump with a punch.

## Moves by part
**Hook.** address.direct — the first phrase into the lens; hook text in caption style at the top
(`text(hook, style='caption', anim='pop')`, 1.5–3 s), not a title card; type.karaoke — from the first word, larger
(5–5.5 % H) and with a bounce; zoom.punch — ×1.15–1.25 on the first stressed word, held until the end of the phrase, without motion
blur; cut.jump — 2–4 jumps by phrase; lens.ultra_wide — if there is a 0.5× selfie or the product is held right up to
the lens (1–2 s); gfx.callout — a "look here" arrow or circle on the product or the problem (drawn over 8–12 frames,
≤ 3 words).

**Build.** type.karaoke — only the active word changes color; cut.jump — pauses, slips, a jump with a punch;
handheld.shaky — the frame "breathes": do not stabilize selfie footage into dead stillness (`stabilize(0.3–0.5)`), on
tripod shots use the calm profile at 0.3–0.6 % of the frame; do not add it to an already shaky shot;
shot.medium_close_up — the backbone of the story, shot.close_up — on the "this drove me crazy" emotions (0.6–1.5 s).

**Drop.** cut.insert — a product detail when it is mentioned (texture, a button, the ingredients), 0.5–1.5 s;
pov.first_person — a hands-on first-person demo, 1.3–4 s (if longer, cut on the action); layout.split_screen — before /
after top/bottom (in 9:16 do not split left/right), 2–4 s, "before" and "after" labels at 2–3 % H; time.freeze — a
freeze on the result, 0.6–1.2 s, with a 1–2-frame white flash and a label stating the result; trans.whip — between demo
shots in speech pauses, a 4–6-frame blur window, ≤ 4 in a row; address.aside — a knowing look into the camera after the
product has worked, 0.3–1.6 s, once; zoom.punch — on a benefit word ("in 5 minutes", "no smell"). type.karaoke — the key
words of the result in a second color.

**Outro.** type.karaoke — the call-to-action word as the accent, chunks of 1–2 words; address.direct — the call to
action into the lens, the product in hand next to the face; gfx.callout — a price sticker by the product (rotated 4–8°,
bounce ×1.15, "−30%", "promo code"): data only from the user; gfx.counter — the price "was → now" instead of the
sticker, if the benefit in numbers matters (one of the two).

**Situational (allowed).** type.subtitles — a translation without word-level timestamps. address.lens_touch — a "grab
the camera and carry it over to show you" hook (once). angle.overhead_close — unboxing and "what's in the kit". Format
angles depending on the script: pov.object (the product "looks" at the creator), pov.screen (a reaction to an app),
pov.mirror (beauty, "get ready with me"), pov.dialogue (a "POV: you…" skit), pov.animal (pet products). Interfaces:
gfx.floating_ui (a message from a friend: "what's that product?"), gfx.touch_gesture (a swipe between "before" and
"after"), layout.screen_life (an app or an order on screen), trans.screen (a transition into the phone screen).
trans.wipe — a palm passes in front of the camera and swaps "before" for "after". track.lead — a walking monologue in
the hook. time.fast_motion — a routine at ×3–4 (1–3 s). time.boomerang — a satisfying looping gesture in the hook
(once). time.slow_motion — the product's texture at ×2. cut.quick — "getting ready" or a routine, 3–6 pieces of
0.3–0.6 s. trans.flash — a change of block, ≤ 1 per 10–15 s. look.photo_prints — results as a stack of photo prints.
mask.bg_replace — the creator against customer comments or a screenshot ("green screen"). scene.forced_perspective,
anim.doodle_overlay, fx.talking_animal — only for a humorous UGC skit, once each. loop.end — only if the call to action
stays on screen as a banner until the last frame. Every move the cards mark as signature for UGC is used: the basic ones
in the parts, the format ones (POV angles, interfaces, skit effects) in allowed, because they depend on the script and
the footage.

**Limits.** Per 10 s: punches ≤ 2 (≤ 1 per 3–6 s), callouts ≤ 2, whip transitions ≤ 3, flashes ≤ 1. Per video: a
freeze frame ≤ 1 per 15 s, a look into the camera (address.aside): 1, special effects from allowed: no more than 2
different ones.

**Forbidden.** type.title_card — a title card gives the ad away instantly and breaks the native feel (the hook is text
in caption style); type.beat_text — a second time grid fights the speech; sfx.riser and sfx.sub_drop — trailer sounds
come across as a TV commercial; time.velocity — breaks lip sync; crane.telescopic and rig.robot_arm — expensive studio
camera moves that a person with a phone does not have; fx.letterbox — "cinema" instead of a selfie, and it eats the
vertical frame; fx.light_leak — a film light leak over the face and the product; glitch.pixel_sort — melts the face and
the product.

## SFX
- Minimal: the creator's voice is everything; sounds only in speech pauses ≥ 150 ms and 14–24 dB below the voice.
- hook: sfx.glitch — a "pop" when the hook text or an arrow appears, −20…−24 dB.
- build: no synthesized sounds (live sound of the problem from the sources is allowed).
- drop: sfx.whoosh — a 0.15–0.3 s swish on whip transitions, peak on the cut, −18…−22 dB; sfx.glitch — a shutter click
  on the result freeze frame or a scratch on the look into the camera, −16…−20 dB; sfx.impact — a gentle "soft" when
  the result appears, −16…−18 dB, once.
- outro: sfx.glitch — a "pop" on the price sticker or the counter, −20 dB.
- Bed: `duck(music, under=voice)` 18–24 dB below the voice; no vocals. Limit: ≤ 5 sounds per 30 s.
- Voice: HPF at 70–90 Hz, noise reduction when the noise is above −55 dBFS, a de-esser, 3:1 compression, light
  room-echo reduction; master −14 LUFS integrated, true peak ≤ −1 dBTP.

## Color
- Native: minimal correction, as if shot on a good phone. Contrast 0…+5 %, saturation 0…+8 % (vibrance, skin
  protected), white balance neutral or slightly warm (+100…+300 K indoors), black point 2–6 of 255 (do not crush the
  shadows), white point 240–250; skin 140–180 of 255.
- Consistency: exposure on the face between pieces ±6 %, ΔE between neighboring pieces ≤ 6 (even out the phone's auto
  white balance).
- Before / after: identical correction on both pieces: correction difference ΔE 0.
- No looks, no film, no bars, no vignettes; the product's brand color ΔE ≤ 4 to the reference, if one is given.

## Text
- Karaoke (the base): a rounded sans-serif 800 (friendly), sentence case; font size 4.6 % H (4.2–5.5 %), in the hook
  5–5.5 % H with a ×1.12 bounce; chunks of 2–3 words (fast speech: 1–2), ≤ 2 lines, a line ≤ 76 % of the width; base
  #FFFFFF, the active word #FFE14A or a box under the word (one style per video), benefits and numbers #45F06B, ≤ 1 per
  chunk; outline #000 at 10 % of the font size; center x 0.47, y 0.67 (block 0.58–0.78), on a close-up face below the
  chin at 0.50–0.58. Timing: a chunk 2 frames before the word, the highlight 1 frame before, minimum 3 frames @25 fps /
  4 @30 fps.
- Hook text: ≤ 8 words, 1–2 lines, the same sans-serif at 4–5 % H, black text on a white box or white with an outline;
  center x 0.5, y 0.15–0.30; 1.5–3 s from the first frame.
- Price sticker and "was → now": a 5–7 % H sticker rotated 4–8°; the counter number ≤ 72 % of the width; next to the
  product, not on the face.
- "Before / after" labels: 2–3 % H in the corner of each half; the call to action: a chunk of 1–2 words in the accent
  color, 5–6 % H.
- Safe zone: top 12 %, bottom 20 %, right 12 % (platform buttons), everything in x 0.06–0.88; text does not cover the
  mouth, the eyes or the product label.
- Claims about results and figures come only from the creator's words or the user's data.

## Quality checks
| check | threshold |
|---|---|
| cuts inside a word, `qa_word_cuts` (new) | 0 |
| the first word, `qa_first_word` (new) | ≤ 0.3 s |
| product in the hook, `qa_product_presence(t=[0, 3])` (new) | product mask ≥ 3 % of the area in at least one frame of the first 3 s |
| call to action, `qa_cta(last_s=5)` (new) | the last 5 s contain a call to action by voice and in text, the product is in frame on the last frame |
| karaoke sync, `qa_sync(tol=1fr)` | ≥ 95 % of words within ±1 frame |
| text: `qa_text_safe_zone(layout='tiktok')`, `qa_overlap(face)`, `qa_reading_speed(max_cps=20)` | 100 % in the zone; 0 overlaps with the face; ≤ 20 chars/s |
| visual change, `qa_visual_change(max_gap=4.0)` (new) | ≤ 4 s without a change |
| before / after | scale 1.00 ± 0.03, offset ≤ 3 %, correction difference ΔE 0 |
| numbers, `qa_numbers(source=user_data)` | 100 % match the data |
| loudness | −14 LUFS ±1, true peak ≤ −1 dBTP; the voice ≥ 15 dB above the bed during speech |
| residual pauses, `qa_pauses` (new) | no pauses > 0.35 s, except the pause before the result ≤ 0.5 s |
| nativeness | no bars, no film textures, no title cards; no shake added on top of an already handheld shot |
| faces in frame, `face_issues` | 0 |
| length | 15–60 s; `cuts_on_grid_share` is disabled for the genre |
