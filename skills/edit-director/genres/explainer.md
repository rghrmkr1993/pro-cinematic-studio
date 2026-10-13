---
genre: explainer
slug: explainer
kind: speech
platforms: [TikTok, Reels, Shorts, YouTube]
format: {aspect: ["9:16", "16:9"], duration_s: [20, 90], typical_s: 45}
structure:
  - {part: hook,  t: "0–3 s (0–7 %)",     goal: "a question or a promise of the result, and right away a proof picture — the viewer understands what they will learn and why it matters to them"}
  - {part: build, t: "3–28 s (7–62 %)",   goal: "a step-by-step explanation: problem → cause → how it works; every claim is backed by a picture, a graphic or a detail"}
  - {part: drop,  t: "28–38 s (62–84 %)", goal: "the answer, the 'aha moment': the main conclusion, a number or a 'before / after' comparison — the strongest graphic in the video"}
  - {part: outro, t: "38–45 s (84–100 %)", goal: "a one-sentence summary and the next step for the viewer; a tie-back to the question from the hook"}
rhythm:
  shot_len_s: {hook: [1.0, 2.5], build: [2.0, 4.5], drop: [1.5, 4.0], outro: [2.0, 4.0]}
  cut_grid: {hook: "first word no later than 0.3 s; cuts only on word boundaries; the proof picture comes in on the word that names it", build: "a cut or a graphics change on a phrase or step boundary, every 2–4 s; pauses > 0.3 s are cut out, 0.2–0.4 s is left between steps so the graphic can 'settle'", drop: "a 0.3–0.5 s pause before the answer; the answer graphic starts 1–1.5 s before the result word and lands on its end; no cuts inside the answer", outro: "the summary line in one shot to camera, 2–4 s; ends on a sentence boundary, no 'bye'"}
  on_beat_share: 0       # speech genre: the grid is words and explanation steps; the beats of the music bed are not used
  on_word_share: 0.95    # share of cuts in speech pauses, ±1 frame from a word boundary; none inside a word
  max_shot_s: 5
moves:
  hook:  [address.direct, type.subtitles, cut.jump, zoom.punch, gfx.counter, cut.insert]
  build: [type.subtitles, cut.jump, shot.medium_close_up, cut.insert, gfx.callout, angle.overhead_close, layout.screen_life, type.lower_third]
  drop:  [type.subtitles, gfx.counter, zoom.punch, lens.magnifier, look.vfx_breakdown, type.margin_notes, type.kinetic]
  outro: [type.subtitles, address.direct, zoom.slow, loop.end]
  signature: [gfx.callout, gfx.counter, type.subtitles, cut.insert, zoom.punch, cut.jump]
  allowed: [type.karaoke, frame.interview, shot.close_up, anim.vector, gfx.mixed_media, parallax.photo, scene.archival, layout.split_screen, time.fast_motion, time.timelapse, time.slow_motion, time.freeze, trans.screen, pov.first_person, type.hand_drawn, type.intertitle, trans.fade, cut.match, look.news, fx.living_object]
  forbidden: [shake.beat, time.velocity, time.speed_ramp, fx.rgb_split, glitch.datamosh, trans.spin, light.flash, look.film, cut.stutter, sfx.sub_drop]
sfx: {hook: [sfx.glitch], build: [sfx.glitch, sfx.whoosh, sfx.riser], drop: [sfx.impact], outro: []}
looks: [look.news]
---

# Explainer

## Goal and platform
A 20–90 s video (typically 45 s) that explains one thing: how it works, why it is so, how to do it, what to choose.
The viewer should leave with one understood takeaway and the feeling "I got this faster than I expected". The core is the author's voice
(on camera or as a voice-over), and every second the picture helps understanding: a detail, a diagram, an arrow, a number, a screen recording.
Platforms: TikTok, Reels, Shorts (9:16) and YouTube (16:9 for the long version and for embedding). People often watch without sound —
the subtitles and labels carry the meaning on their own.

Differences from neighbors: vs clips — the video is built around a scripted explanation, graphics and inserts are mandatory; vs UGC —
it sells nothing, trust is built on clarity rather than on a personal story; vs product — a product can be the subject
of the explanation, but the rhythm is set by speech, not by the beat. Infographics, arrows, zooms and subtitles are the genre's signature.

## Structure by seconds
The part keys are kept, but in a speech genre they mean: **hook** — a question or a promise of the result with a proof
picture, **build** — the steps of the explanation (problem → cause → mechanism), **drop** — the answer and the "aha moment" (conclusion,
number, comparison), **outro** — a one-sentence summary and the next step. Part boundaries are phrase ends from the word-level timestamps
of the transcript; the music bed does not set the rhythm.

| part | time (45 s) | speech | on screen | which shot goes in |
|---|---|---|---|---|
| hook | 0–3 s | "Why…?" / "In 30 seconds I'll show you…" / a fact with a number; first word ≤ 0.3 s | the author to camera; right away an insert of the result or a big number; subtitles from the first word | face to the lens, medium close-up; the best shot of the result or the object |
| build | 3–28 s | 2–4 steps; each step has one claim and an example | talking head ≤ 50 % of the time, the rest — inserts, an overhead view of hands, screen recording, callouts, an expert lower third | every noun and action gets its own supporting shot; the head between steps |
| drop | 28–38 s | a 0.3–0.5 s pause, then the answer: conclusion, number, "before / after" | one main device by answer type: a counter or a chart, a magnifier on a detail, a layer breakdown, a calculation in notes; a punch-in on the key phrase | the clearest graphic or detail in the video; the author's face on the key phrase |
| outro | 38–45 s | a one-sentence summary + what to do (try it, save it, ask a question) | the author to camera, a slow zoom-in; ties back to the hook's question | a calm medium close-up to the lens |

Other lengths: 20 s — hook 0–2, build 2–12 (1–2 steps), drop 12–17, outro 17–20 s; 90 s — hook 0–4, build 4–60
(3–5 steps, each 10–15 s with its own graphic), drop 60–78, outro 78–90 s.

## Rhythm
- Speech rate after cleanup 2.5–3.5 words/s (slower than clips: the viewer is thinking); pauses > 0.3 s are shortened to
  0.1–0.15 s, filler words and slips are cut out; 0.2–0.4 s is left between steps — the graphic "settles".
- A visual change every 2–4 s (a cut, an insert, a new graphic, a framing change ×1.0 ↔ ×1.15–1.2); without a change — no
  longer than 5 s (a shot with an animating chart or counter may hold up to 5 s).
- Graphics start on the word that names them: a callout at the word's start frame minus 2 frames, a counter lands on
  the end of the number word, an insert or cutaway comes in on the first syllable of the noun; it holds ≥ 1.5 s + 0.3 s per word of the label.
- The voice runs continuously through inserts (J/L cuts), picture cuts fall on word boundaries; audio at the
  jump-cut joins — a 10–20 ms crossfade.
- Over the course of the video: the hook is dense (a change every 1–2.5 s), build is steady (2–4 s), the drop slows down — the answer holds as one
  shot or one graphic, the outro is calm.
- Music bed: instrumental, even, no sharp hits; in the drop it can be removed for 0.5–1 s before the answer and brought back on
  the summary.

## Shot selection
1. Main shot (A-roll): the author looks into the lens (address.direct) or at the interviewer (frame.interview), medium
   close-up (face 0.28–0.60 of the height, eyes at 0.36), even light, static camera; a take with slips — cut it out, do not
   cover it up.
2. Supporting shots (B-roll): each shot is tied to a word in the transcript — the noun or action is matched against
   the shot tags (VLM tagging of the sources); the cutaway comes in on that word and lasts 1.5–3 s (an insert of a detail of the same
   shot, cut.insert, is shorter, 0.5–1.5 s). No shot for an important word —
   a graphic (callout, counter, diagram) or a generation with the user's consent.
3. A hands-on process — overhead view (angle.overhead_close): a series of 3–6 inserts, one action each, the hands enter from the same
   side throughout the series (rotating the frame by 90/180° is allowed if there is no text on the objects).
4. Screen recording (layout.screen_life): crop to the relevant area — in 9:16 the whole screen is unreadable; key text after
   magnification ≥ 3 % H (zoom-in to the element ×1.5–2 over 1–1.6 s); one interface per scene; personal data and third-party logos
   must be covered or replaced.
5. Photos and archive: parallax.photo (2–5 layers, 3–5 s per photo), scene.archival — only the user's own materials or materials with
   cleared rights; never pass a generation off as a document.
6. Avoid: a busy background behind the author (no room for graphics), glare on glasses, shots with small unreadable text, B-roll
   "for looks" with no link to a word, blurred and dark pieces, repeating one B-roll shot more than 2 times.
7. Talking head — no more than 50 % of build time and 40 % of drop time; in hook and outro it is the basis.

## Moves by part
**Hook.** address.direct — the first line into the lens, face centered or on a third; type.subtitles — from the first word;
cut.jump — 1–2 jumps that cut out pauses and retakes; zoom.punch — ×1.15–1.2 on the key word of the question, held to the end
of the phrase, no blur; gfx.counter — if the hook is a number ("90 % of people…"): a big number counts up over 0.8–1.0 s and lands
on the end of the number word; cut.insert — the result or object the video is about, for 1–1.5 s right after the first line.

**Build.** type.subtitles — by phrase; cut.jump — pauses and slips, a framing change across a cut every 1–2 phrases;
shot.medium_close_up — the base shot of the head; cut.insert — a detail when it is mentioned, 0.5–1.5 s, ≤ 1 per 3–5 s, back to
the speaker; gfx.callout — a dot with a label, an arrow or an outline on an object at the moment it is named, ≤ 1 per 3–4 s,
≤ 2 on screen (9:16) / 3 (16:9), label ≤ 3 words; angle.overhead_close — hands-on steps; layout.screen_life — steps in
an app: cursor, taps, zoom-in to the element; type.lower_third — the expert's name and role 0.5–1 s after their first
shot, 3–5 s, once (in 9:16 — above the subtitles).

**Drop.** One main device by answer type, plus a punch-in on the key phrase. gfx.counter — a numeric answer or
a comparison: a number landing on the end of its word (count 1.0–1.5 s, outCubic, ×1.1 pulse on landing) or columns from a common baseline
(2–6, each grows in 0.6 s, one at a time); lens.magnifier — the answer is in a detail: a ×2 magnifier is guided to the finding and holds 1–2 s;
look.vfx_breakdown — "before / after": 2–3 layers, a line wipe of 0.8 s, each layer 1.5 s; type.margin_notes — a calculation
next to the author: numbers are written as they are spoken, old ones are crossed out, the result gets an arrow; type.kinetic — the conclusion
in 1–3 big words (0.4–0.5 s per word), the subtitles are hidden for that time; zoom.punch — ×1.2 on the first word of the conclusion,
held to the end of the phrase. type.subtitles — throughout the drop, except for the type.kinetic words.

**Outro.** type.subtitles; address.direct — the summary and the next step into the lens; zoom.slow — zoom-in ×1.05–1.1 over the whole summary
shot, linear; loop.end — a speech loop: the last line leads back into the hook's question (audio crossfade 20–50 ms). If
the ending needs a call to action with a caption — do not loop.

**As the situation calls for (allowed).** type.karaoke — instead of phrase subtitles in a short video that is almost all talking
head without graphics (neutral typeface at weight 700, lowercase, color change only). frame.interview — the expert interview format.
shot.close_up — an accent shot size in the alternation. anim.vector (generation, with consent) and gfx.mixed_media — a diagram or
"how the machine sees it" markup, as an insert ≤ 8 s. parallax.photo and scene.archival — history and context. layout.split_screen —
comparing options (in 9:16 — top/bottom only). time.fast_motion and time.timelapse — compress a process (1–4 s). time.slow_motion —
show a fast process (physics, a mechanism). time.freeze — a freeze with a "that's me" label at the start or on a step. trans.screen —
a transition into a phone screen when showing an app. pov.first_person — a tutorial "as the user sees it". type.hand_drawn —
a diagram or a word "handwritten on a board". type.intertitle — the step number and name ("Step 2"), 1.3–2.9 s. trans.fade — a chapter
change in a long video, on a speech pause, 0.3–0.6 s. cut.match — linking ideas (object → metaphor). look.news — the "news report"
format. fx.living_object — an object-guide that "explains" by itself. All moves that the cards mark as signature for explainer
are used; frame.interview, anim.vector, gfx.mixed_media and parallax.photo are in allowed because they depend on the format
and the material (interview, generation, archival photos).

**Limits.** Per 10 s: callouts ≤ 3, inserts ≤ 2, punch-ins ≤ 2 (and never two in one phrase), counters ≤ 1 (≤ 1 per 8–10 s).
Per video: magnifier and layer breakdown — 1 each, kinetic text ≤ 15 % of the running time. On screen at the same time — subtitles and
≤ 2 graphic elements in 9:16 (≤ 3 in 16:9), of which no more than one number or chart.

**Forbidden.** shake.beat, time.velocity and time.speed_ramp — shake and pulsing speed make graphics hard to read and
break the speech sync; fx.rgb_split and glitch.datamosh — color fringes and melting spoil text, lines and numbers; trans.spin — the rotation
pulls attention away from the idea; light.flash — blinking and strobe are tiring and hazardous over long speech; look.film — grain, dust and
jitter "eat" thin infographic lines and small text; cut.stutter — a repeated piece of speech sounds like a glitch; sfx.sub_drop —
a low rumble under the voice makes the delivery sound like a trailer and hurts intelligibility. For the same reason the other
moves that the cards mark as forbidden for this genre are off-tone too: tilted frame and camera rotation, dream, absurd and
psychedelic looks, transitions through liquid, shards and lens distortion, echo trail, bullet time, slit-scan, kaleidoscope.

## SFX
- The voice is the main layer; sounds are quiet and "UI-like", only in speech pauses ≥ 150 ms or on graphics.
- hook: sfx.glitch — one "tick" when the number or the first graphic appears, −20…−24 dB below the voice.
- build: sfx.glitch — a "pop" on the callout dot and ticks while counting (≤ 15 per second, sparser toward the end of the count), −22…−26 dB;
  sfx.whoosh — a short 0.15–0.3 s swish when a lower third flies in or on the transition to a screen recording, −20…−24 dB, ≤ 2 per 10 s;
  sfx.riser — 0.5–1 s in the pause before the answer, cut off on the first word of the answer, −6 dB below the voice level, once per video.
- drop: sfx.impact — a gentle "soft" or a "ding" on the number landing or on the result of the breakdown, −14…−18 dB, once.
- outro: no sounds.
- Music: the bed sits 20–26 dB below the voice (`duck(music, under=voice)`), no vocals and no percussive accents; limit —
  ≤ 6 sounds per 30 s.
- Voice: high-pass filter 70–90 Hz, de-esser, 3:1 compression, noise reduction when the noise is above −55 dBFS; master −14 LUFS integrated,
  true peak ≤ −1 dBTP.

## Color
- Neutral and readable: contrast +5…+10 %, saturation 0…+5 %, neutral white balance (grays within ±2 in a*, b*),
  black point 4–8, white 240–248 of 255; natural skin.
- Screen recording — no grade; only map the 16–235 range → 0–255 and remove moiré.
- Graphics: one palette per video — white text, a dark #000 backing at 50–60 % or darkening the frame by 30–50 % under a number,
  one accent (#FFC400 by default or the topic's color), green #2BD96B / red #FF4D4D only for "rise / fall" with
  a sign; contrast ≥ 4.5:1.
- Consistency: A-roll exposure between takes ±5 %, ΔE of adjacent pieces from the same camera ≤ 3.
- No looks; look.news only as the "news report" format with a made-up package of lower thirds.

## Text
- Font: one sans-serif (covering the caption language, OFL), 500 / 700, tabular figures; a handwritten font only for type.margin_notes and
  type.hand_drawn. Colors — see "Color".
- Subtitles (the core): 9:16 — font size 3.8–4.5 % H, chunks of 3–6 words, ≤ 2 lines of 22–26 characters, 0.8–2.5 s, block at y 0.62–0.78;
  16:9 — font size 4.5–6 % H, ≤ 2 lines of 42 characters, baseline at 0.90–0.93 H. White with a 0.3 % H outline; reading speed
  ≤ 17 characters/s.
- Callouts: 9:16 — 2.2–2.8 % H, ≤ 18 characters per line; 16:9 — 2.8–3.6 % H, ≤ 24 characters; ≤ 2 lines.
- Counter: 9:16 — the number ≤ 72 % of the width (≈9–13 % H), center x 0.47, y 0.32–0.55; 16:9 — 18–30 % H (typically 24 %),
  label 3–4 % H. Format: a narrow no-break space as the thousands separator from 5 digits, a decimal comma, "45 %", minus sign U+2212.
- Margin notes: 16:9 — line 4–7 % H, block 26–36 % of the width on the side opposite the face; 9:16 — line
  3.5–5 % H, block 60–76 % of the width in a free strip above or below the author.
- Expert lower third: 9:16 — name 3.2 % H, role 2.1 % H, above the subtitles (y 0.48–0.60) or in the top strip 0.13–0.24;
  16:9 — 4.5 % H / 3 % H, block bottom ≤ 0.78 H when there are subtitles.
- Key words: 9:16 — 1–3 words across 70–86 % of the width; 16:9 — a phrase at 9–14 % H; center y 0.46–0.50.
- Magnifier in 9:16 — diameter 0.7–0.85 of the frame width (in 16:9 — 0.6–0.9 H).
- Zones: graphics in the y 0.20–0.58 strip, subtitles in 0.62–0.78, so they do not collide; 9:16 safe zone — top 12 %,
  bottom 20 %, right 12 %; 16:9 — margins ≥ 5 %. Graphics do not cover the author's face.
- Sync: see "Rhythm"; numbers and facts only from the user's script or speech; when in doubt, check with the user.

## Quality checks
| check | threshold |
|---|---|
| cuts inside a word, `qa_word_cuts` (new) | 0 |
| first word, `qa_first_word` (new) | ≤ 0.3 s |
| graphics-to-word sync | callout: word start −2 frames (±2 frames); the counter lands on the end of the number word ±1 frame |
| graphics hold | ≥ 1.5 s + 0.3 s per word of the label |
| numbers, `qa_numbers(source=user_data)` | 100 % match the data or the speech |
| subtitles: `qa_reading_speed(max_cps=17)`, `qa_text_safe_zone`, `qa_overlap(face)` | ≤ 17 characters/s; 100 % inside the zone; 0 overlaps with the face |
| on screen at once | subtitles + ≤ 2 graphic elements in 9:16 (≤ 3 in 16:9), no more than one number or chart |
| small text, `qa_text_size(min_h=0.03)` (new, OCR) | key text in frame ≥ 3 % H in 9:16 |
| visual change, `qa_visual_change(max_gap=5.0)` (new) | ≤ 5 s without a change |
| talking head in build | ≤ 50 % of the part's time |
| callout jitter, `qa_track_jitter` | ≤ 0.2 % of the width per frame |
| loudness | −14 LUFS ±1, true peak ≤ −1 dBTP; voice ≥ 20 dB above the bed during speech |
| black and frozen frames | no black frames (except a planned chapter fade); a freeze > 0.5 s only for a freeze frame or a chart; `cuts_on_grid_share` is disabled for this genre |
| length | 20–90 s; ends on a sentence boundary |
