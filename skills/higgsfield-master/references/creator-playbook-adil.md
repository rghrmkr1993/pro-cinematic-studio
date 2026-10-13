# Creator playbook: @adilinthewildtempo on Higgsfield (11 blog posts, 2026-09-02 to 2026-10-11)
Read 2026-10-13 via the public blog API and post bodies (the pages render client-side). Organised by technique. Labels: (V) creator or vendor claim, (E) our estimate, (A) assumption, (U) unverified. Money and result claims are never verified. Model names are as the posts state them (GPT 6 Astra, Claude Fable 5.1, Seedance 2.5, Seedream 5.0 Pro, MiniMax H3, Nano Banana 2, imagegen 2.0); confirm availability on the Generate button.
Posts: (1) $5K a month Marketing Studio service 09-02; (2) $39K faceless channel 09-04; (3) Blender cinematic scenes 09-12; (4) 10 Meta ad creatives 09-15; (5) infinite camera angles 09-16; (6) AI motion graphics with After Effects 09-21; (7) 6 ad formats 10-03; (8) faster video editing 10-02; (9) 3-step realism 10-07; (10) AI influencers 10-10; (11) clipping 10-11. Companion: clipping-business.md.

## 1. Realism and consistency (post 9, 7, 4)
- The "3-step" realism post is really an asset-first ad build: (1) build reusable assets, (2) direct timed scenes, (3) land the brand and the payoff. Full recipe: workflows.md recipe 12 and photoreal-humans ai-prompting-realism.md section 10.
- Character sheet: 3 panels on plain mid-grey, soft broad light, neutral white balance. Left frontal portrait, centre front outfit cropped at the neck, right back outfit, same scale and ground line, face only in the portrait panel. Ban sepia, film emulation, LUTs and grain on the sheet.
- Generate base in Soul Cinema, correct in Seedream 5.0 Pro (remove freckles, crop heads out of outfit panels, soften light) while stating face, glasses and clothes must be preserved. Save the corrected asset under a short name (char_mika, loc_flat2) and reuse it.
- Locations are built around the action: three distinct seats, clear camera path, food already placed, three-quarter view for foreground, middle and background. Corrections are specific and literal (beanbag beside sofa, near side of table open, remove the motorboat).
- Recurring props get their own sheet (phone front, back, 40 degree rear; unbranded). Packaging gets a sheet too, with exact quoted wordmark and subline, and is verified against the brief.
- Cast stability words: "same single person across panels, only angle and crop change", "no beautify, no symmetrize", hands empty. Fixed accessory logic ("beanie and hood both stay on").

## 2. Directing timed scenes (posts 9, 4, 3)
- Seedance 2.5 prompt skeleton used in every long ad: REFERENCES (<<<image_1>>> = identity only, <<<video_1>>> = camera only), STYLE, LIGHTING, COLOR, CAMERA, GEOMETRY, PHYSICS, RULES (numbered), CHARACTERS plus ACTING TASKS, ACTION TIMING with shot windows, SOUND, "HOLD FOR THE FULL TIMELINE" recap. Duration, ratio and resolution are set in the generate URL, so re-check the duration field (the page can keep the old value).
- Timecodes are continuous and the last stamp equals the requested length; every spoken line fits its window; one action per window.
- Anchor each person to a landmark behind them (shelves, skylights, lamp) so seats survive angle changes. "He has the cat" does not assign a seat.
- Match cut recipe: keep subject size, pose, face position, lens, orbit direction and speed identical across the cut; change only location, light and ambience. Motivate the cut with a phone tap or a foreground wipe (an opaque back crossing the lens).
- Use a top-down blocking diagram with percentage coordinates when counts or seat positions fail; attach it to the same chat as the location photo.
- Product first, then one rack focus to the payoff; describe visible eating or action so the end has something to judge. Brand line starts at frame 1.
- Acting tasks (motive, goal, obstacle, tactic) replace "she is happy"; give the body action that carries the emotion. Never a frozen glassy stare; natural blinks.
- Tool for this: higgsfield-timed-prompts (installed). Claude drafts, you review: windows continuous, lines fit, total equals request.
- Credits in the post: Part 1 18 s, Part 2 19 s, packshot 4 s, all 1080p Seedance 2.5 (cost on the Generate button).

## 3. One camera in, many angles out (post 5)
- Film one wide stable take with clean audio, attach as a video reference, then ask for a 13-shot, 30 s Seedance 2.5 alternate-camera cut of the same performance. Output time t depicts source time t.
- Prompt blocks: reference inputs, master direction (shots, hard cuts at stated times), continuity locks (cast, seats, props), timecoded camera sequence, finish rules (no extra cuts, no music, no invented action).
- Shots mixed: dolly-back frontal, true overhead, across-glassware, bottle-mounted low angle, inside-the-glass, inclined overhead through leaves, reverse two-shot, reaction, focus pull across three layers, grass-level pet close-up, over-shoulder, clean close-up, push-in finale.
- Assets that never appear in the master (a dog) are generated separately and attached as an image.
- Workflow: write the shot schedule in plain words, ask Claude to expand it into the Seedance 2.5 prompt with locks and timeline mapping. Adds to signature-shots.md.

## 4. Blocked one-takes from 3D previz (post 3)
- Pipeline: Astra (or Claude) blocks the scene with grey shapes in Blender or in the browser with 3D Jutsu, fixes camera path, timing and staging, exports the blocking video, then Seedance 2.5 video-to-video repaints it (opening frame locks room and light, blocking drives camera, character sheet locks the person).
- Cases: infinite loop (last frame equals first, droste logic spelled out), mirror pass-through, 30 s casino one-take, desert concert (66 dancers in rings of 12, 22, 32 or 36; coloured boxes mapped to roles), one-take vacuum chase ("wall rule" for the clear bin).
- Setup: Higgsfield Blender plugin, then connect in chat with the command "@higgsfield /use-blender". Map placeholder colours to real objects in the prompt; give facing codes for crowds; state counts exactly; separate the legend from the look.
- Loop proof: verify the loop numerically in the previz rather than by eye.

## 5. Ads: formats, research and testing (posts 4, 7)
- Research before creative: buyer language, competitor ads (Meta Ad Library: when an ad started and its reach), objections, offers. Skill: create-ads-with-agents (installed). Client brief PDF first.
- E-commerce statics (Nano Banana 2, 9:16, 4K): callout diagram, review card, offer card. Check each with PROOF: Promise, Receipts, Offer, Objection, First step.
- Service ads: quiz, case story, direct offer. Check with QUEST: Qualify, Understand, Educate, Stimulate, Transition. Be specific about who you serve. Replace fictional case numbers with real, documented results.
- Videos: 5 static plus 5 video per product from one brief; outfit-change elevator, streetwear, unboxing, factory film, fashion portrait; UGC with a "friends show and tell" motive; a CGI durability test. One product, unbranded props, text added in the edit, lower-centre clear for the CTA.
- Resize for Feed, Stories and Reels by re-laying out, not cropping. Second-pass QA prompt: product accuracy, lettering, offer text, phone-size readability, continuity.
- Test: post concepts as organic Reels first, read watch and ask signals, then a paid test; feed the ad report back and make variations around winners, one change at a time.
- Cost claim (V): about $100 for every static and video in the 6-format post, mostly iterations. A UGC creator charge of $100 to $200 per ad is the comparison the post uses.
- Motion graphics over footage: instruct the editor agent to keep original cuts, duration and audio, use only provided copy, never invent prices or claims, keep graphics clear of faces and hands, check frames at phone size, deliver the MP4 plus the editable project.

## 6. Characters and influencers (post 10)
- Build a memorable character (AI Influencer builder or own photo), save the character sheet, use Genjutsu (motion control model) to swap the character into a trend clip with one unexpected twist. Prompt skeleton: keep same character, movement, camera, setting; match scale, light and contact of the added element.
- STOP idea checklist: Surprise, Tension, Outcome, Pass-it-on.
- Product integration: start from a clip where someone already holds an item; swap the item for the product photo; preserve hand action and orientation; check label against the photo.
- Brand host: audience insight, brand expertise, angle, format; build 3 references first (character sheet in Soul 2.0, product sheet in Soul 2.0, location in Soul Cinema) then Seedance 2.5 for scenes. Hold the last close-up long enough to see the product before the punchline.
- Service angle: concept ad for a launch, labelled as your own creative take, posted as a portfolio series. Claim (V): an AI influencer page reached thousands of followers in 7 days and attracted brand contacts.
- Disclosure: label AI hosts and concept ads (compliance.md).

## 7. Faceless channel (post 2)
- Stack: Higgsfield MCP or CLI plus a chat model (the post uses GPT 6 Astra) plus two skills: faceless-script-writer and faceless-video-prompts (both installed here).
- Niche logic: check RPM (what YouTube pays per 1,000 views, from VidIQ or similar); the post names finance, tech and education as higher payers; chose edutainment because evergreen.
- Script rules: original research, real insight, no template, cold open, stakes, open loops, exact numbers, present tense. 3-minute video from the script: one consistent style, voiceover, music, cuts every few seconds, 1080p.
- Package: thumbnails for A/B, titles, description, tags; two more videos on the same channel; one folder per run; weekly or 3 a week cadence (V).
- Claims (V, not verified): $39,500 a month AdSense on a similar channel; entry bar of 1,000 subscribers and 4,000 watch hours.
- YouTube risk: the policy targets mass-produced, repetitive or inauthentic content; we must add real research, real edit and AI disclosure. Never promise income.

## 8. Marketing Studio service and motion design (posts 1, 6, 8)
- Connect Higgsfield MCP as a custom connector in Claude settings; load the motion prompt skill (installed as minimax-h3-motion-design). Six sellable styles with creator price points (V): launch video $500 to $3,000 per 15 s; motion over real footage $200 to $500 per minute; hyper motion product video; real-estate 3D flythrough $2,000 to $15,000 per minute vs 7 to 8 weeks traditional; 2D explainer $300 to $800 to start; editorial explainer $1,500 to $4,000 per minute.
- Motion prompt grammar: locked camera, ease-out entrances, ease-in exits, text lock (exact quoted strings only), palette hex list, beat sheet in 1.5 to 2 s windows, copy list, content-safety and non-IP line, style-consistency rule (3D lit and physical, 2D flat fills).
- Reverse-engineer: drop a finished video into the chat and ask for the prompt that recreates its motion and text.
- Cost claim (V): about $70, 1,800 credits, one evening for all styles including failed takes, roughly $8 per video; at a $100 price that is a 95 percent margin. Our rate is about 20 credits per $1 (official), so 1,800 credits is about $90; treat margin claims as unverified.
- After Effects path: the Higgsfield After Effects plugin ("@higgsfield install after effects") builds editable layers, markers attached to moving type, beats measured from the soundtrack.
- Editing path: the post 8 skill zip is a Russian-language editor workflow tied to Resolve; not installed. Use edit-director, edit-voice and edit-gen.

## 9. Clipping (post 11)
See clipping-business.md for the end-to-end workflow, prompts, numbers, reality check and compliance.

## 10. Credit saving habits seen across posts
- Draft the cheapest shot first and fix the asset, not the prompt; iterate on assets (cheap stills) before video.
- Describe failures specifically; change one variable.
- Save the whole workflow as a skill so the next video is one command (post 2 tip).
- Re-use the same reference and music for a batch; one generate URL stores model, ratio, duration and resolution.
- Check the duration field before pressing Generate.

## 11. Top insights
1. Assets first: sheets, corrected locations, prop and packaging sheets, then scenes.
2. Long timed prompts with locks and a recap line beat short prompts for multi-shot ads on Seedance 2.5.
3. One wide take can become 13 angles by prompting camera only.
4. Grey-shape previz fixes camera and timing for 30 s one-takes.
5. Frameworks (STOP, PROOF, QUEST) make ideas testable.
6. Research and testing precede spend; organic first, then paid.
7. Income claims are vendor claims; sell packages with defined scope and verify every number ourselves.
