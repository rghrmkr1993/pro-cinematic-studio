---
name: cinematography
description: "Prompt compression for AI video: verified prompt length limits per model, how models weight prompt order, a slot-and-budget method to fit a rich scene into 512 characters, six before and after examples, and the 512 check. Part of the cinematography skill."
---

# Prompt compression (fit a scene into 512 characters)
Labels: (V) vendor-official, (3P) third-party, (H) house rule. Verified 2026-10-14. Use when a tool caps the prompt, when credits matter, or when a long prompt dilutes the shot.

## Verified prompt limits
| Tool | Limit | Evidence |
|---|---|---|
| Higgsfield Cinema Studio 2.5 and 3.0 | 512 characters in the prompt field; in 2.5 each @ Element chip eats about 80 to 100 hidden characters, max 2 tags; 3.0 references are media inputs and may cost less | 3P only (OSideMedia higgsfield-cinema skill, one repeat). No Higgsfield page states it. [verified as a 3P claim, 2026-10-14] |
| Higgsfield Cinema Studio 4.0 | No cap published. Higgsfield's own 4.0 blog prints a "Prompt used" of about 3,400 characters, and its Seedance 2.5 guide prints prompts of 4,900 to 7,000 characters | V (higgsfield.ai/blog/cinema-studio-4-0 and /blog/seedance-2-5-prompting-guide; the help center page has no limit text). [no public source for a hard 4.0 cap as of 2026-10-14; checked: help center, 4.0 blog, API playground page, OSideMedia repo, search for user reports] |
| Seedance 2.5 and 2.0 | No hard cap in any official page read. Official guidance: 60 to 100 words per clip for 2.0 (write-up of the Volcengine guide); one third-party API page says about 2,000 characters | [no public source for an official cap as of 2026-10-14; checked: suno.bi, Sogni docs, BytePlus prompt guide and tutorial (client-rendered, empty), apiyi, nxcode] |
| Kling 3.0 | API: 3,072 characters hard, 2,500 recommended; multi-shot: 512 characters per shot, 1 to 6 shots | V Kling API reference as quoted by search results (the page renders client-side and could not be fetched); some resellers enforce 2,500 |
| Veo 3.1 | 1,024 text tokens, about 4,000 characters at 4 characters per token | V Gemini API docs (ai.google.dev/gemini-api/docs/veo) |
| Nano Banana Pro (Gemini 3 Pro Image) | 65,536 input tokens, 14 reference images at 560 tokens each | V Gemini API and Vertex model pages |
| Runway Gen-4.5 | Not published on pages that could be read | [no public source as of 2026-10-14; checked: Runway help center (403 to fetch), Gen-4 prompting guide, third-party specs]. Runway says keep prompts simple |

House tiers (H): 512 is the safe cap for any Cinema Studio version and for every Kling multi-shot beat; 1,000 to 1,500 characters is the working ceiling for 4.0 and Seedance until the live counter proves more; a clip still holds only one move and one action, so length rarely helps. Always read the character counter in the live field; limits change by version.

## What models read (research summary)
- Order: models are said to weight the opening of a prompt most. Many blogs repeat this but no vendor doc states it, so it is a heuristic (3P). Test it.
- Vendors disagree on the first slot. Veo docs list subject, action, style, camera, composition, focus, ambiance (V). Kling guidance opens with subject and movement, camera later (3P). Runway wants motion-first plain prose (V). Higgsfield's Seedance 2.5 guide opens with global style, then scene, characters, location, shots, optics, physics, lighting, audio (V). The Seedance official order is asset references, one-sentence summary, timed plot, closing constraints (3P write-up).
- House rule (H): when hardware sits in the Cinema Studio panel, open with subject and action and place the camera move in the first half. A camera move placed late in a long prompt is the one most often dropped (3P Seedance guides).
- Models mostly ignore quality filler ("8k, masterpiece, award-winning, ultra detailed"), adjective stacks beyond two, polite or conversational phrasing, and numbers they cannot render (a lighting ratio of 8:1). Higgsfield's own guides leave them out (V).
- Negatives are unreliable. Runway says negative phrasing is not supported and may give the opposite result; write "locked camera" not "no camera movement" (V Runway Gen-4 guide). Keep only short audio exclusions such as "no music" where the model makes audio (V Higgsfield).

## Compression method
1. Write the long version once. Mark what the viewer must see (story change, product, face); the rest are cut candidates.
2. Fill seven slots in this order. Budget per slot in characters, 460 in total, 52 spare:
| Slot | Budget | Holds |
|---|---|---|
| 1 Subject and action | 130 | Who or what, one action, start to end pose |
| 2 Setting | 55 | Place plus 2 or 3 anchors |
| 3 Camera | 80 | Size, lens mm, one move with speed |
| 4 Light | 70 | Source, direction, quality, Kelvin |
| 5 Colour and look | 45 | 2 colours, grain or stock |
| 6 Realism cue | 40 | Pores, sweat, fabric weight, dust, breath |
| 7 Audio | 40 | Ambience, one sound, "no music" (only if the model makes audio) |
3. Keyword rules: digits not words (50mm, 3200K, 5s, 120fps); abbreviate units only and spell shot sizes ("close-up"); one noun phrase per anchor; motion verbs with a speed ("slow push-in over 5s"); drop articles and words like "very", "beautiful", "stunning".
4. Highest-signal words: shot size, mm and f-stop, one move verb with speed, light source plus direction plus Kelvin, two colours, concrete physical nouns, an exact first and last pose. Lowest signal: mood adjectives, "cinematic", "epic", resolution words.
5. Cut list, in order: quality filler, negatives, duplicate adjectives, a second subject action, a third environment detail, camera brand and body (use the panel), lens words that repeat the panel, backstory, anything the reference image already shows.
6. Offload to references (V Higgsfield Elements): faces, wardrobe, product, location and style go to Elements, a first frame or reference images, and the text keeps only the verb. Hardware (camera, lens, aperture, genre, colour palette, lighting preset) goes in the Cinema Studio panel, not the prompt.
7. Counting with Elements: in 2.5 subtract 80 to 100 per @ chip. Two chips leave about 310 visible characters.
8. Split when it does not fit: one clip carries one move and one action. Cut the scene into timed beats of 4 to 8 s, each its own 512-character prompt (`Shot 1 (0-5s)`, `Shot 2 (5-10s)`), chained by last frame. Kling multi-shot takes up to 6 beats of 512 each (V). Restate setting and light in every beat so the cuts match (H).
9. Run the 512 check below. Over by under 30 characters: cut slot 6 or 7 first. Over by more: split.

## Six before and after examples
Counts were measured with Python len(). The originals are padded with the filler models ignore; each compressed prompt keeps every visible story beat. All content is invented and client-neutral.

### 1. Product pour (skincare, generic)
Before (987 characters, over budget): A beautiful, ultra detailed, 8k cinematic close-up of a luxurious golden facial serum being slowly poured from an elegant amber glass dropper bottle onto the fingertips of a woman with flawless glowing skin, in a bright, minimal, airy white bathroom with a marble counter and a soft green plant in the background. Gorgeous soft natural window light from the left creates lovely highlights on the glossy liquid. Warm cream and gold colour palette, shallow depth of field, shot on a professional cinema camera, very realistic, smooth slow motion, relaxing spa atmosphere, no text, no logo, no distortion. The camera starts on the bottle label, then drifts down to the hand. The bathroom has a frosted window, folded white towels, a wooden tray with a ceramic dish, a hint of steam and a sense of calm self-care. Make it feel premium, expensive, award-winning commercial quality, perfect, masterpiece, 4k, hyper realistic, smooth, no blur, no watermark, no extra fingers, no deformed hands.

After (397 characters):
`Macro, 100mm f/2.8, slow drift from label to hand. Golden serum drips from an amber glass dropper onto a woman's fingertips, one thick bead stretching in 120fps slow motion. White marble counter, soft plant blur. Soft window light from left, 5000K, specular glint on the liquid. Cream and gold palette. Real skin pores, fine grain. Soft drip foley, no music. Towel and tray soft in the background.`

### 2. Street dialogue (Indian setting)
Before (901 characters, over budget): An incredibly cinematic and emotional medium close-up of an old, kind tea seller in his fifties who is pouring hot tea from a great height into a small glass while smiling warmly at a young customer who is replying to him, set in a very narrow, busy, colourful old lane in Chennai during the evening, with a steaming steel kettle, hanging bulbs, and lots of atmosphere. Beautiful warm tungsten light with a deep blue dusk sky, teal and amber colour grade, handheld camera feel, realistic natural skin with sweat, authentic street sounds, and speech in Tamil. Behind him there are glass jars of biscuits, a faded film poster, a scooter, scattered banana leaves and wet ground from earlier rain. People walk past in the background. Cinematic masterpiece, 8k, ultra sharp, shallow depth of field, anamorphic lens flare, award winning, perfect faces, no subtitles, no text, no extra people, no distortion.

After (390 characters):
`Medium close-up, 50mm, handheld. A tea seller in his 50s pours tea from a height into a glass and smiles at a young customer who answers. Narrow Chennai lane, steaming steel kettle, hanging bulbs. Warm tungsten practicals 3200K under a blue dusk sky. Teal and amber, light grain. Natural skin, sweat sheen. Street ambience, kettle hiss, one line in Tamil. Background walkers softly blurred.`

### 3. Rain alley fight
Before (885 characters, over budget): An epic, intense, super dynamic fight scene shot from a dramatic low angle with a wide lens in a dark, rainy, neon-lit alley at night, where two fighters violently trade fast punches and kicks, one throwing a big hook while the other ducks under it and counters with an elbow, with rain spraying everywhere, wet asphalt reflecting neon signs, steam rising from vents, cold cyan backlight and red neon fill light, gritty teal and red colour grade, heavy film grain, realistic fabric weight and motion blur, loud impacts, rain and thuds, no music. The alley has dumpsters, fire escapes, flickering signs in Japanese and Hindi, puddles that splash, and a stray cat running away. Camera should feel powerful and cinematic with dramatic slow motion at the moment of the elbow, ultra detailed 8k, hyper realistic, masterpiece, perfect anatomy, no blood, no extra limbs, no morphing, no cuts.

After (375 characters):
`Wide, low angle, 24mm, locked. Two fighters trade fast strikes in a rain-soaked alley: one throws a hook, the other ducks and lands an elbow, rain spraying off them. Neon signs, wet asphalt, vent steam. Cold cyan rim light from behind, red neon fill. Teal and red, gritty grain. Real fabric weight, real-time 24fps. Impact thuds, rain, no music. One continuous take, no cuts.`

### 4. Awe landscape, crane reveal
Before (900 characters, over budget): A breathtaking, majestic, ultra wide cinematic crane shot of a lone trekker slowly climbing a snowy Himalayan ridge toward the rising sun, while the camera gracefully rises up and up to reveal an enormous sea of clouds filling the valley below, with colourful prayer flags snapping in the wind, golden hour backlight with long shadows and a light haze, warm gold against cool blue, fine film grain, realistic wind-blown jacket and visible breath, the sound of wind and crunching snow, epic atmosphere, no music. Fluttering prayer flags in red, blue, yellow and green hang over the ridge, with dark rock outcrops, distant peaks and drifting clouds layered in the background. The trekker wears an orange jacket, a backpack and trekking poles. Make it stunning, epic, cinematic, award-winning documentary quality, 8k, ultra detailed, hyper realistic, no logos, no text, no drones in frame, no jump cuts.

After (367 characters):
`Extreme wide, 16mm, slow crane up. A lone trekker climbs a snow ridge toward sunrise; the frame rises to reveal a cloud-filled valley. Prayer flags snap in the wind. Low golden backlight 3500K, long shadows, light haze. Warm gold against cool blue, fine grain. Wind-blown jacket, visible breath. Wind and crunching snow, no music. Orange jacket pops against the snow.`

### 5. Food, hero cooking beat
Before (894 characters, over budget): A mouth-watering, ultra detailed, 4k cinematic close-up of a skilled cook spreading golden dosa batter in a perfect circle on a sizzling hot iron griddle in a busy traditional tiffin kitchen full of steel utensils, the edges crisping up beautifully as steam rises, lit by warm overhead tungsten light with soft window fill from the side, rich saffron and brown colour palette, shallow depth of field with a slow gentle push-in, oil glistening, crisp texture, loud sizzle and ladle scraping sounds, appetising atmosphere. In the background a second cook stirs a big pot of sambar, there are stacks of steel plates, coconut chutney in a bowl, hanging chillies and a wall calendar. The cook wears a white cotton shirt with rolled sleeves. Appetising, delicious, hyper realistic, ultra sharp, masterpiece, 4k, award winning, no text, no extra hands, no distortion, no cartoon look, no plastic food.

After (378 characters):
`Close-up, 85mm, slow push-in. A cook spreads golden dosa batter into a circle on a hot iron griddle, edges crisping, steam rising. Busy tiffin kitchen, steel utensils blurred. Warm overhead tungsten key 3200K, soft window fill. Saffron and brown palette, shallow focus. Oil glisten, crisp lace edges. Sizzle, ladle scrape, no music. Wall calendar and chutney bowl in soft focus.`

### 6. Emotional close-up, night ride
Before (883 characters, over budget): A deeply emotional, heartbreaking, beautifully lit cinematic extreme close-up of a young woman sitting in the back of a moving auto-rickshaw at night with tears slowly forming in her eyes, first looking out at the glowing city and then turning to look straight into the camera, with streaking city lights outside and a passing streetlight that gently sweeps across her face, muted blue and amber colours, film grain, shallow depth of field, realistic unretouched skin and wet eyelashes, engine hum and distant horns. The rickshaw has a yellow canvas roof, a hanging garland, a small dashboard idol, and rain-spotted plastic side curtains flapping in the wind. Make the performance subtle and truthful, not melodramatic. Cinematic masterpiece, award-winning, 8k, ultra detailed, hyper realistic skin, perfect eyes, no text, no subtitles, no distortion, no extra people, no fake tears.

After (349 characters):
`Close-up, 85mm f/1.8, static. A young woman in the back of a moving auto-rickshaw, tears forming; she looks out, then straight into camera. Night city lights streak past. A passing streetlight sweeps her face, soft 4000K. Muted blue and amber, grain. Unretouched skin, wet lashes. Engine hum, distant horns. Rain-spotted yellow canvas curtain flaps.`

## The 512 check
Save the final prompt to a file and count it. Spaces count; strip the editor's trailing newline; read as utf-8 on Windows:
`python -c "import sys;print(len(open(sys.argv[1],encoding='utf8').read().strip()))" prompt.txt`
Plain form: `python -c "print(len(open(f).read()))"` with `f` set to the file name. It counts a trailing newline, so subtract 1 if the editor adds one. Pass is 512 or fewer; with 2.5 chips, pass is 512 minus about 90 per chip. Log the count in the shot list next to the shot ID.

## Checks before spending credits
- Subject first, camera in the first half, one move, one action, positive wording.
- Every adjective earns a visible result; filler removed.
- Identity lives in the Element or reference, not in words.
- Count passes and the live counter in the tool agrees.
