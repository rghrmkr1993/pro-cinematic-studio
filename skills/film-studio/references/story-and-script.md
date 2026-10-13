# Story and script (Phase 1)

Evidence labels: (F) fact from a cited source, (E) estimate, (A) assumption. Structure models are craft conventions, not laws.

## 1. Workflow: idea to screenplay (gate at each arrow)
1. Premise: one sentence, who wants what, what stops them. Gate: a stranger repeats it back correctly.
2. Logline (25 to 35 words): protagonist with a flaw, inciting event, goal, stakes, irony. Template: "When [inciting event], a [adjective flawed protagonist] must [goal] before [stakes], but [opposing force]."
3. Synopsis (1 page) then treatment (5 to 12 pages for a feature, present tense, no dialogue except key lines).
4. Beat sheet (section 2) with target runtime minute per beat.
5. Sequence plan (section 3): 8 sequences, each with a want, obstacle, partial resolution.
6. Scene list: one line per scene: location, time, characters, what changes, emotional value shift (plus to minus or reverse). Cut any scene where nothing changes.
7. Screenplay draft (section 4 format), then two revision passes: structure pass, then dialogue and visual pass.
8. AI-readiness pass: every scene must be shootable by a generator (section 6).
Owner: creative-director writes, tech-writer formats and keeps versions, qa-tester reads for continuity holes. Lock = G1.

## 2. Structure templates
Pick one spine, borrow beats from the others only to diagnose.
### Three-act (F, standard craft)
Act 1 set-up about 25 percent, Act 2 confrontation about 50 percent (midpoint at 50), Act 3 resolution about 25 percent. Turning point 1 at about 25 percent, turning point 2 at about 75 percent.
### Save the Cat, 15 beats (F, Snyder; pages for a 110-page script, convert to percent for other lengths)
| Beat | Page | Percent |
|---|---|---|
| Opening Image | 1 | 1 |
| Theme Stated | 5 | 5 |
| Set-Up | 1 to 10 | 1 to 9 |
| Catalyst | 12 (some sources 10) | 11 |
| Debate | 12 to 25 | 11 to 23 |
| Break into Two | 25 | 23 |
| B Story | 30 | 27 |
| Fun and Games | 30 to 55 | 27 to 50 |
| Midpoint | 55 | 50 |
| Bad Guys Close In | 55 to 75 | 50 to 68 |
| All Is Lost | 75 | 68 |
| Dark Night of the Soul | 75 to 85 | 68 to 77 |
| Break into Three | 85 | 77 |
| Finale | 85 to 110 | 77 to 100 |
| Final Image | 110 | 100 |
For a 90-minute film multiply percent by 90 to get the runtime minute of each beat.
### Hero's Journey, 12 stages (F, Vogler after Campbell)
Ordinary World, Call to Adventure, Refusal, Meeting the Mentor, Crossing the Threshold, Tests Allies Enemies, Approach to the Inmost Cave, Ordeal, Reward, The Road Back, Resurrection, Return with the Elixir. Best for quest, fantasy, animated family and coming-of-age. No page targets.
### Sequence method, 8 sequences (F, Frank Daniel, Gulino)
Act 1 = sequences 1 to 2, Act 2 = 3 to 6, Act 3 = 7 to 8; each about 12 to 15 minutes in a 120 minute film, about 10 to 12 in a 90 minute film. Each sequence is a mini-movie with its own want and tension. This is also the production chunking unit (SKILL.md section 3). Use it to manage a sagging Act 2.
### Others to know
Kishotenketsu (4 parts: intro, development, twist, reconciliation; no central conflict, common in Japanese and some Korean and Indian slice-of-life), Indian masala structure with interval (E: first half builds to an interval hook at about 55 to 60 percent of runtime, second half resolves), episodic anthology, documentary arc (question, evidence, turn, resolution), music film (song-driven set pieces linked by thin plot).
### Which to use
Animated family: Save the Cat plus Hero's Journey. Photoreal drama: three-act plus sequences. Epic sci-fi or fantasy: Hero's Journey plus sequences. Documentary style: question-led arc, interviews as scripted scenes. Music film: song list first, then plot between songs. Short (under 15 min): one turning point, one image of change; do not scale a feature beat sheet down mechanically.

## 3. Sequence plan template
`SEQ 3 | min 24 to 36 | want: ... | obstacle: ... | scenes: SC08 to SC14 | ends: partial win, new problem | locations: ... | cast: ... | est shots: 90`

## 4. Screenplay format cheat sheet (F, industry standard)
- Page: US Letter or A4, Courier 12 pt, 1 page about 1 minute. Margins: left 1.5 in, right 1 in, top and bottom 1 in.
- Scene heading (slugline): `INT. LOCATION - DAY` or `EXT.`; times: DAY, NIGHT, DAWN, DUSK, CONTINUOUS, LATER. One heading per location change. Add a scene number only on the production draft.
- Action: present tense, visible and audible things only, 3 to 4 lines per paragraph, no camera directions unless essential.
- Character cue: caps, centred at about 3.7 in from left; first appearance in action in CAPS with age and one visual tag.
- Dialogue: block at 2.5 in left, about 35 characters wide. Parenthetical only when tone is not obvious. Extensions: (V.O.) voice over, (O.S.) off screen, (CONT'D).
- Transitions (CUT TO:, DISSOLVE TO:) only when meaningful. Montage as a list of shots under `MONTAGE -`.
- Dual dialogue and songs: lyrics in a block headed `SONG: title`, with runtime estimate.
- Title page: title, "Written by", draft date, contact. Version in file name: `film_v03_2026-10-14.fountain` (Fountain plain text is the working format; export PDF for review).
- Non-Latin scripts: write the screenplay in the language's own script (Tamil, Devanagari) with the English slugline convention kept, plus a romanised line and an English gloss in a side file for the AI prompt stage (languages-and-localization.md).

## 5. Dialogue rules (craft)
- Every line has an objective and a tactic; cut lines that only transmit information (exposition) unless disguised by conflict.
- Subtext: characters rarely say what they feel. Let action and silence carry it.
- Distinct voices: vocabulary, sentence length, rhythm, verbal habit differ per character; cover the names and still know who speaks.
- Short lines: 1 to 2 sentences; speeches over 5 lines need a visual break.
- Generator constraints (E): lipsync and voice models drift on long lines; keep a spoken take under 8 to 12 seconds, about 20 to 35 words; split long speeches across shots with reaction cutaways.
- Overlap and interruption are written in the script, then built in the edit.
- Read aloud with the voice cast model before locking. Native-speaker review for every language (sound-music-voice.md).

## 6. AI-readiness pass (per scene)
- Can each beat be shown in 4 to 8 seconds with one subject action?
- Crowds, hands-on-object choreography, text on screen, fast fights with several characters and exact lip-read dialogue are costly: reduce, stage in silhouette, or cut away.
- Non-human leads or fantasy creatures: freeze the design in the bible before scripting action for them.
- Count speaking characters per scene (aim 3 or fewer on screen at once) and distinct locations per film (aim 8 to 20 for a feature) to bound the reference work.
- Write for the cut: leave breathing shots (establishing, insert, reaction) as scripted lines, they are cheap and hide drift.

## 7. Writing per genre (short notes)
- Animated feature: clear want, visual gags, a mentor and a sidekick, a song or montage beat at the midpoint, emotional truth for adults and clarity for children; family tone gates content and language.
- Anime: episodic arc rhythm, internal monologue, silence and held frames, seasonal and school or workplace settings; do not copy any existing series.
- Photoreal drama: scene-driven, small casts, long dialogue scenes written as shot-reverse-shot plus cutaways.
- Sci-fi and fantasy epic: rules of the world written first (what is impossible, what it costs), then plot.
- Documentary style: scripted narration or interview questions, archive-style inserts marked as recreation; label reconstructed material.
- Music film: lyrics written before picture, emotional spine in the choruses.
- Period: research file first (genres-and-styles.md section 6), then dialogue register for the era.

## 8. Deliverables checklist
Logline, synopsis, treatment, beat sheet with minute targets, 8-sequence plan, scene list, screenplay, character list with speaking line counts, location list, prop list, est shot count, est runtime, AI-readiness issues, IP and sensitivity flags for legal.

## 9. Copyright notes at the story stage
Stock tropes and structures are free to use. Protected: named characters, distinctive world designs, specific plots and invented terms of a franchise. Test: could a viewer name the original from the characters and setting alone? If yes, change it. Details: delivery-and-legal.md section 3.
