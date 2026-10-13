---
name: cinematography
description: "Coverage and sequences for AI film work: standard scene coverage (master, mediums, singles, inserts, cutaways), dialogue grammar, action and chase grammar, montage, establishing sequences, transitions (match cut, whip, morph), and how to plan coverage shot by shot for AI generation. Part of the cinematography skill."
---

# Coverage and sequences
Labels: (K) established craft, (3P) third-party, (V) vendor-official, (H) house rule. For film pipeline steps (script to master edit) use `film-studio`; this file is the shot-level grammar.

## Why coverage
Coverage is the set of angles that lets the editor build a scene with rhythm, fix mistakes and hide cuts. With AI there is no "shoot it all once": every angle is a separate generation, so plan the minimum set that tells the story. (H)

## Classic scene coverage
| Shot | Purpose | Notes |
|---|---|---|
| Establishing | Place, time, mood | Wide, exterior or room; usually first |
| Master | Whole scene in one wide, actors and geography | Safety net, shows blocking |
| Two-shot / medium | Relationship, bridging | Between master and singles |
| Over-the-shoulder pair | Dialogue exchange | Alternate A and B |
| Singles / close-ups | Emotion, key lines | A and B, matched eyeline height |
| Reaction | Listener's response | Often the most expressive |
| Insert | Object or detail | Letter, phone, hand, product |
| Cutaway | Related image | Hides edit, pacing |
| Re-establishing | Show the new geography after movement | After a big change |
| POV | Subjective | Use sparingly |
Triangle rule: for a standard two-person dialogue shoot master, two OTS, two singles, and 1 to 2 inserts. Typical edit: master to start, singles for emotion, back to master when blocking changes. (K)

## Dialogue scene grammar
- Open wide or medium to set the space, then cut to closer coverage as intensity grows. (K)
- Keep the 180 line, same eye-line height, consistent screen direction (see `composition-and-blocking.md`). (K)
- Cut on the listener, not only the speaker, for subtext. (K)
- Use singles when a character reveals; use a two-shot to show distance or to break a spell. (K)
- Rhythm: slow scenes breathe on longer takes (4 to 8 s), tense scenes cut faster (1.5 to 3 s). (3P pacing guidance from Higgsfield visual-language notes)
- Lip-sync and dialogue audio: native audio with Veo 3.1 and Cinema Studio 3.0 and up (V); put dialogue in quotation marks, label SFX and ambient sounds (V Google guide). Keep lines short per clip.
- AI shortcut for dialogue: make one strong locked master and two matching singles in the same light and lens, then cut. Matching light and lens across clips is the continuity. (H)

## Action and chase grammar
- Vector direction: keep the chaser and the chased moving in consistent screen directions (usually pursuer behind, same direction). Reverse only at deliberate turns. (K)
- Build escalation: wide geography, medium tracking, close details (feet, hands, wheels), obstacle, near miss, payoff. (K)
- Mix perspectives: drone, tracking side, low front, POV, inserts. Change angle at least 30 degrees between neighboring shots (K).
- Cut rhythm accelerates toward climax, then holds on the aftermath. (K)
- Slow motion beats mark impact; speed ramps in post (V, Cinema Studio speed ramps).
- Renderable by AI: pursuits, near misses, aftermath, jumps, stunts at distance. Unreliable: precise strikes, close grappling, prop combat (V Higgsfield guidance). Cut away at the strike and show the reaction or aftermath. (H)
- Physical logic: say speed, vehicle, surface and direction; "motorbike speeds left to right across frame, dust trail, camera tracks parallel".

## Montage
| Type | Use | AI plan |
|---|---|---|
| Time passage | Training, seasons | Same framing, changed light or costume; 6 to 10 shots at 1 to 2 s |
| Parallel | Cross-cutting two lines | Distinct palettes per line |
| Associative | Ideas by juxtaposition | Match shapes or colors between images |
| Rhythmic / music | Beat-cut | Plan against the audio waveform |
| Product benefit | Ad structure: hook, problem, product, proof, CTA | 0 to 1.5 s hook, 1.5 to 5 s desire, 5 to 15 s product, 15 to 22 s proof, last 2 to 3 s CTA (H, from Higgsfield visual-language notes) |
Montage works best when shots differ in size and angle but share color and light. (K)

## Establishing sequences
1. Wide of place (landscape, skyline, building exterior).
2. Medium into the environment (street, doorway).
3. Detail that tells character or time (clock, sign, hands).
4. Arrive on subject.
Day, weather and time of day cues: light angle and color tell the audience in one frame. (K)

## Transitions
| Transition | How | AI method |
|---|---|---|
| Cut | Direct | Edit |
| Match cut | Shape, motion or position carries across a cut | Same framing and subject position in both clips; use last frame as the next first frame (V Higgsfield Academy recommends frozen-pose match cut) |
| Whip pan | Blur wipe between two places | Whip at end of clip A, whip from opposite side at start of clip B |
| Morph / transform | Object becomes another | Veo first-and-last frame, Kling start and end frames (V); keep shapes similar |
| Dissolve | Cross fade | Edit |
| Dip to black | Time gap | Edit |
| Smash cut | Silent to loud | Edit and sound |
| Wipe by object | Subject or object covers the lens | Use dark pass, door, cloth as natural wipe |
| L-cut / J-cut | Audio leads or lags picture | Edit |
| Seamless long take | Hidden cut during whip or pass | Clip joins at a dark moment |
Transition pairing rule: end a clip on a still beat and start the next on a still beat (about 1 to 2 s) to join cleanly. (V Cinema Studio guidance on still beats; H)

## Plan coverage for AI generation (shot by shot)
1. Write the beat sheet (5 to 12 beats per scene).
2. List shots in a table (see `shot-list-templates.md`). One shot per beat, fewer if possible.
3. Decide the continuity pack: subject reference (Element or image), location reference, light, lens, palette. Build these first (V Higgsfield Academy: locations first, then characters).
4. Generate the hardest shot first to prove the setup (V).
5. Chain shots by last frame to first frame where continuity is needed; otherwise re-anchor with a fresh reference image. (V)
6. Keep each shot to one move, one action, 4 to 8 s; short clips behave better. (3P)
7. Alternate size, angle and action between adjacent shots to avoid morph-like cuts. (H)
8. Generate 2 to 4 variants per hardest shot; review hands, labels, eyelines, reflections, left-right orientation.
9. Edit in a conventional editor; fix gaps with cutaways and inserts rather than regenerating a perfect master.
10. Add sound design and a grade across the sequence last.
Budget thinking: wasted generations are the main cost. Draft on a cheaper model or lower resolution, lock camera language, then render finals. (H; costs change, read the Generate button)

## Insert and cutaway library for products (client-neutral)
Texture macro, pour or drop, hand using product, packaging detail, ingredient botanical, environment cutaway, label hero. Generate inserts from the same product reference to keep the label shape consistent; add real label text in edit, since models garble text. (H)

## Common sequencing mistakes
- Same size and angle twice in a row (jump cut look).
- Eyelines pointing the same direction in a reverse shot.
- Lighting changes between singles of the same scene.
- Too many moves: cut energy comes from the edit.
- Forgetting re-establishing shot after a big movement.
