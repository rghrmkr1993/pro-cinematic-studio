# Higgsfield Academy, condensed curriculum [official, 2026-10-13]
Source: higgsfield.ai/academy (16 courses, lesson pages read for 8 of them; others list titles only, see end). Paraphrased. Labels: (V) official lesson text, (T) inferred from titles only.

## Master pattern taught in every course (V)
1. ASSETS first (product sheet, character sheet, locations, props) in Soul Cinema or GPT Image 2.0. 2. SHOT LIST written by a Claude skill, one shared style header on every shot. 3. SCENES generated in Seedance 2.0, then repair. "The finished ad is the best few seconds of about a hundred tries."
Never write Seedance prompts from scratch per shot; load a prompt-builder skill once, hand it: the script, every locked asset as an image (not described in words), and a name for each (@hero, @product, @kitchen).

## Course 1: The 3-Step Realistic AI Ad Workflow (16 lessons)
- Product sheet: one photo is not enough. Edit it in GPT Image 2.0 into front plus 3/4 (and back/top) views so the video model knows every side. Prompt pattern: "Make a product sheet with front and 3/4 views of the item from @image_1".
- Character sheet: ask Claude to write the prompt; two panels (face close-up, full body front and back), plain GREY background, Soul Cinema. Run many batches (about 8 images per credit), keep two or three faces, do not lock the first.
- One face per sheet: the full-body panel repeats the face, so the video model drifts between two faces. Erase the face on the full-body panel (GPT Image edit) and keep the close-up as the only face.
- Side characters: AI Cast gives a full sheet with styling options from one line. Pick the face whose role reads at a glance.
- Locations: generate at a 3/4 angle (depth for camera moves), bright clean commercial look. A still can pass and still fail in video: always run the hero through the location before locking (light can go flat in motion). Test 2 heroes x 2 locations with the SAME simple prompt, change one variable only.
- Outfits: ask Claude for 10 outfit prompts, run all in GPT Image 2.0, about half are usable, combine best parts of two ("shirt from look 2, jeans from look 1"). Every edit pass costs quality, so check skin texture after edits (face softening).
- Props (hero object repeats): one clean sheet each, no motion test needed.
- Two sheets, not one prompt fighting itself: dry vs sweaty wardrobe states are separate references.
- Scene repair loop: run, NAME what is wrong (light, static camera, crammed beat), have Claude fix the shot list, change the shared style prefix once and it updates every prompt. Request "no static wide, ease around to profile" instead of "dynamic".
- Light drifts (to sunset), direction flips, prop size changes: words cannot pin geometry. Build a LAYOUT MAP (schematic with landmark, prop at exactly 2x person height, walking direction left to right) in GPT Image 2.0, give it to Claude to rewrite the prompt, and reuse the identical map in later scenes.
- "Asking for a dance gets flailing": choreograph move by move with timings. Generic direction only where the beat is a simple contrast.

## Course 2: Cinematic Ad End-to-End (10 lessons)
- Same 3 stages. Shared STYLE HEADER on every shot (V): format and realism, cinematography, natural light with contre-jour and camera on shadow side, 60:30:10 colour rule, physical cine lens with 180 degree shutter, pore-level skin (or metal-level realism for machines), naturalistic acting, physics (weight, contact shadows, no floating props), continuity, 24fps, audio rule (environment SFX only, no music, no subtitles).
- Shot prompt anatomy: STYLE header, SUBJECT with @tags and size ("human-scale 1.85 m, matches reference 100%"), MULTISHOT with beats, FIRST FRAME and blocking, audio. Dutch angle values in degrees, handheld height, and beat numbering ("Beat one... Beat two") are used.
- Heavy handheld is stated as a physical operator (tremor in cm, breath drift) plus NEVER lists (gimbal glide, lockoff). Say "no rain, no fog" when the look must stay sunny.
- Scene pairs per lesson (12 shots); failed takes are shown with the fix.

## Course 3: Santiago short film (19 lessons, seven read)
- Read failed takes: 4 of 4 bad means REWRITE the prompt, not reroll. Tells: a third chair appears (furniture count not locked), flat angle, dead eyes. Lock object counts and name the acting beat.
- Character sheet 3 panels (front, back, close-up) on grey, with sizes, eye colour, hand-lettered shirt text. Age-regression: a separate sheet for the child version.
- Establishing shots and hands: give x/y frame positions in FIRST FRAME blocking, light direction, named references with "100% matches the reference".
- Speed ramp: one continuous take, extreme handheld, floodlights as flare source, fog; freeze beat described in time. Whip pan: two shots, hard cut at 0.5 s, readable text kept on a large prop.
- Titles only (T): Dutch angle and combining takes, match cut and flares and fog, one-off characters, voice-over direction, dialogue pacing after flashback, final scene in three shots.

## Course 4: AI VFX on Real Footage (11 lessons, all read)
- The one move: video-to-video in Seedance 2.0. Real clip in, one sentence of change, same shot out. No masking, rotoscope or tracking.
- Prompt skeleton: "@source: Original clip (describe subject, setting, handheld move). Preserve identity, face, wardrobe, performance, lip-sync, framing, lens, camera exactly. Change ONLY [x]. Do not re-frame, re-time, re-light or re-cut. Photoreal, ratio, duration, grade. NON-IP (generic creature, no logos). SFX only. Continuous with the source, frame for frame."
- Rules: keep a REAL ANCHOR (face, hands, dashboard); effects sit behind edges with real contact shadows; parallax must match a moving camera; change ONE thing; shoot native 4K to hold detail and lip-sync. Creature from a reference photo: say the reference is appearance only. Time-of-day or world swap: replace background and light, keep subject and car.

## Course 5: Brand visuals with AI (9 lessons)
- Stack: image model for brand assets, Claude for prompts, Marketing Studio for finished ads. Logo prompt gives a hex accent, flat vector, stacked icon over wordmark; "recreate exactly, change only the wordmark" for tweaks.
- Product mock-ups: spell out fabric, silhouette, panel construction, one-word graphic in quotes, white background. Packaging: describe material, text lines, colour of each item, "lots of empty space".
- Marketing Studio: Hyper Motion runs with product only and zero prompt (assembly reveal), reliable for catalog batches. TV Spot: brief the idea in Claude first (selective colour, long exposure, invert flashes). Try-on: static camera and timed segments (0-3s, 4-7s) in the prompt. Social stills: Nano Banana Pro at 3:4, the same ambassador character across the batch, Claude skill turns character plus clothing sheet into the post prompt.

## Course 6: Cinematic Realism 4K (8 lessons, all read)
- Genre prompts: 3D cartoon (shot-by-shot with quoted lines), cartoon/2D, hyper-detail one-take (single continuous shot, original creature design), game trailer (HUD elements pinned per shot with positions, "game-rendered, NOT film"), arcade racing (MASTER STYLE REFERENCE image, match 100%).
- Crowds: 21:9 army shots now hold at 4K where 1080p melted background figures. Ad with sharp text: logos and names given verbatim as "read exactly", timed sections (0.0-2.0s), hard cuts on action, one named film-burn transition.
- Say what the image is NOT ("no 3D render, no game engine") when you need photoreal.

## Course 7: Direct AI Fight Scenes (5) and Car Commercial (11)
- Read the result backward as a CONTINUITY problem before a generation problem. Repeated failure points at brief or references; one-off defect after the move works means reroll.
- Give measurements ("start 8 m out, 3 m up, half circle, end 4 m, under half a second"), not "huge" or "dramatic". Freeze pose before impact is its own asset. Replace game-like trailing cam with cinematic coverage (orbit, low angle, close-up, wide). Split crowds into classes if silhouettes clone.
- Car: build a dependency table (asset, approved reference, scenes). Block the middle first, then arrival and exit. Clean plates: remove text, clutter, distant cars (they morph into copies of the hero car). One variable per correction. Keep a TAKE LEDGER: keep the fragment that solves one job, discard the rest. Wide traffic frames fail; tighten framing. Check geography in the edit (side of road, exit side). Derive reference stills from one motion clip so light matches. Props that read: bold headline, blurred small print; give the cap a landing spot; fix the controller in the window from frame one; state exact shot and cut counts.

## Course 8: How to evaluate AI filmmaking demos (11 lessons, Seedance 2.5)
- Review ONE kind of evidence per pass: camera trajectory, edit continuity, face under strain, choreography (entry, contact, recovery, reflections), world coherence, delivery size. Write observable facts, not "cinematic". Check contact points (hand and object), eyelines, light direction at reverse shots, consequences persisting after a transformation, depth layers under fast pullbacks, tiny faces are "inconclusive". Verify resolution claims on the real product (V caution).

## Not read (titles only): Blockbuster 4K pipeline (10), Claude plus Higgsfield ad agency (12, business ops: niche, offer, intake, QC gate that never auto-approves or sends, subscription), Animated Short (8 styles), Faceless channel (7), Automate faceless niche (11), Mix AI with real footage (10), 3D games with MCP (10). Prompt bank at /academy lists camera moves (static, pan, tilt, zoom, dolly, rack focus, crane, drone orbit, aerial pullback).
