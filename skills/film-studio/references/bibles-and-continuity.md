# Bibles and continuity (Phase 2, enforced in Phase 3)

Rule: assets first, prompts second, video third (Higgsfield academy practice, 3P). A bible is a text block plus reference images; both are reused verbatim in every prompt. Drift is harder to catch in locations, props and wardrobe than in faces. Owner: tech-writer writes, creative-director approves, qa-tester audits.

## 1. Style bible (one per film; the shared header)
```
STYLE-BIBLE v1 | locked YYYY-MM-DD
Look family: [e.g. 3D feature animation, soft subsurface, warm bounce light]
Reference frames: 6 to 12 approved stills (file ids)
Medium cues: [film stock or render engine words; grain, halation, line weight]
Lens language: [focal lengths used, aperture, anamorphic yes/no]
Camera rules: [handheld ratio, preferred moves, forbidden moves]
Palette: [5 to 8 named colours with hex; shadow, mid, highlight tint]
Light rules: [key direction convention, time of day looks per sequence]
Aspect and frame rate: 2.39:1 or 16:9, 24 fps
Negative list: [no text in frame, no plastic skin, no extra fingers, no lens flare unless scripted]
Style header (paste into every prompt, 40 to 70 words): ...
```
Edit the header once, never per prompt. If a second model is used, keep header identical and add a model-specific suffix.

## 2. Character bible (one page per recurring character)
```
CHAR-001 NAME | role | age | locked YYYY-MM-DD
Identity text block (60 to 90 words, front-loaded, reused verbatim): face shape, skin tone and undertone, eyes, hair, build, height vs others, distinguishing marks
Wardrobe sets: see WARD-xxx
Voice: language, accent, pitch, pace, voice profile id, sample file
Movement and habits: gait, gestures, tics, expression range
Emotion range stills: neutral, joy, anger, fear, sorrow, deceit (6 images)
Reference set: front, 3/4 left, 3/4 right, profile, full body, close-up (plain grey, ONE face each); 20 or more images if training Soul ID or similar
Age variants: if the story spans years, one block per age
Relationships: who towers over whom, who touches whom
Consent: original character OR written consent id for any real likeness
Ethnic and regional specifics: use asian-human-reference regions-and-appearance.md; state skin tone explicitly and never lighten
```
Non-human leads: add turnaround, scale vs human, material and motion rules (how it moves, weight, speed).
Animated styles: model sheet with fixed line weight, proportions in head-heights, expression sheet, hands sheet.

## 3. World bible
```
WORLD v1 | era | place | tech level | rules of the world | social structure | architecture language | flora and fauna | signature sounds | forbidden anachronisms | research file links
```
Fantasy and sci-fi: write what is impossible, what it costs, and the one visual motif repeated across locations. Period: link the research file (genres-and-styles.md section 6).

## 4. Location bible (one card per location)
```
LOC-014 Old Harbour Warehouse | INT/EXT | scenes SC12, SC13, SC41
Master plate images: wide, 3/4 left, 3/4 right, detail (4 stills, 3/4 angles, no people)
Layout map: top-down sketch with door, window, furniture, camera zones; screen-direction notes (where the sun enters, where the exit is)
Light by time of day: dawn, day, dusk, night (text plus plate)
Dressing list: fixed items with positions
Weather and season variants
Sound: ambience bed id
Lock test: hero character generated in the plate and approved (do this before locking)
```

## 5. Wardrobe bible
```
WARD-003 Meera | set B "work day" | scenes SC05 to SC11
Items: garment, fabric, colour (hex), pattern scale, fit, accessories, footwear, jewellery, hair styling
Condition arc: clean, dust, torn sleeve after SC09 (damage persists until a scripted change)
Era check: source note for each item
Image: front and back plate on plain grey
```
Garment count per character is a production cost: aim 3 to 6 looks per lead.

## 6. Prop bible
```
PROP-021 Brass compass | hero prop | scenes SC03, SC19, SC52
Dimensions vs hand, material, wear state per scene, left or right hand carry, who holds it when
Views: front, 3/4, back, scale-in-hand
Rule: one instance per frame; no duplicate props; text on props added in edit
```

## 7. Shot ID scheme
`S##-SC##-SH###[-T##]`
- S = sequence (01 to 12), SC = scene within film (01 to 60), SH = shot within scene (001 to 999; step by 10 on first pass so inserts fit: 010, 020, 025).
- T = take (T01, T02...). Approved take is marked in the ledger, not by renaming.
- Related IDs: `AUD-S03-SC07-SH020-DLG` for audio, `FX-...` for repairs, `ALT-...` for alternates.
- File name: `S03-SC07-SH020_T04_seedance25_720p_v1.mp4`. Never reuse an ID.

## 8. Shot list row (minimum columns)
`id | scene | location id | characters | wardrobe id | size | angle | lens | move | action (one) | dialogue ref | start frame source | end frame target | model | est secs | status | notes`
Format details and boards: previs-storyboard.md.

## 9. Continuity ledger (one file per sequence, `ledgers/S03.csv` or md; one row per shot)
```
shot_id | time_of_day | weather | screen_dir (L>R/R>L) | char_pos | wardrobe_state | injuries_dirt | props_in_hand | prop_positions | eyeline | light_key_dir | lens | grade | audio_bed | prev_last_frame_ok | next_first_frame_ok | flags
```
Rules:
- The ledger is written from the shot list before generation (planned) and corrected from the approved take after QA (actual).
- Persistent state changes (a cut, a lost glove) are logged at the shot where they occur and carried forward until reversed.
- Screen direction: keep the travel direction and the 180-degree line constant within a scene; log any scripted crossing.
- qa-tester diffs planned versus actual per sequence and signs the lock.

## 10. Locks per sequence (written at G3)
`locks/S03.lock.md`: style header version, character block versions, location plates ids, wardrobe ids, prop ids, model and version, seeds if exposed, grade LUT id, voice profile ids, list of approved takes with hashes. A change after lock needs a change note and re-QA of affected shots.

## 11. Common drift causes and fixes
Face drift between cuts: re-anchor with the reference set and Soul ID; cut on a different angle. Costume shift: wardrobe plate in every prompt, name colour and pattern, repair with video-to-video. Location creep: regenerate from the plate, not from text. Prop duplication: one-instance rule and insert shots. Lighting jumps: same key direction and time word; grade pass last. Age or weight drift: age-variant blocks.
