# AI prompting for realistic people (researched 2026-10-13)
Labels: (V) vendor-official, (3P) third-party or community guide, (E) estimate or rule of thumb, (U) unverified or conflicting. Almost all model tips below are 3P and version-specific: test side by side before standardising. Generic model mechanics live in higgsfield-master/references/model-dialects.md; this file holds only the realism layer.

## 1. Prompt anatomy for a photoreal person
Order: (1) framing and camera, (2) subject identity with 2 to 3 anchors, (3) skin and imperfection cues, (4) eyes, (5) hair, (6) wardrobe, (7) environment with 3 anchors, (8) one light source with direction, (9) grade, grain, film, (10) constraints.
Rules: subject early (models weight early tokens, 3P); describe the photo you want rather than quality adjectives; replace complaints with concrete descriptions (say "visible pores across the nose, slight sheen on the forehead" instead of "not plastic"); keep Soul-type prompts short (under about 100 words, 3P) and Seedance 60 to 100 words.
Template: "[Candid portrait], [85mm f/2], [woman, late 30s, medium wheatish skin with warm golden undertone, dark brown eyes]. Visible pores on nose and cheeks, faint expression lines, slight under-eye texture, a small mole near the jaw, natural left-right asymmetry, fine peach fuzz in the backlight. Dark brown hair with flyaways and a few grey strands. Cotton kurta. Sitting by a north-facing window, soft daylight from camera left, neutral white balance. Unretouched, fine 35mm grain, natural colour. No text, no watermark."

## 2. Camera, lens and film language
- Framing: headshot, bust, three-quarter, full body; eye-level or slightly above for flattering; phone-selfie arm-length for UGC.
- Focal length: 24 to 35mm environmental or UGC, 50mm natural, 85mm flattering portrait, 100mm and up strong compression (3P). Wide lenses up close distort noses and add a tell; 85mm is the safe default.
- Aperture: f/1.4 to f/2.8 isolates, f/4 balanced, f/8 to f/11 deep focus; UGC and phone looks are deep focus (higgsfield house rule). Real shallow depth keeps the focus plane on the nearest eye.
- Body class: "full-frame mirrorless", "phone camera" or "35mm film SLR" steer texture; named bodies and lenses ("85mm f/1.4 on a mirrorless body") appear in many guides, (3P) and change composition more than sharpness.
- Film stock words: Kodak Portra 400 (warm, soft skin, lifted shadows), Fuji Pro 400H (cool pastel greens), Kodak Ektar (saturated), CineStill 800T (halation, tungsten), Tri-X (b/w grain). Use sparingly: film words add grain and colour shifts, which also hide plastic skin (3P). For commerce keep the grade neutral.
- Sensor and lens flaws: fine noise in shadows, slight chromatic fringe at edges, a mild vignette, soft corners; these read as optics, not as filters.
- Registers: "unretouched candid frame", "unedited RAW file look" (3P), "phone photo, slightly overexposed window" for UGC.

## 3. Lighting setups for skin (photography guides, rule-of-thumb angles)
| Setup | Position | Skin effect | Use |
|---|---|---|---|
| Soft window light | large window, camera left or right, 30 to 45 degrees | gentle falloff, honest texture | default for UGC and lifestyle |
| Loop | 30 to 45 degrees, slightly above eye line | small nose shadow toward the cheek | safe all-rounder |
| Rembrandt | about 45 degrees, above eye line | triangle of light on the shadow cheek, more texture | editorial, drama |
| Butterfly | in front and above | symmetrical, shadow under nose | glamour, beauty |
| Clamshell | key above, reflector or fill below, fill about 2 stops under key | even smooth skin, catchlights low and high | beauty, skincare close-ups |
| Split | 90 degrees to the side | half face in shadow, strong texture | drama only |
| Backlight or rim | behind and above | vellus halo, ear translucency | depth, golden hour |
Ratios: a reflector close gives about 2:1 soft shadows, none gives about 4:1 dramatic. Larger, closer sources soften; small hard sources exaggerate pores. Name the source, size, direction and colour temperature once ("soft overcast window light from the left, 5600K"); mixed or unnamed light produces contradictory shadows. Skincare imagery: use diffuse large sources and do not light in a way that overstates results.

## 4. Imperfection cues and anti-patterns
Positive cues: pores, fine facial hair, faint freckles, uneven redness, under-eye texture, asymmetry, lip creases, flyaway hair, visible knuckle creases, a small mole, faint sheen, slight skin shine on T-zone, a crooked tooth, creased fabric, lint, a scuffed nail polish.
Negative or constraint tail (use as a short positive line where the model has no negative field, for example Flux 2, 3P): "no plastic or waxy skin, no airbrushing, no beauty filter, no over-sharpening, no HDR glow, no symmetrical face, no extra fingers, no text, no watermark, no 3D or CGI look."
Anti-patterns (3P, consistent across sources):
- Quality-keyword stacking (photorealistic, 8K, ultra detailed, masterpiece): does little or adds a render look.
- Beauty words: flawless, perfect, radiant, glowing, glass skin, porcelain.
- Beauty-tuned LoRAs or "cinematic" presets without a photographic anchor.
- Over-long prompts with contradictory lights and styles.
- Over-sharpened or heavy "enhance" passes that re-smooth skin.
- Stacking a dozen imperfections (looks diseased).
- Extra people and beats in one frame (identity and hand failure).

## 5. Per-model realism dialects
- Nano Banana Pro or 2 (Gemini image): explicit texture line in any face prompt ("preserve natural skin texture and pores"); structured prompt with a texture-realism line, defects to avoid, output size and ratio; exact counts and layout; for edits say "maintain skin character, keep freckles and fine lines" and "subtle retouch while preserving pores"; with face references, end with the smoothing negatives; up to 14 references in Higgsfield, name each role (V for refs, 3P for the rest). Generate lower and upscale if blurry.
- Flux 2 (and Kontext for edits): no negative-prompt workflow in the guides, so use a short positive constraints line; literal and direct prompts; subject first; name lens and film; avoid "flawless, perfect symmetry"; a lower guidance value (2.0 to 3.0) is suggested for skin on the flex variant by one source (U, single source).
- Midjourney v7: natural-language sentences; `--style raw` is the main anti-beautification switch; keep `--s` low, with sources ranging from 0 to 50 up to under 200 (U, conflicting); `--chaos` 0 to 20 for consistent portraits; `--oref` with `--ow` for identity; naming a lens changes composition (3P). Treat `--q` and "8K" claims as unproven.
- Seedream 4.5 and 5.0: use physical, photographable terms; name light source, direction, softness, temperature; one test found 4.5 better on skin realism and 5.0 sharper with a stronger AI look and better on prompts with many elements (U, single vendor test); register matters, "smartphone photo" for candid versus a retouch look for fashion. Best de-slop editor: "keep composition and subjects exactly; change only micro-realism; avoid waxy skin, HDR glow, oversharpening" (house rule).
- Soul 2.0 (Higgsfield): short prompts, let a preset or Moodboard carry style; Soul ID plus character strength (0 to 1) for likeness; save seeds; use an instruction to keep real facial structure and not beautify when working from a consented reference; Moodboard needs 20+ cohesive images without faces (V and 3P).
- GPT Image: good at colour and text accuracy; use for sheets and on-image copy, then run a skin check.
- Veo 3.1: cinematic paragraph with micro-actions ("a breath catches, eyes shift, a small pause"); audio line with quoted dialogue; close-up faces can soften, use medium shots; 4 to 8 s clips; avoid brand names and real people (3P).
- Kling 3.0: staged expression changes ("neutral, brows lift slightly, eyes widen, smile begins"); ask for wrinkles, skin texture and eye glint rather than "a face"; strong camera control; vendor blogs report identity drift after about 6 s (U); Start and End Frames anchor motion (V).
- Seedance 2.0 and 2.5: image-to-video from a still that passes QA; identity in an Element or @character, action in the prompt; single camera move; 60 to 100 words; load `seedance-20` for syntax.
- Wan, Hailuo: strong on short realism tests and facial emotion (3P); use first and last frames.

## 6. Upscale and detail-pass workflow (3P guides)
1. Generate at the model's native resolution; do not push "4K" in the prompt for blurry output.
2. Clean first (denoise lightly): upscaling turns noise into false texture.
3. Pick the tool by risk. Faithful (Topaz-style) keeps identity and tone; generative (Magnific-style, SUPIR, Clarity) invents detail and can change skin tone, ethnicity or bone structure at high creativity.
4. Settings that sources suggest as a start: 2x with a face-aware model; creativity about 2 to 4 of 10; resemblance about 7 to 9; HDR off; avoid 4x to 6x on faces; prompt describing the scene (E, from vendor blogs).
5. Skin pass: seed or inpaint pores with a conservative generative pass, blend over the original on skin only, optional frequency separation to restore texture.
6. Add fine grain and a camera-profile grade last, uniformly over the frame.
7. Compare before and after at 100% on nose, forehead, eyes; verify tone patch unchanged and no new teeth, fingers or text; reject if identity shifts.
8. Inpaint faces, teeth and hands locally rather than rerolling the whole frame. Every pass softens detail, so do the fewest passes.

## 7. Video realism
- Micro-expression: write small staged beats, not "smiles": neutral, a slight brow lift, eyes shift, mouth corner rises, settle. Keep one emotion per clip, tie it to a visible action.
- Breathing: slow chest and shoulder rise, faint nostril and neck movement, 12 to 20 breaths per minute at rest (E); a barely visible rise is enough.
- Blink rate: about 15 per minute at rest, about 10 to 12 reading, about 25 to 30 or more while talking, with large individual variation; blinks cluster at pauses and sentence ends (physiology literature, 3P summary). In prompts say "blinks naturally at pauses"; tells are no blinking, constant blinking, mechanically regular blinks or asymmetric blinks.
- Gaze: saccades and small shifts, glance away to think; no fixed stare; both eyes same direction.
- Head and neck: small tilts, weight shifts, jaw and neck tendons move when speaking, shoulders breathe; avoid a statue head with a moving mouth.
- Motion blur: a 180 degree shutter equals 1/(2 x fps), for example 1/48 s at 24 fps; fast motion shows blur, slow motion stays crisp; say "natural motion blur on fast hand moves".
- Rolling shutter (phone footage): skew on fast pans or swung objects, jello on vibration; add only for phone or UGC looks and only on fast moves.
- Handheld: low-frequency sway plus small corrections and slight breathing in the frame; "handheld micro-sway", "slight handheld breathing" (3P). Avoid stabilised gimbal glide when claiming handheld, and avoid shake that hides faces.
- Speech: jaw, lips, cheeks and throat move together; lip sync on plosives (p, b, m close the lips); check teeth visibility.
- Hair and cloth: physics respond to head turns, hair lags slightly, no clipping through shoulders.
- Continuity: lock light, grade, wardrobe, hand job per beat; chain clips by last frame; same skin tone across cuts; re-check identity at the 5 to 8 s mark; one variable changes between shots; start the next clip from the best frame, not the last-generated drift.
- Audio: room tone, cloth rustle, breath and mouth sounds make faces believable; no lyrics.

## 8. Product realism in the same frame
- Labels: generate packaging text-free and composite the real label, or use a front packshot reference; never enlarge the product to make text readable; check text, barcode, cap logic and shape in a frozen frame (house rule). Lock the pack via references; one hero product per frame.
- Glass: refraction through thick walls, bright edge highlights, rim thickness at the base, a soft contact shadow, fingerprints and a faint dust speck for realism; the reflected light matches the scene source.
- Liquids and oils: a meniscus at the surface, a thin translucent amber strand from a dropper, highlight streak following the curve, small bubbles; viscosity must match the real product.
- Creams and balms: soft peaks with a glossy ridge, ribbon fall that holds shape, slight sheen, sparse air pockets, a spread streak showing translucency on skin.
- Soap lather: bubbles of mixed sizes with thin iridescent films, dense creamy centre, wet foam sliding between fingers, water drips; bar soap is matte with cut face grain.
- Application on skin: product thins and absorbs, the sheen fades, skin underneath keeps its pores; the amount shown is honest to a real dose.
- Honesty: textures, colours, lather or absorption shown must match the real product; do not show a result or finish the product cannot deliver; claims go through the qualified team (house rule).

## 9. Iteration rules
Change one variable per round. 4 of 4 bad takes: rewrite the prompt or switch model. One bad take: reroll or inpaint. Keep a take ledger (prompt, seed, model, score). Save the best frame as a style and identity anchor for the series.

## 10. Higgsfield 3-step realism workflow (creator blog, 2026)
Source: @adilinthewildtempo, published 2026-10-07 (3P creator post on higgsfield.ai, read 2026-10-13). The title says realism; the body is an asset-first, directed 3-stage ad build (a 3-friend food-delivery commercial). Results and costs are creator claims (U). Recipe form: higgsfield-master workflows.md recipe 12.
Stages and models stated: Soul Cinema for character and location bases; Seedream 5.0 Pro to correct them and to make props, packaging and an overhead blocking diagram; Claude writes the prompts (skill: higgsfield-timed-prompts, installed); Seedance 2.5 generates the video takes; selected moments are cut together.
Step 1, build reusable assets (approve each asset before any scene):
- Character sheet, 3 panels in one row on seamless neutral mid-grey: frontal head and shoulders, front outfit cropped at the base of the neck, back outfit, identical scale and ground line, face only in the portrait. Settings seen: soul_cinematic, 16:9, 1080p for the base; seedream_v5_pro, 16:9, 2k for the corrected sheet.
- Sheet prompt blocks: "real photograph, documentary-grade realism" plus a top-priority colour rule (neutral white balance, true colours, no sepia, no warm cast, no film emulation, no LUT, no grain); identity (age, skin with visible pores and natural tonal variation, no airbrushing, no plastic smoothing); hair; wardrobe item by item with "no bag, no phone, empty hands"; panel instructions; flat soft broad light, matte skin, no reflections in glasses; "same single person across all panels, only angle and crop change"; a negatives tail (no CGI skin, no beauty retouch, no text or labels).
- Check before moving on: glasses, hands, skin texture, silhouette. Fix with a specific Seedream edit (remove freckles, crop heads out of the outfit panels, soften light, keep face, glasses, clothes). Save as char_name.
- Locations: build around the action (seat count, camera path, food already placed), three-quarter view with foreground, middle and background; Soul Cinema first, Seedream edits for counts and clutter; save as loc_name. State exact counts in text ("exactly three chairs, three plates").
- Recurring props and packaging get product sheets (front, back, 40 degree rear, unbranded) with quoted wordmark text; one group image keeps a band of four distinct musicians together.
Step 2, direct timed scenes (Seedance 2.5, 1080p, 16:9; model, ratio, duration and resolution live in the generate URL):
- One prompt per scene: cast block repeated verbatim, prop block, a location block per place, a LOOK line (lens range 16 to 28 mm, natural colour, realistic skin, physically plausible camera), SHOTS in continuous windows (0.0-1.5 s, 1.5-3.0 s and so on), SOUND (dry close dialogue, ambience, no score unless a scene needs live music), CONTINUITY (one phone, no visible screen, same clothes, seats fixed).
- Durations used: 18 s, 19 s and a 4 s packshot. Check the duration field before generating; the page can keep the previous value.
- Dialogue lines carry exact timestamps and are spoken once; finish speech before an off-camera sound cue.
- Cuts: match cut on a tap with matched subject size, pose and orbit speed; foreground wipe by an opaque back crossing the lens; the same camera move carries over the cut.
- For layout failures add a top-down blocking diagram with percentage coordinates and attach it with the location photo.
Step 3, land the brand: packshot readable first, one rack focus to the payoff action (a cat eating), voice-over from frame 1, friends soft in the background, packaging count and colour stated, no music, no captions.
Directing lessons (creator): anchor each person to a landmark; an overhead view must not swap seating; check the number of place settings before judging acting; describe visible action (head lowers, food shifts, bite, chew) so the payoff can be judged.
Conflicts with our rules and resolution (official Higgsfield docs and Academy win):
1. Prompt length. Official dialects say Seedance 60 to 100 words and one camera move. The post uses 500 to 1,000 word timed prompts. Resolve: 60 to 100 words for single Seedance 2.0 shots and drafts; long timed prompts only for Seedance 2.5 multi-shot scenes with locked asset references, as the Academy ad pipeline does with a prompt-builder skill and one shared style header.
2. Person base model. Our tree sends people stills to Soul 2.0 and cinematic stills and locations to Soul Cinema. The post uses Soul Cinema for character bases. Resolve: Soul 2.0 (or Soul ID) for realistic people we rely on; Soul Cinema bases are acceptable for fictional cast if the sheet obeys the neutral-light rules above.
3. Text in generation. Golden rule 13 says never bake text or logos. The post bakes a quoted wordmark into a packaging sheet with Seedream 5.0 Pro. Resolve: keep rule 13; in-frame text only for a prop that must read, with Nano Banana Pro or GPT Image if possible, and check every letter in a frozen frame (Seedream text accuracy is not confirmed officially, U).
4. Edit passes. We warn that every edit pass softens detail. The post uses a Seedream edit to fix sheets. Resolve: allowed on sheets and locations; re-check pores, hands and skin tone after each pass and keep the prompt line "visible pores, no airbrushing".
5. Grade. The post forbids film look on sheets but uses grain and halation on location stills. Not a conflict: neutral on identity assets, film grade only on locations and final video.
6. Clip length. Our Veo 3.1 note says 4 to 8 s. Seedance 2.5 officially supports up to 30 s, so the 14 to 19 s takes fit.
Credit cost per run is not stated in the post; read the Generate button.
