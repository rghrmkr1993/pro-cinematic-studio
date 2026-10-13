---
genre: clips
slug: clips
kind: speech
platforms: [TikTok, Reels, Shorts]
format: {aspect: ["9:16"], duration_s: [15, 60], typical_s: 35}
structure:
  - {part: hook,  t: "0–3 s (0–9 %)",     goal: "the hook: the strongest line or reaction of the excerpt plays from the first frame, the headline promises why it is worth watching to the end"}
  - {part: build, t: "3–22 s (9–63 %)",   goal: "the setup: who is speaking and what the argument or story is about; no pauses and no filler, tension rises toward the payoff"}
  - {part: drop,  t: "22–31 s (63–89 %)", goal: "the payoff: the punchline, the main point, a number or a reaction — the moment the clip was cut for"}
  - {part: outro, t: "31–35 s (89–100 %)", goal: "the tag: a short line or reaction with no goodbyes; the end joins the start in a loop"}
rhythm:
  shot_len_s: {hook: [0.8, 2.0], build: [1.5, 4.0], drop: [1.0, 3.0], outro: [1.5, 3.5]}
  cut_grid: {hook: "the first word no later than 0.3 s after the first frame; cuts only in pauses and at word boundaries; 1–2 jump cuts", build: "a cut at every removed pause > 0.25 s and at every change of thought; a shot-size change (medium close-up ↔ close-up) every 1–2 phrases, 2–4 s; inserts no more often than 1 per 3–5 s", drop: "the pause before the punchline is kept at 0.3–0.6 s; the punchline is one shot with no cuts inside the phrase (a phrase longer than 4 s gets a punch-in inside the shot instead of a cut); the reaction — a cut 0.2–0.4 s after the end of the phrase", outro: "the tag 1.5–3.5 s; the last cut on a word boundary so that the seam with the first frame has no pause > 0.3 s"}
  on_beat_share: 0       # speech genre: cuts follow the words, the beat grid does not apply (music is only a bed)
  on_word_share: 0.95    # share of cuts in speech pauses, ±1 frame from the word boundary; none inside a word
  max_shot_s: 4
moves:
  hook:  [type.karaoke, type.intertitle, shot.close_up, zoom.punch, cut.jump]
  build: [type.karaoke, cut.jump, zoom.punch, shot.medium_close_up, type.lower_third, cut.insert]
  drop:  [type.karaoke, zoom.crash, zoom.punch, type.kinetic, time.freeze, address.aside]
  outro: [type.karaoke, shot.close_up, zoom.punch, loop.end]
  signature: [type.karaoke, cut.jump, zoom.punch, zoom.crash, type.lower_third]
  allowed: [type.subtitles, frame.interview, address.direct, layout.split_screen, layout.windowbox, cut.quick, cut.vector_match, gfx.callout, gfx.counter, time.slow_motion, trans.flash, trans.whip]
  forbidden: [type.beat_text, time.velocity, trans.lens_distort, glitch.pixel_sort, glitch.datamosh, fx.light_leak, trans.dissolve, frame.tableau]
sfx: {hook: [sfx.glitch], build: [sfx.whoosh, sfx.riser], drop: [sfx.impact, sfx.glitch], outro: []}
looks: []
---

# Clips

## Goal and platform
A short vertical clip of 15–60 s (typically 35 s) cut from a long video — a podcast, an interview, a stream, a
lecture, a vlog, a talk. The task is to pull out one complete moment (a story, an argument, a tip, a joke, a strong
statement) and package it so that a person with no context stops, understands within 3 s what it is about, and watches
to the payoff. Platforms: TikTok, Reels, Shorts, 9:16 only. People often watch without sound — subtitles are
mandatory. Versions in other languages are made by swapping the subtitle layer or by dubbing (edit-voice); the edit
does not change.

Differences from the neighbors. Unlike UGC, the footage was not shot for the clip: the speaker talks to another person
rather than selling to the viewer; there is no ad structure. Unlike an explainer, there is no script and no
infographics as the backbone; what matters is live speech and reactions. Unlike motivation, it shows the speaker on
camera in sync, not a voice-over over cutaways. Unlike viral, it is cut by words rather than by the beats of a track,
and it is carried by the meaning of the excerpt rather than by trending moves.

## Structure by seconds
The part keys are the same as in the music genres, but their meaning is speech-based: **hook** — the hook (the
strongest line or reaction from the first frame; often 1–3 s taken from the payoff — a "flash-forward"), **build** —
the setup and context, **drop** — the payoff (the punchline, the main point, a number, the other person's reaction),
**outro** — the tag and the loop seam. Part boundaries are phrase ends taken from the word-level speech recognition
timestamps, not the beats of a track; music, if there is any, is only a bed.

| part | time (35 s) | speech | on screen | which shot we use |
|---|---|---|---|---|
| hook | 0–3 s | the first line is a question, a number, a sharp statement or a reaction; the first word ≤ 0.3 s | the speaker in close-up, the headline at the top, large karaoke captions with a bounce, a punch-in on the first stressed word | a close-up of whoever says the strongest line; with a flash-forward — 1–3 s of the payoff or the reaction |
| build | 3–22 s | the story or the argument without pauses, filler words or repetitions | jump cuts with shot-size changes, a name lower third for 2–4 s, occasional inserts of what is being talked about | a medium close-up of the speaker as the base, a close-up on accents; the other person only for reactions |
| drop | 22–31 s | a 0.3–0.6 s pause before the punchline, the whole punchline, the reaction (laughter, silence, "no way") | a punch-in or a crash zoom onto the face, 1–3 key words in large type, a freeze frame on the reaction, a look into the camera | the speaker's face at the moment of the punchline; the other person's best reaction |
| outro | 31–35 s | one short tag line or a laugh; no spoken "subscribe" | a close-up of the reaction, a reverse punch on the last word, the seam with the first frame | a reaction or a last line that leads into the first one |

Other lengths: 20 s — hook 0–2, build 2–11, drop 11–17, outro 17–20 s; 60 s — hook 0–3, build 3–42 (with 2–3
mini-payoffs inside, 1 accent each), drop 42–55, outro 55–60 s. Flash-forward: 1–3 s of the strongest line from the
payoff go first, then a hard cut back to the start of the story; the whole punchline is never moved into the hook — it
plays in full in the drop.

## Rhythm
- Speech cleanup: pauses > 0.25 s are shortened to 0.08–0.12 s (2–3 frames of "breath"); filler words ("uh", "um",
  "well", "sort of", "anyway", "like") and stumbling repeats are cut if they are ≥ 0.15 s and the cut does not break
  the phrase; the resulting pace is 2.8–3.8 words/s, no higher than 4.5 words/s — over-compressed speech sounds
  robotic.
- Keep: the 0.3–0.6 s pause before the punchline, the 0.5–1.2 s laugh after it (trim at the peak), one dramatic pause
  ≤ 0.8 s per video.
- Cuts: in a pause, 2 frames after the end of a word; audio — a 10–20 ms micro-crossfade on every seam. A change of
  speaker — a J/L cut: the next speaker's voice starts 4–8 frames before their picture (or the picture switches to the
  active speaker with a 3–6 frame delay).
- Density: a visual change (a cut, a shot-size change, an insert, graphics) at least once every 4 s; in the build —
  every 2–4 s; in the drop the pace slows down — the punchline holds in one shot to the end of the phrase.
- Music: optional, an instrumental bed without vocals; cuts are not tied to the beats; at the payoff the bed drops
  almost to zero (−30 dB from its own level) 0.3–0.6 s before the punchline and comes back after the reaction; the
  video ends on a downbeat of the bed where possible.

## Shot selection
1. Finding the moment in a long video (`clip_candidates` — a new primitive, working from the transcript and the
   audio): 15–60 s windows that start at the beginning of a sentence and make sense without the preceding context (the
   first line has no "and that's why", "as I said before", or "he" without saying who), and end at the end of a
   sentence with falling intonation.
2. Hook score (the first line of the window or a flash-forward candidate): a question, a number, a sharp or
   controversial statement, emotional words, loudness 2–4 dB above the median, a burst of speech rate, a laugh or a
   reaction right after. Payoff score: after the line — a laugh, a pause ≥ 0.4 s or the other person's reaction;
   summing-up words ("the main thing", "that's why", "in the end"), a stated number. Window total = hook × payoff
   × speech density (share of silence < 15 %) × face visibility. Overlapping windows (IoU > 0.3) — keep the best one.
3. Picture: the active speaker (`active_speaker` — new: lip movement from the mediapipe face mesh, correlated with the
   voice envelope) → a 9:16 crop on them. Base — a medium close-up (face 0.28–0.60 of the height, eyes at 0.36),
   accent — a close-up (face 0.6–0.9, eyes at 0.33). From 16:9 1080p the vertical crop is already ×1.78 — on top of
   that a punch-in ≤ ×1.2 is acceptable; a close-up only from 4K or with upscaling.
4. Two people in conversation: when both faces are needed at once (an argument, a reaction) — layout.split_screen
   top/bottom at 50 % each; if the faces in the source are more than 0.5 of the width apart and the crop cuts one of
   them — layout.windowbox (a full-width 16:9 window, the headline above it, subtitles below it). The listener's
   reaction — ≤ 1.5 s, only on the punchline and on laughter.
5. Avoid: a face touching the edge of the crop (`face_issues` = 0), a hand at the mouth, looking at notes or a phone
   for longer than 2 s, interruptions and two voices talking at once, small slides and screens (use a zoomed insert or
   a callout instead), blurry and dark pieces where the face cannot be read.
6. Inserts (cut.insert) — from the same video: an object, a screen or a gesture named in the speech (by a noun from
   the transcript), 0.8–1.5 s, the voice runs on without a break.
7. Repeats: the same crop for no more than 2 pieces in a row; shot-size alternation no more than 6–8 times in a row,
   then an insert or a reaction.

## Moves by part
**Hook.** type.karaoke — larger than usual (font size 5–5.5 % H) with a ×1.12 bounce on the active word;
type.intertitle — a hook headline over the first shot (a question or a statement of ≤ 7 words) in the top band; it
stays for the whole hook, 2.5–3 s, and leaves with a cut at a word boundary (the "topic" variant stays to the end of
the video); shot.close_up — open on a close-up of the face (from 4K or with upscaling; on 1080p — a medium close-up
and a ×1.2 punch-in); zoom.punch — ×1.15–1.25 on the first stressed word, held to the end of the phrase, no blur;
cut.jump — 1–2 jumps that remove pauses.

**Build.** type.karaoke — calmer: only the active word changes color; cut.jump — a "jump with a punch-in": every
second piece at ×1.15–1.2 on the face (less than ×1.15 reads as a mistake), pieces of 1.5–4 s following the phrases;
zoom.punch — on stressed words and numbers, ≤ 1 per 3–6 s and never two in one phrase; shot.medium_close_up — the base
shot; type.lower_third — the speaker's name and role 0.5–1 s after their first shot, in a speech pause, 3–5 s, once
per person (in a long clip — the "section topic" variant above the subtitles); cut.insert — the detail being talked
about, 0.8–1.5 s, ≤ 1 per 3–5 s.

**Drop.** zoom.crash — on the reaction or the "realization" after the punchline: ×2.5–3 from a medium close-up to the
eyes over 8–12 frames @25 fps (10–14 @30 fps), radial blur in the middle of the move, a hard landing in the pause
after the line; the total magnification from the source pixels comes to ×4–5, so on a 1080p source — upscale the
excerpt (upscale_video, with consent); without it the crash zoom is replaced with a ×1.25 punch-in + sfx.impact; once
per clip.
zoom.punch — an alternative to the crash zoom on the punchline itself: ×1.2–1.25 on the first word, held to the end of
the phrase.
type.kinetic — 1–3 key words of the punchline in large type in the center, 0.4–0.5 s per word, a pop-in over 7 frames;
the karaoke line is hidden for that time. time.freeze — a freeze on the reaction for 0.6–1.2 s with a 1–2 frame white
flash, a slight push-in ×1.05–1.1 and an optional caption; never mid-word. address.aside — if the source has the
speaker glancing into the camera after the punchline (0.3–1.6 s), place it right after the line; if not, do not fake
it. One main move per punchline: the crash zoom or the freeze, not both.

**Outro.** type.karaoke — the last line; shot.close_up — the reaction or the laughter in close-up; zoom.punch — a
reverse punch ×1.2 → ×1.0 on the last word (an "exhale"); loop.end — a speech loop: the final line is trimmed so that
the first line of the hook completes it; the music is cut on a bar, audio crossfade 20–50 ms. If the ending needs a
call to action or a link to the full version — do not loop; show a caption in the last 2 s instead.

**Situational (allowed).** type.subtitles — phrase-level subtitles without highlighting: a translation without
word-level timestamps, a calm interview tone, a video for a 16:9 platform. frame.interview — a normal base for a clip
from an interview (looking at the interviewer is not a mistake). address.direct — if the speaker addresses the viewer.
layout.split_screen (top/bottom only) and layout.windowbox — a conversation between two people, see "Shot selection".
cut.quick — the hook of a compilation: 3–5 reactions of 0.3–0.5 s before the main excerpt, once. cut.vector_match — a
run of cutaways from the video linked by one gesture of motion (camera moves, pans) while the speech runs over them.
gfx.callout — circle an object or a line on a screen that is being talked about (≤ 1 per 3–4 s). gfx.counter — a
stated number, landing on the end of the number word (≤ 1 per 8–10 s). time.slow_motion — a reaction without speech at
×0.5, once. trans.flash — only on a change of section or on a punchline, ≤ 1 per 10–15 s. trans.whip — a change of
topic or a switch to the other person in a pause, only between medium shots (on close-ups of faces the blur reads as a
defect), the subtitles sit on top of the transition and are not blurred, ≤ 2 per clip. All the moves that the cards
mark as signature for clips are used; type.subtitles, cut.quick and cut.vector_match are moved to allowed: the main
subtitle style is karaoke, while bursts and motion-matched cutting are needed only for compilations and clips with
cutaways.

**Limits per 10 s:** punch-ins ≤ 2 (and ≤ 1 per 3–6 s), inserts ≤ 2, callouts ≤ 2; crash zoom ≤ 1 and freeze ≤ 1 per
clip, flash ≤ 1.

**Forbidden.** type.beat_text — a second time grid (beats) competes with the speech; time.velocity — pulsing speed
breaks the sync of lips and voice; glitch.datamosh and glitch.pixel_sort — melt faces and subtitles;
trans.lens_distort — distorts the speaker's face and looks like a music-video transition, not a conversation;
fx.light_leak — warm blotches over faces and text that mean nothing; trans.dissolve — a dissolve between two talking
heads doubles the faces and the subtitles; time in a clip is compressed with a jump cut, not a dissolve; frame.tableau
— a long staged tableau shot without speech stalls the clip.

## SFX
- The voice is the main layer; SFX only in speech pauses ≥ 150 ms, never on words.
- hook: sfx.glitch — one quiet "pop" or "tick" when the headline appears or on the first key word, −20…−24 dB under
  the voice.
- build: sfx.whoosh (a 0.15–0.3 s swish) on a cutaway or a whip transition, −18…−22 dB under the voice, ≤ 2 per 10 s;
  sfx.riser 0.5–1 s — only in a natural pause before the punchline, cut off on its first word, −6 dB below the voice
  level, ≤ 1 per clip.
- drop: sfx.impact (a short "punch") on the landing of the crash zoom or on the freeze frame — −12…−16 dB under the
  voice, in a pause; sfx.glitch — a scratch or a tape stop on the freeze frame together with muting the bed for
  0.3–1 s; the main impact — 1 per clip.
- outro: no sounds, only the end of the bed on a downbeat.
- Music: `duck(music, under=voice)` — the bed 18–24 dB below the voice (attack 50 ms, release 300 ms); in pauses
  without speech (laughter, a freeze) — +6 dB. Limit: ≤ 4 sounds per 30 s.
- Voice: high-pass filter 70–90 Hz, noise reduction (`afftdn`) only when the noise is above −55 dBFS, de-esser 5–8 kHz
  −3…−6 dB, compression 3:1; master −14 LUFS integrated, true peak ≤ −1 dBTP.

## Color
- The goal is natural and even: pieces from different cameras and different parts of the video must not "flicker".
- Expose for the face: skin brightness of the main speaker 140–180 of 255; the difference between speakers and cameras
  ≤ 8 %.
- Contrast +5…+10 %, saturation +5…+10 % via vibrance with skin protection; neutral white balance (grays a*, b* within
  ±3), skin without a green or magenta cast; black point 4–10, white point 240–250 of 255.
- Noise in dark streams — gentle denoising before the crop; sharpening after the crop — unsharp 0.3–0.5.
- No stylizing looks; webcam and stream footage — shadows +5 %, remove the green cast.
- ΔE between adjacent pieces from the same camera ≤ 3 (the color does not jump after a jump cut).

## Text
- Layers: the headline (type.intertitle), karaoke subtitles (the whole video), the name lower third
  (type.lower_third), key words (type.kinetic in the drop), and situationally a callout or a counter. No more than 2
  layers on screen at once, not counting the subtitles.
- Karaoke: sans-serif weight 700, sentence case; font size 4.6 % H (4.2–5.5 %), in the hook 5–5.5 % H with a bounce; a
  chunk of 2–3 words, ≤ 2 lines, a line ≤ 76 % of the width (≈20 characters); base #FFFFFF, active word #FFE14A (one
  accent color per video), key word (a number, a negation) #45F06B — ≤ 1 per chunk and on ≤ 25 % of the chunks;
  outline #000 at 10 % of the font size; center x 0.47, y 0.67 (block 0.58–0.78), on a close-up of a face — below the
  chin, 0.50–0.58; never cover the mouth and the eyes. Timing: the chunk appears 2 frames before its first word, the
  highlight 1 frame early, minimum 3 frames @25 fps / 4 @30 fps.
- Headline: ≤ 7 words, 1–2 lines of ≤ 22 characters, a bold sans-serif 4–5 % H, white on a black plate at 60–70 % or
  with an outline; center x 0.5, y 0.13–0.24 (below the interface); from the first frame for 2.5–3 s or for the whole
  clip.
- Name lower third: name 3.2 % H, role 2.1 % H; left edge x 0.06–0.08; above the subtitles at y 0.48–0.60 or in the
  top band 0.13–0.24 after the headline leaves; 3–5 s, once per person.
- Key words: 1–3 words across 70–86 % of the width (≈10–14 % H), center y 0.40–0.50, 0.4–0.5 s per word.
- 9:16 safe zone: the top 12 %, the bottom 20 % and the right 12 % are the interface; everything within x 0.06–0.88;
  text does not cover faces.
- Translation: the same layout; for languages with long words — font size down to 4.2 % H and chunks of 1–2 words.

## Quality checks
| check | threshold |
|---|---|
| cuts inside a word, `qa_word_cuts` (new, from word-level timestamps) | 0 |
| leftover pauses, `qa_pauses` (new) | no pauses > 0.35 s except the planned ones (before the punchline ≤ 0.6 s, ≤ 2 per clip) |
| first word, `qa_first_word` (new); headline | ≤ 0.3 s; the headline on frame 0 |
| highlight sync, `qa_sync(tol=1fr)` | ≥ 95 % of words within ±1 frame; the chunk does not blink during pauses ≤ 0.6 s |
| reading speed, `qa_reading_speed(max_cps=20)` | ≤ 20 characters/s; a chunk ≤ 2.5 s |
| text, `qa_text_safe_zone(layout='tiktok')`, `qa_overlap(face)` | 100 % inside the zone; 0 overlaps with faces |
| visual change, `qa_visual_change(max_gap=4.0)` (new) | ≤ 4 s without a cut, a shot-size change or graphics |
| faces in the crop, `face_issues` from ed_qa | 0; the active speaker in frame for ≥ 90 % of their speaking time |
| crop from the source | ≤ ×2.2, otherwise upscale |
| loudness | −14 LUFS ±1, true peak ≤ −1 dBTP; the voice ≥ 15 dB above the bed during speech |
| clicks at the seams | crossfade ≥ 10 ms; no spikes > 6 dB above the local RMS within ±5 ms of a cut |
| loop seam, `qa_seam(max_ratio=1.6)` | ≤ 1.6× the median frame-to-frame difference, audio without a pause > 0.3 s |
| move limits | crash zoom ≤ 1, freeze ≤ 1 per 15 s, punch-in ≤ 1 per 3–6 s, flash ≤ 1 per 10–15 s |
| length and ending | 15–60 s; ends on a sentence boundary |
| black and frozen frames | no black frames; a freeze > 0.5 s only as the planned freeze frame; the `cuts_on_grid_share` check is disabled for this genre |
