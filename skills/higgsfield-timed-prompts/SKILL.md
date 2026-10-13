---
name: "higgsfield-timed-prompts"
description: "Write, revise and audit timecoded multi-shot video prompts for Higgsfield using Seedance 2.5 and similar timestamp-driven models, for commercials and short narrative clips with fixed dialogue, match cuts, multi-location continuity, blocking diagrams and reframe/outpaint passes. Create placement maps from supplied references and apply them to video prompts; deliver in the format requested by the user."
---
Part of the cinematic pipeline: entry point creative-studio


# Higgsfield Timed Prompts

A production method for timecoded video prompts in Higgsfield using Seedance 2.5 (and similar timestamp-driven video models), distilled from a multi-part commercial: several friends, one prop passed between them, three countries, fixed dialogue, match cuts, a packshot. It works for any project where a clip has several shots, exact timecodes, spoken lines and characters who must stay in their seats.

Chat with the user in their language; every generation prompt is written in English unless they request another language. Optional translated tabs (e.g. Chinese) are kept in sync with the English master.

## 0. Non-negotiable conventions

- Asset handles are `@` + the asset's own file name, exactly as it sits in the project folder: `@char_alex2`, `@loc_flat2`, `@loc_mexico`, `@loc_japan`, `@prop_phone`, `@japan_topshot`. Never `@image1`, `@video1`, slot numbers or `<<<uuid>>>` — convert any such reference the user pastes.
- Preserve the user's requested destination and format: a chat answer, an existing Notion block, or an HTML file. Use the HTML workflow only when that format is requested. Keep established asset handles; do not add or remove numeric suffixes automatically. Archive replaced production files when the user has requested backups.
- Always deliver full prompts (never diffs or "same as before"). Keep every previous correction unless the user removes it explicitly. Never re-introduce a cancelled version or invent new story beats.
- When the user asks for a prompt "in the chat", paste the complete prompt in a code block and do not touch the HTML unless asked.

## 1. Workflow

1. Collect: script/lines with the user's timecodes, asset list (file names), aspect, duration per part, target model route.
2. Draft the prompt for the requested part. For an HTML deliverable, keep a scratch `.txt` and splice it into the requested HTML with escaped text; for a chat or Notion deliverable, preserve the existing block format.
3. For timecoded video prompts, validate that shot headings are contiguous (`end_i == start_{i+1}`), the last end equals the declared duration, and spoken lines and times agree with the SOUND list. Check all handles against the supplied assets. Each shot describes its background; preserve the existing heading style. A still-image diagram prompt does not need video timing or sound sections.
4. Deliver in the user's requested format and briefly report the exact changes. Update only the agreed material; do not overwrite unrelated files.
5. On feedback, edit the scratch text with exact-match replacements that assert exactly one hit, then re-splice. If a replacement misses, nothing is written — fix the search string, never silently continue.

## 2. Prompt architecture (in this order)

```
<One-sentence logline: duration, aspect, what happens, what the cut trick is.>
<"Opens mid-situation …" — the state of the world at frame 0 if the clip continues an earlier one.>

REFERENCES
@handle — what it is, what to take (face/clothes/geometry), what to IGNORE (studio backdrop, people in the location plate, colour of a blocking map). Say when a location plate's camera angle IS the first shot's angle.

LOOK
One paragraph: lens family, colour intent, per-location light.

CHARACTERS
Name — two or three trait words + how they speak + one behavioural rule ("never laughs", "never still").

<PROP RULE(S)> e.g. PHONE RULE: screen never shown, angled screen-to-character, red back to camera, taps on the screen side, face down on tables.

WHERE EVERYONE IS — fixed for the whole clip
Per location: clock-face seats (empty side = 6 o'clock) OR plain screen-left/centre/right from a named camera side, plus what is behind each person.
<Exact placement paragraph for any recurring background group (a band, a crowd): where they stand, orientation, that they keep acting, that they never move.>

WHAT IS BEHIND EACH OF THEM — so they land in the right seats
Per location, one line: behind A …; behind B …; behind C ….

SHOTS
<t0–t1>s — <camera position, lens, move that runs the whole shot>. <Who is where in THIS frame>. BACKGROUND: <what is behind them from this angle>. <Action beats with timecodes>. <Line(s) with exact times and delivery>. <Cut / transition on which frame>.

SOUND
Music policy (usually none; diegetic only, with on/off frames). Ambience per location, changing on exact cut frames. Voice recording spec. "Lines, each spoken exactly once and nothing else: <time> <Name> "…" · …". "No added words, interjections, laughter, humming or added background score." Keep any explicitly requested live music audible in its assigned shot.

KEEP CONSISTENT
8–14 one-line rules restating the things the model tends to break (see §6).
```

Why this order works: the model reads geometry before action, every shot is self-contained (camera → who is where → background → action → light), and the last block repeats the fragile rules.

## 3. Shot-writing rules

- First frame: state it explicitly ("THE VERY FIRST FRAME OF THE CLIP IS THIS …") and, if a plate defines the angle, say "exactly the angle of @loc_x". If the user wants an establishing wide, make it its own 1.0–1.5 s shot with a hard cut, showing who sits where, no boat/prop/close-up in front. If they later drop it, shift every timecode and re-state the new first frame.
- Every shot names camera position, lens (16–28 mm wides for energy), the move (orbit ~135°, push-in, travel L→R, whip, pull-back) and that the move never stops for a line.
- Every shot has `BACKGROUND:` — what is behind each visible person from this angle. It is the cheapest way to make seating stick.
- Off-frame people: say "X is out of frame" rather than leaving it implied.
- Timecodes for every beat: bite, grab, tap, look, sit-up. Lines get start–end (short words get a single time). A line never spills across a cut unless the transition depends on it.
- Body/prop truth per shot: what is in each hand, from the first frame of the shot ("BOTH hands full and clearly visible").
- Reactions are staged inside the shot: "In this same shot, right after the reveal … Still inside this shot, before X happens …".
- Write positives; use negations only as a short tail ("no dissolve, no flash, no morph"). Preserve the approved look. If washed-out colour is an observed problem, revise the relevant grade wording; do not ban film grain, film look or another deliberately chosen treatment globally.
- Group performance (band, crowd): where exactly, facing which way, "PLAYING the whole time they are on screen", "never walk, never turn their backs".

## 4. Transitions

- MATCH CUT on an action (a tap, a bite): "Same <lens>, same angle, same face size, same pose, same hands, same <move> continuing without a stop. On the cut frame he is still looking at the phone. BACKGROUND behind him now: …". Reaction to the new world only after the cut, with a timecode. Ambience and diegetic music switch on the exact frame.
- HIDDEN CUT under full occlusion: camera slides behind a near shoulder "until <fabric> and hair fill the whole frame, every edge and corner"; the world changes inside the occlusion; the camera "keeps moving at the same speed and comes out past her <side> shoulder" into the new place, with the new geometry named. Prefer match cuts when the user wants reliability; occlusion cuts drift more often.
- FOREGROUND WIPE: when the approved shot uses only partial foreground coverage, describe the opaque silhouette crossing the frame and the next location appearing around its edges. Do not impose full-frame occlusion on this different transition. Preserve the selected transition type.
- Objects that must vanish with the world (a taco, a fork): "vanished with the world change, and only now, never before the cut", followed by the reaction in the same shot.

### Worked example — the "app tap → new country" match cut (home → Venice, "Pasta!")

The pattern: the character speaks TO the friends, then looks INTO the phone, a micro-pause of reading, a pleased one-word reaction, ONE tap — and the world changes on the tap while the camera move continues. The food word is spoken only in the new place, never at home. Two consecutive shots, written like this:

```
9.8–12.2s — Mika sitting on the sofa, 28mm, medium shot waist-up. @prop_phone in her hand, its back to camera. A clear ORBIT of about 135°: the camera starts behind her right shoulder, travels through her right profile to a front three-quarter view, pulling back slightly as it goes, and never stops for the lines. BACKGROUND turns with the orbit: … and at the three-quarter angle lands on the sofa back with the tilted skylights and blue dusk behind her. 10.0–11.1s, looking at her friends, not at the phone, conversational, confident, quick: "Let's check Higgos." Only after the last syllable of "Higgos" does she look down at the phone. 11.1–11.45s a micro-pause: her eyes scan the screen as if she has found something appetising — no swipe, no tap. 11.45–11.8s, still looking INTO the phone, not up at her friends, pleased, the mood turning from puzzled to happy anticipation: "Ooh." At 12.2s ONE tap on the screen with her index finger — and the match cut comes on that tap, with the camera at the front three-quarter angle. No waiting between tap and cut.

12.2–16.5s — MATCH CUT into @loc_italy. Same 28mm, same three-quarter angle, same size and position of Mika in frame, same orbit continuing at the same speed with the same slight pull-back. She is already seated at the terrace table, a plate of tomato spaghetti in front of her. BACKGROUND: the plaster wall with the open window and green shutters directly behind her; as the orbit comes round to frontal, the timber door at one edge and geraniums at the other, hard sun on the wall. Right after the cut she lowers the phone down or to the side, her eyes drop to the plate, and 12.7–13.2s, warm appetising joy, a natural short word, not stretched, not shouted: "Pasta!" The orbit keeps moving during the line, continues to a frontal view and eases to a smooth stop by 14.9s. She then reaches for her fork. Hard midday sun, geraniums at the edge of frame.
```

Supporting lines elsewhere in the same prompt: SOUND — "Ambience cuts with the match cut at 12.2s." and "\"Pasta!\" is spoken only in Italy, never at home. Nobody says \"Italian\"."; KEEP CONSISTENT — "12.2s is a hard cut that changes only the world — same orbit, same speed, same framing." and "the tap at 12.2s lands on the screen side." Reuse the shape for any product-tap transition: line to friends → look into phone → pause → "Ooh."-type reaction → tap = cut → the craving word in the new world.

## 5. Dialogue and voice

- Lines are fixed text from the user; never add or reorder words; each spoken exactly once. Keep a single canonical `Lines, each spoken exactly once and nothing else:` list with identical times to the shots.
- Delivery per line: tempo, emotion, where the eyes are ("looks AT THE SCREEN for the whole line", "addressed to the friends but eyes stay on the taco"), physical state ("MOUTH FULL, cheeks slightly puffed").
- One character interrupting another: put the interrupter's first word inside the other's gesture ("while the mouth is still wide open … cuts in … focus racks on her very first word"), forbid a gap.
- Voice spec that keeps audio clean: "clean, close, professional studio dialogue recording on a professional studio microphone — dry, no echo, no noise; the microphone never appears in frame".
- Sound policy: no score, no stings, no whooshes; diegetic music only from an established source in the scene, whether on or off screen, with on/off frames; ambience per location.
- Voice-over/packshot: give the exact VO text, timing, voice character and pronunciation ("HIG-gohs").

## 6. KEEP CONSISTENT — the usual lines

The following are optional examples. Apply only constraints requested for the current shot; do not copy example durations, framing or character rules into unrelated prompts.

Faces/clothes exactly as references (+ per-character quirks: "no freckles, never a cropped head", "beanie and hood on in every frame, including out-of-focus background") · seats never change within a location, restated per location with backgrounds · the clip opens on <first shot>, never on a close-up/boat · one prop, who holds it when, where it ends · the two cut frames and what kind of cut each is · group keeps performing · "camera never stops for a line" · "X never laughs" · table dressing exact ("three settings, two shared plates, no extra place") · colour "rich and saturated in every shot — never washed out, faded, hazy or pastel" · no subtitles, no on-screen text · what is NOT in this clip ("no packshot, no flat — ends on the doorbell").

## 7. Failure → fix table

| Symptom | Fix |
|---|---|
| Clip opens on the wrong shot (boat, close-up) | Explicit first-frame sentence + "never on …" in KEEP CONSISTENT; make the wide its own shot with a hard cut |
| People swap seats between shots | Clock/screen geometry block + `BACKGROUND:` per shot + WHAT IS BEHIND EACH OF THEM |
| Washed-out colour | Remove film-emulation words; write "clean modern digital cinema look, deep clean blacks, punchy contrast, saturated like the location references" |
| Eyes closed / asleep | "eyes OPEN for the entire shot, pupils clearly visible" + rule line |
| Line said to the wrong person or twice | Address + eye-line in the shot; canonical lines list; "The line is not repeated" after match cuts |
| Band/crowd stands still or walks off | Exact placement paragraph + "playing every moment on screen", "never walk" |
| Prop appears/vanishes early | Per-shot hand inventory + "only with the world change, never before the cut" |
| Model ignores a blocking-map asset | Bind its colours/positions explicitly to the character handles and separate geometry from appearance. Resolve any conflict against the requested layout; do not silently remove an approved map |
| Transition drifts (occlusion) | Check the camera path and coverage first. Propose another transition only if the user wants to change the approved method |

## 7a. Blocking diagrams and placement references

This is the blocking part of `higgsfield-timed-prompts`; a separate blocking skill is not required.

**Choose the camera view from the requested shot.** For a straight-down overhead shot, produce a top-down map. For a frontal or oblique shot, use the requested view. When the user is designing a new angle, do not copy a source photo's perspective automatically.

### Create the map prompt

- Identify each supplied image's role. A location photo may define the round table and the types of plates; the user's text defines the requested seating and counts. A failed generation may show an unwanted extra setting, which must not be preserved when the user asks to correct it. Never assume that a finished map is already attached before it has been created.
- Translate the intended geometry into an image-generation prompt. If no coordinates were supplied, propose approximate X/Y percentages based on the requested layout; do not refer to nonexistent "coordinates below". Keep perspective references separate from the new camera angle.
- Use simple thin outlines on white, one distinct muted colour per figure, with furniture and tableware in light grey. Keep the diagram free of facial, wardrobe and photographic detail. Use no labels or letters on the image unless requested. A faint grid is optional; omit it for a plain-background map.
- Describe the exact number and position of personal settings, shared plates, chopsticks and phone. A shared plate is not another seat. Exclude unrelated background or props from a placement-only map.
- For exact tracing, preserve the requested source crop. For a newly designed composition or requested headroom, use the requested target framing instead. Do not impose a universal rule either to crop heads or to invent missing body parts.
- Return the complete diagram-generation prompt in the requested format. Keep the project's chosen map name, such as `@japan_topshot`; do not impose a new tag scheme. The tag becomes an available asset only after the map is generated and saved.

### Apply an existing map to a video prompt

- Use the map for positions and tableware geometry. Use the location and character photos for room, lighting, identity and clothing. State these roles explicitly; the map's colours identify figures, not wardrobe.
- Bind colours directly to the existing character handles. Letter aliases are optional and must not replace established names. For the Japan example: orange at left = `@char_jenny`; blue at top = `@char_alex2`; green at right = `@char_mika`. The lower side has no personal setting. These are directions in the overhead map, not fixed screen positions from every camera angle.
- Keep all required photo references available alongside the map. Attachment order is not a universal requirement; identify each role by its exact name. If a particular model needs another order, use its observed interface and update the description accordingly.
- Apply a Japan tableware map in Japan only. Other locations retain their own food and props. When connecting shots, distinguish a camera-angle change from a physical change of seats.
- Preserve the user's dialogue, timing and approved actions. For a correction request, change only the requested layout, shot or timing; do not add a new sequence.
- Check that the text, map and named photo references agree. When reviewing an actual result, distinguish the intended instruction from an observed deviation or an explicitly accepted take. Do not claim that the prompt guarantees an exact generation.

## 8. Variants the user often asks for

- Shortened part (e.g. without the establishing wide): drop the shot, shift all times by its length with a single regex pass, re-state the first frame, update SOUND and KEEP CONSISTENT, re-validate.
- Mini fragment (2–3 shots) for retakes: same header blocks trimmed to that location, opening "mid-situation", same lines and geometry as the master.
- Translated tab: full translation of the current master, kept in sync on every edit.
- Looser seating on request ("don't specify where X sits"): remove all positional adjectives for that character, keep only what the shots require, add "each keeps the place of their first shot".

## 9. Reframe / outpaint prompt (16:9 → 9:16 or 1:1)

Analyse the final edit first (`ffprobe`, scene detection, a 1 fps contact sheet) to get the shot list with cut times. Then:

```
GENERATIVE REFRAME 16:9 → 9:16 … Outpainting only.
INPUT @final_x — duration, resolution, fps, N shots, finished sound.
OUTPUT size, fps, exact duration, same cut points. Audio: source track passed through — no generated sound.
HOW THE FRAME IS BUILT — TOP AND BOTTOM ONLY: fit the entire source uniformly to the output width, with left and right edges aligned to the output; zero pixels generated on the sides; keep that fixed scale and exact vertical centre in every frame, with no crop, animated zoom or repositioning; the middle band contains the complete source picture; two equal bands of M px above and below. Composition of the original shot IS the composition of the output. Seams invisible. No zoom, crop, pan-and-scan, letterbox, blur/mirror fill.
RULES FOR THE GENERATED BANDS — environment only; no new people/hands/faces/animals/food/phones/screens/text/logos; no duplicates of existing objects; bodies cut by the edge continue as clothing only; perspective of wide lenses; camera moves carried with parallax; hard cuts hard on the same frame; match cuts change bands on the same frame; colour stays saturated.
SHOT BY SHOT — per shot: ABOVE: … BELOW: … (ceiling/sky vs floor/table), what must stay a single object.
AUDIO — NOTHING IS GENERATED: source track only, list every forbidden category (music, ambience, foley, voices, effects), "silence is preferable to any new sound".
KEEP CONSISTENT.
```

Band maths: (output height − output width × 9/16) / 2. For 1080×1920, fit the source to about 1080×608 and add 656 pixels above and below. For 1080×1080, add about 236 pixels per band. Round to whole pixels consistently; the source is uniformly fitted, not preserved at its original pixel dimensions. Tell the user that if the tool still crops/moves the source, its fit/fill setting overrides the prompt, and that replacing the audio track in the edit is the safe fallback.

## 10. Deliverable HTML

One file, dark or light theme, `.tabs{display:flex;flex-wrap:wrap}`; per tab a `<button role="tab" id="tab-X">` with label + duration + `<span id="tabcount-X">` chars; per pane a Copy button (`data-copy="prompt-X"`), a meta line ("N references · set 21 s / 16:9 / 1080p · <b id="count-X"> chars") and `<pre id="prompt-X">` with the escaped prompt. JS: fill counters from `textContent.length`, tab switching, clipboard copy. Header states total durations. Add tabs by extending the letter list in all three JS arrays. Validate tag balance after every splice.
